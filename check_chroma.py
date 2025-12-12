"""Quick script to check ChromaDB collections"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from pathlib import Path

# Connect to ChromaDB
client = chromadb.PersistentClient(
    path=str(Path("data/chroma_db")),
    settings=ChromaSettings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# List all collections
print("=" * 60)
print("CHROMADB COLLECTIONS")
print("=" * 60)

collections = client.list_collections()
print(f"\nFound {len(collections)} collections:\n")

for collection in collections:
    count = collection.count()
    print(f"📦 {collection.name}: {count} documents")

print("\n" + "=" * 60)
