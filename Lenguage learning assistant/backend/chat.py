from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from backend.rag import RAGPipeline  # Import RAGPipeline

class LocalChat:
    def __init__(self, embedding_model_name='paraphrase-multilingual-MiniLM-L12-v2', text_gen_model_name='microsoft/DialoGPT-medium'):
        """Initialize local chat models with context retention and RAG."""
        # Load SentenceTransformer for embeddings
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # Load Hugging Face DialoGPT for text generation
        self.tokenizer = AutoTokenizer.from_pretrained(text_gen_model_name)
        self.text_gen_model = AutoModelForCausalLM.from_pretrained(text_gen_model_name)

        # Initialize RAG Pipeline
        self.rag_pipeline = RAGPipeline()

        # Context retention buffer
        self.chat_history_ids = None

    def embed_text(self, text: str):
        """Generate embedding for input text."""
        return self.embedding_model.encode(text, convert_to_tensor=True)

    def similarity(self, emb1, emb2):
        """Calculate cosine similarity between two embeddings ensuring same device."""
        device = emb1.device
        emb2 = emb2.to(device)
        return util.cos_sim(emb1, emb2).item()

    def add_to_rag(self, text, doc_id):
        """Add a text document to the RAG collection."""
        embedding = self.embed_text(text)
        self.rag_pipeline.add_documents(
            documents=[text],
            metadatas=[{"source": doc_id}],
            ids=[doc_id]
        )

    def query_rag(self, query_text):
        """Query the RAG collection for relevant content."""
        return self.rag_pipeline.query(query_text)

    def generate_response(self, message: str, max_length: int = 1000):
        """Generate a text response using DialoGPT with attention mask."""
        input_ids = self.tokenizer.encode(message + self.tokenizer.eos_token, return_tensors='pt')

        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        attention_mask = input_ids.ne(self.tokenizer.pad_token_id)

        chat_history_ids = self.text_gen_model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=max_length,
            pad_token_id=self.tokenizer.eos_token_id
        )

        response = self.tokenizer.decode(
            chat_history_ids[:, input_ids.shape[-1]:][0],
            skip_special_tokens=True
        )
        return response

    def reset_context(self):
        """Reset the conversation context."""
        self.chat_history_ids = None

if __name__ == "__main__":
    chat = LocalChat()
    print("Start chatting with the AI. Type '/reset' to clear context or '/exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == '/exit':
            break
        elif user_input.lower() == '/reset':
            chat.reset_context()
            print("[Context reset]")
            continue
        response = chat.generate_response(user_input)
        print("Bot:", response)