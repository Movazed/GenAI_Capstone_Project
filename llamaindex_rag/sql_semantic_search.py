import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from llama_index.core import SQLDatabase, Settings
from llama_index.core.objects import ObjectIndex, SQLTableNodeMapping, SQLTableSchema
from llama_index.core.indices.struct_store.sql_query import SQLTableRetrieverQueryEngine
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI

load_dotenv()
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.llm = OpenAI(model="gpt-4o-mini")
def get_sql_analytics_answer(question: str) -> str:
    db_path = "data/telecom_ops.db"
    if not os.path.exists(db_path):
        return "Error: Database not found. Please run init_db.py first"
    engine = create_engine(f"sqlite:///{db_path}")
    sql_database = SQLDatabase(engine)
    table_node_mapping = SQLTableNodeMapping(sql_database)
    table_schema_objs = [
        SQLTableSchema(
            table_name="network_outages", 
            context_str="Contains historical network outage records. Use this to find outage severity, affected customers, incident IDs, and root causes."
        ),
        SQLTableSchema(
            table_name="network_towers", 
            context_str="Contains the physical inventory of cell towers. Use this to find tower locations, technology (4G/5G), and operational status."
        ),
        SQLTableSchema(
            table_name="tower_performance", 
            context_str="Contains live performance metrics. Use this to find latency, packet loss, throughput, and signal strength for specific towers."
        ),
        SQLTableSchema(
            table_name="customer_subscriptions", 
            context_str="Contains customer billing tiers. Use this to describe plans, monthly fees, and account types."
        )
    ]
    obj_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,
    )
    query_engine = SQLTableRetrieverQueryEngine(
        sql_database,
        obj_index.as_retriever(similarity_top_k=1)
    )
    response = query_engine.query(question)
    return str(response)

if __name__ == "__main__":
    print("Testing Semantic SQL...")
    test_q = "Which region had the most CRITICAL network outages recently?"
    print(f"\nQuestion: {test_q}")
    
    answer = get_sql_analytics_answer(test_q)
    print(f"\nAnswer: {answer}")