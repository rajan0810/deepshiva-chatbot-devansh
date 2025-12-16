"""
Cloud Vector Store Manager - Supports Pinecone, Qdrant, and local ChromaDB
"""
from typing import List, Dict, Optional, Tuple
from langchain_core.documents import Document
from config.settings import settings
from src.embeddings.embedding_manager import EmbeddingManager
import logging

logger = logging.getLogger(__name__)


class CloudVectorStore:
    """Unified interface for cloud vector stores."""
    
    def __init__(self, collection_name: str, embedding_manager: Optional[EmbeddingManager] = None):
        self.collection_name = collection_name
        self.embedding_manager = embedding_manager or EmbeddingManager()
        self.store_type = settings.VECTOR_STORE_TYPE
        
        # Pinecone: Use single index with namespaces (free tier = 1 index only)
        if self.store_type == "pinecone":
            self.index_name = "pran-protocol"  # Single index for all collections
            self.namespace = collection_name.replace("_", "-").lower()  # Use as namespace
        else:
            self.index_name = collection_name
            self.namespace = None
        
        # Initialize the appropriate store
        if self.store_type == "pinecone":
            self._init_pinecone()
        elif self.store_type == "qdrant":
            self._init_qdrant()
        elif self.store_type == "chroma":
            self._init_chroma()
        else:
            raise ValueError(f"Unsupported vector store: {self.store_type}")
    
    def _init_pinecone(self):
        """Initialize Pinecone cloud vector store with namespaces."""
        try:
            from pinecone import Pinecone, ServerlessSpec
            
            if not settings.PINECONE_API_KEY:
                raise ValueError("PINECONE_API_KEY not set in .env")
            
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Create ONE index for all collections (free tier limitation)
            if self.index_name not in pc.list_indexes().names():
                pc.create_index(
                    name=self.index_name,
                    dimension=settings.EMBEDDING_DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.PINECONE_ENVIRONMENT or "us-east-1"
                    )
                )
                logger.info(f"✅ Created Pinecone index: {self.index_name}")
            
            self.index = pc.Index(self.index_name)
            logger.info(f"✅ Connected to Pinecone index: {self.index_name}, namespace: {self.namespace}")
            
        except ImportError:
            raise ImportError("Pinecone not installed. Run: pip install pinecone")
    
    def _init_qdrant(self):
        """Initialize Qdrant cloud vector store."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
            
            if not settings.QDRANT_URL or not settings.QDRANT_API_KEY:
                raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in .env")
            
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY
            )
            
            # Create collection if doesn't exist
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created Qdrant collection: {self.collection_name}")
            
            logger.info(f"✅ Connected to Qdrant collection: {self.collection_name}")
            
        except ImportError:
            raise ImportError("Qdrant not installed. Run: pip install qdrant-client")
    
    def _init_chroma(self):
        """Initialize local ChromaDB (fallback)."""
        from src.vector_store.chroma_manager import ChromaDBManager
        self.client = ChromaDBManager(
            collection_name=self.collection_name,
            embedding_manager=self.embedding_manager
        )
        logger.info(f"✅ Using local ChromaDB: {self.collection_name}")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to vector store."""
        if self.store_type == "pinecone":
            return self._add_pinecone(documents)
        elif self.store_type == "qdrant":
            return self._add_qdrant(documents)
        else:
            return self.client.add_documents(documents)
    
    def _add_pinecone(self, documents: List[Document]) -> List[str]:
        """Add documents to Pinecone with namespace support."""
        import uuid
        
        logger.info(f"📊 Embedding {len(documents)} documents...")
        
        # Batch embed all documents at once (much faster!)
        texts = [doc.page_content for doc in documents]
        embeddings = self.embedding_manager.embed_documents(texts, show_progress=True)
        
        ids = []
        vectors = []
        
        for doc, embedding in zip(documents, embeddings):
            doc_id = str(uuid.uuid4())
            
            vectors.append({
                "id": doc_id,
                "values": embedding,
                "metadata": {
                    "text": doc.page_content,
                    **doc.metadata
                }
            })
            ids.append(doc_id)
        
        # Upsert in batches of 100 with namespace
        logger.info(f"☁️ Uploading {len(vectors)} vectors to Pinecone...")
        for i in range(0, len(vectors), 100):
            batch = vectors[i:i+100]
            self.index.upsert(vectors=batch, namespace=self.namespace)
            logger.info(f"   Uploaded {min(i+100, len(vectors))}/{len(vectors)} vectors")
        
        logger.info(f"✅ Added {len(documents)} documents to Pinecone namespace '{self.namespace}'")
        return ids
    
    def _add_qdrant(self, documents: List[Document]) -> List[str]:
        """Add documents to Qdrant."""
        from qdrant_client.models import PointStruct
        import uuid
        
        ids = []
        points = []
        
        for doc in documents:
            doc_id = str(uuid.uuid4())
            embedding = self.embedding_manager.embed_query(doc.page_content)
            
            points.append(PointStruct(
                id=doc_id,
                vector=embedding,
                payload={
                    "text": doc.page_content,
                    **doc.metadata
                }
            ))
            ids.append(doc_id)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logger.info(f"✅ Added {len(documents)} documents to Qdrant")
        return ids
    
    def similarity_search(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Search for similar documents."""
        if self.store_type == "pinecone":
            return self._search_pinecone(query, k)
        elif self.store_type == "qdrant":
            return self._search_qdrant(query, k)
        else:
            return self.client.similarity_search_with_score(query, k=k)
    
    def search(self, query: str, top_k: Optional[int] = None, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar documents (ChromaDB-compatible interface).
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Metadata filters (currently not used for cloud stores)
        
        Returns:
            List of result dictionaries with content, metadata, and similarity
        """
        from config.settings import settings
        k = top_k or settings.TOP_K
        
        results = self.similarity_search(query, k=k)
        
        # Convert to ChromaDB-style format
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity": float(score)
            })
        
        return formatted_results
    
    def _search_pinecone(self, query: str, k: int) -> List[Tuple[Document, float]]:
        """Search Pinecone with namespace support."""
        embedding = self.embedding_manager.embed_query(query)
        
        results = self.index.query(
            vector=embedding,
            top_k=k,
            include_metadata=True,
            namespace=self.namespace
        )
        
        docs = []
        for match in results.matches:
            doc = Document(
                page_content=match.metadata.pop("text"),
                metadata=match.metadata
            )
            docs.append((doc, match.score))
        
        return docs
    
    def _search_qdrant(self, query: str, k: int) -> List[Tuple[Document, float]]:
        """Search Qdrant."""
        embedding = self.embedding_manager.embed_query(query)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            limit=k
        )
        
        docs = []
        for result in results:
            doc = Document(
                page_content=result.payload.pop("text"),
                metadata=result.payload
            )
            docs.append((doc, result.score))
        
        return docs
    
    def count(self) -> int:
        """Get document count."""
        if self.store_type == "pinecone":
            stats = self.index.describe_index_stats()
            # For namespaced index, get count from specific namespace
            if self.namespace and 'namespaces' in stats:
                return stats['namespaces'].get(self.namespace, {}).get('vector_count', 0)
            return stats.total_vector_count
        elif self.store_type == "qdrant":
            info = self.client.get_collection(self.collection_name)
            return info.points_count
        else:
            return self.client.collection.count()
