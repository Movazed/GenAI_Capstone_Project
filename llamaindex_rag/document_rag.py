import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()

Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.llm = OpenAI(model="gpt-4o-mini")

# --- THE FOOLPROOF PATH FIX ---
# This forces Python to always find the root folder, no matter where your terminal is.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PERSIST_DIR = os.path.join(BASE_DIR, "data", "vector_index")
DOCS_DIR = os.path.join(BASE_DIR, "data", "documents")


def get_policy_answer(question: str) -> str:
    # Double-check the documents directory actually exists to prevent crashes
    if not os.path.exists(DOCS_DIR):
        return f"System Error: Cannot find documents folder at {DOCS_DIR}"

    if not os.path.exists(PERSIST_DIR):
        print("Vector Index not found, reading documents and creating vector index...")
        documents = SimpleDirectoryReader(DOCS_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print("Index saved successfully")
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)
    
    query_engine = index.as_query_engine()
    response = query_engine.query(question)

    return str(response)

if __name__ == "__main__":
    print("Testing Policy RAG...")
    test_q = "What is the roaming policy for Western Europe?"
    answer = get_policy_answer(test_q)
    print(f"\nQuestion: {test_q}")
    print(f"\nAnswer: {answer}")