import chromadb
import tempfile

class RAGPipeline:
    def __init__(self, collection_name="german-listening-comprehension"):
        # Use a temporary directory for ChromaDB persistence
        temp_dir = tempfile.mkdtemp()

        # Updated Chroma client initialization
        self.client = chromadb.PersistentClient(path=temp_dir)

        # Try to create or get the collection
        try:
            self.collection = self.client.get_collection(collection_name)
        except Exception as e:
            print(f"Collection not found, creating a new one: {e}")
            self.collection = self.client.create_collection(collection_name)

    def add_documents(self, documents, metadatas, ids):
        """Add documents to ChromaDB collection."""
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def query(self, query_text, n_results=2):
        """Query the collection for the most relevant documents."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results