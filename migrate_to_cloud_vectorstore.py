"""
Migrate local ChromaDB data to cloud vector store (Pinecone or Qdrant)
"""
import asyncio
from src.vector_store.chroma_manager import ChromaDBManager
from src.vector_store.cloud_vector_store import CloudVectorStore
from src.embeddings.embedding_manager import EmbeddingManager
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_collection(collection_name: str):
    """Migrate a single collection from ChromaDB to cloud."""
    logger.info(f"📦 Migrating collection: {collection_name}")
    
    # Initialize managers
    embedding_manager = EmbeddingManager()
    
    # Source: Local ChromaDB
    source = ChromaDBManager(
        collection_name=collection_name,
        embedding_manager=embedding_manager
    )
    
    # Destination: Cloud vector store
    destination = CloudVectorStore(
        collection_name=collection_name,
        embedding_manager=embedding_manager
    )
    
    # Get all documents from ChromaDB
    logger.info("📥 Fetching documents from local ChromaDB...")
    collection_data = source.collection.get(include=["documents", "metadatas"])
    
    if not collection_data or not collection_data["documents"]:
        logger.warning(f"⚠️ No documents found in collection: {collection_name}")
        return
    
    # Convert to Document objects
    from langchain_core.documents import Document
    documents = []
    for i, doc_text in enumerate(collection_data["documents"]):
        metadata = collection_data["metadatas"][i] if collection_data["metadatas"] else {}
        documents.append(Document(page_content=doc_text, metadata=metadata))
    
    logger.info(f"📤 Uploading {len(documents)} documents to {settings.VECTOR_STORE_TYPE}...")
    
    # Upload to cloud in batches
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        destination.add_documents(batch)
        logger.info(f"  ✓ Uploaded batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
    
    logger.info(f"✅ Migration complete: {collection_name}")
    logger.info(f"   Total documents: {len(documents)}")


async def main():
    """Migrate all collections."""
    if settings.VECTOR_STORE_TYPE == "chroma":
        logger.error("❌ VECTOR_STORE_TYPE is set to 'chroma' (local)")
        logger.error("   Change it to 'pinecone' or 'qdrant' in your .env file")
        return
    
    logger.info("=" * 60)
    logger.info(f"🚀 Starting migration to {settings.VECTOR_STORE_TYPE.upper()}")
    logger.info("=" * 60)
    
    # List of collections to migrate
    collections = [
        "yoga_collection",
        "ayush_collection",
        "mental_wellness_collection",
        "symptoms_collection",
        "schemes_collection",
        "documents"  # general collection
    ]
    
    for collection_name in collections:
        try:
            await migrate_collection(collection_name)
            print()
        except Exception as e:
            logger.error(f"❌ Failed to migrate {collection_name}: {e}")
            continue
    
    logger.info("=" * 60)
    logger.info("✅ Migration complete!")
    logger.info("=" * 60)
    logger.info(f"\n🎉 Your data is now in {settings.VECTOR_STORE_TYPE.upper()}!")
    logger.info(f"\n✅ The RAG workflow will automatically use {settings.VECTOR_STORE_TYPE.upper()} from now on.")
    logger.info("\nNext steps:")
    logger.info("1. Run: python verify_vectorstore.py (to test)")
    logger.info("2. Start API: python api_mongodb.py")
    logger.info("3. Optional: Delete data/chroma_db to free up space")


if __name__ == "__main__":
    asyncio.run(main())
