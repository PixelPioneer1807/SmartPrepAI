import os
import faiss
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --- IMPORTANT: Set this to the ID of the user you want to check ---
USER_ID_TO_CHECK = 1 
# --------------------------------------------------------------------

# Path to the specific user's vector store
db_path = f"vector_store/user_{USER_ID_TO_CHECK}/faiss_index"

print(f"🔍 Checking vector store for User ID: {USER_ID_TO_CHECK}")
print(f"📂 Path: {db_path}\n")

if not os.path.exists(db_path):
    print("❌ No vector store found for this user. Have they failed a quiz yet?")
else:
    try:
        # Load the embeddings model (must be the same one used to create the store)
        print("Loading embeddings model...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Load the FAISS index
        print("Loading vector store from disk...")
        vector_store = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        
        print("\n✅ Successfully loaded vector store!")
        print(f"Total entries (mistakes) stored: {vector_store.index.ntotal - 1}") # Subtract 1 for the dummy doc
        
        # To see the actual text content, we can fetch all the documents
        # Note: This is not efficient for very large stores, but perfect for checking.
        retriever = vector_store.as_retriever(search_kwargs={'k': 100}) # Retrieve up to 100 docs
        all_docs = retriever.invoke("all")

        print("\n--- Stored Content ---\n")
        if all_docs:
            for i, doc in enumerate(all_docs):
                # Don't print the dummy document
                if "initial document" not in doc.page_content:
                    print(f"📌 Document {i+1}:")
                    print(doc.page_content)
                    print("-" * 20)
        else:
            print("No content found besides the initial document.")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")