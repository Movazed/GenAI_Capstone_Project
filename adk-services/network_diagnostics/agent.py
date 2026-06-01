import os
import sqlite3
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

DB_PATH = "data/telecom_ops.db"

def run_sql(query: str, params: tuple = ()):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        return f"Database error: {str(e)}"

def check_tower_status(tower_id: str) -> str:
    query = """
        SELECT t.tower_id, t.region, t.technology, t.status, i.severity, i.description, i.status as incident_status
        FROM network_towers t
        LEFT JOIN open_incidents i ON t.tower_id = i.tower_id
        WHERE t.tower_id = ?
    """
    results = run_sql(query, (tower_id,))
    if isinstance(results, str) and "error" in results.lower():
        return results
    if not results:
        return f"Tower {tower_id} not found."
    return str(results)

def run_connectivity_diagnostics(tower_id: str, symptom: str) -> str:
    query = """
        SELECT avg_latency_ms, packet_loss_pct, throughput_mbps, signal_strength_dbm
        FROM tower_performance
        WHERE tower_id = ?
        ORDER BY recorded_at DESC LIMIT 1
    """
    results = run_sql(query, (tower_id,))
    
    if isinstance(results, str) and "error" in results.lower():
        return results
        
    if not results:
        return f"No performance data found for {tower_id}."
    
    perf = results[0]
    if perf['packet_loss_pct'] > 2.0 or (perf['signal_strength_dbm'] is not None and perf['signal_strength_dbm'] < -100):
        return f"Diagnostics run for {symptom}: High packet loss ({perf['packet_loss_pct']}%) or weak signal ({perf['signal_strength_dbm']} dBm) detected. Recommendation: Dispatch field technician to check antenna alignment."
    else:
        return f"Diagnostics run for {symptom}: Metrics look nominal (Latency {perf['avg_latency_ms']}ms). Issue may be user device related."

def get_regional_network_summary(region: str) -> str:
    query = """
        SELECT status, COUNT(*) as count
        FROM network_towers
        WHERE region = ?
        GROUP BY status
    """
    results = run_sql(query, (region,))
    if isinstance(results, str) and "error" in results.lower():
        return results
    if not results:
        return f"No network data found for region: {region}."
    return str(results)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""You are a NOC (Network Operations Center) specialist. 
    Your job is to diagnose network connectivity issues, check tower statuses, 
    and provide regional network summaries. Always use your tools to query the 
    live SQLite database. Never guess or make up data.""",
    tools=[check_tower_status, run_connectivity_diagnostics, get_regional_network_summary]
)

app = FastAPI()

@app.post("/chat")
def chat_api(payload: dict):
    prompt = payload["messages"][0]["content"]
    try:
        chat = model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(prompt)
        return {"result": response.text}
    except Exception as e:
        return {"result": f"Model Error: {str(e)}"}

if __name__ == "__main__":
    print("Starting Network Diagnostics FastAPI Service on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)