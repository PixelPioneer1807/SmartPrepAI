import os
import streamlit as st
from typing import List, Dict

# LangChain components for RAG
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings

# Define the path for the persistent vector store
VECTOR_STORE_PATH = "vector_store"

class VectorDBManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = self._load_vector_store()

    def _get_user_db_path(self) -> str:
        """Get the database path specific to the logged-in user."""
        if 'user' not in st.session_state or not st.session_state.user:
            return None
        user_id = st.session_state.user['id']
        user_db_dir = os.path.join(VECTOR_STORE_PATH, f"user_{user_id}")
        os.makedirs(user_db_dir, exist_ok=True)
        return os.path.join(user_db_dir, "faiss_index")

    def _load_vector_store(self) -> FAISS:
        """Loads the vector store from disk if it exists, otherwise creates a new one."""
        db_path = self._get_user_db_path()
        if db_path and os.path.exists(db_path):
            try:
                return FAISS.load_local(db_path, self.embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                print(f"Error loading vector store: {e}. Creating a new one.")
        
        dummy_text = "initial document"
        return FAISS.from_texts([dummy_text], self.embeddings)

    def add_quiz_results_to_db(self, results: List[Dict], topic: str):
        """Formats quiz results and adds them to the vector database."""
        if not results:
            return

        documents = []
        for result in results:
            if not result['is_correct']:
                content = (
                    f"Question on {topic}: {result['question']}\n"
                    f"My incorrect answer: {result['user_answer']}\n"
                    f"The correct answer: {result['correct_answer']}\n"
                    f"Explanation: {result['explanation']}"
                )
                metadata = {
                    "topic": topic,
                    "difficulty": st.session_state.get('current_difficulty', 'Unknown'),
                    "question_type": result['question_type']
                }
                documents.append(Document(page_content=content, metadata=metadata))
        
        if documents:
            self.vector_store.add_documents(documents)
            self._save_vector_store()
            st.toast(f"Saved {len(documents)} weak points to your personalized prep material!", icon="🧠")

    def _save_vector_store(self):
        """Saves the vector store to disk."""
        db_path = self._get_user_db_path()
        if db_path:
            self.vector_store.save_local(db_path)

    def retrieve_relevant_documents(self, topic: str, k: int = 3) -> List[Document]:
        """Retrieves k most relevant documents for a given topic."""
        if not self.vector_store:
            return []
        # Use similarity search to find the most relevant past mistakes
        retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
        return retriever.invoke(f"Questions and explanations about {topic}")
    
    def has_enough_context(self) -> bool:
        """Checks if the vector store has more than just the initial dummy document."""
        if not self.vector_store:
            return False
        # The index has 1 doc on creation, so > 1 means user data exists.
        return self.vector_store.index.ntotal > 1