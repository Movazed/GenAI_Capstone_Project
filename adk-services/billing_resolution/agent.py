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

def lookup_billing_account(customer_id: str) -> str:
    """Retrieves the current balance and recent charges for a customer."""
    query = """
        SELECT a.current_balance, c.charge_id, c.description, c.amount, c.charge_date, c.is_duplicate_flag
        FROM billing_accounts a
        LEFT JOIN billing_charges c ON a.customer_id = c.customer_id
        WHERE a.customer_id = ?
        ORDER BY c.charge_date DESC LIMIT 5
    """
    results = run_sql(query, (customer_id,))
    if not results:
        return f"Account for {customer_id} not found."
    return str(results)

def check_duplicate_charges(customer_id: str) -> str:
    """Finds any charges explicitly flagged as duplicates in the database."""
    query = """
        SELECT * FROM billing_charges
        WHERE customer_id = ? AND is_duplicate_flag = 1
    """
    results = run_sql(query, (customer_id,))
    if not results:
        return f"No duplicate charges found for {customer_id}."
    return str(results)

def apply_billing_credit(customer_id: str, amount: float, reason: str) -> str:
    """Applies a credit to the account. Over $100 requires manual approval."""
    # <-- CHANGED: Raised the approval limit from 50 to 100
    status = 'PENDING_APPROVAL' if amount > 100 else 'APPLIED'
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO billing_credits (customer_id, amount, reason, status, applied_at) VALUES (?, ?, ?, ?, datetime('now'))", 
                (customer_id, amount, reason, status)
            )
            
            if status == 'APPLIED':
                cursor.execute(
                    "UPDATE billing_accounts SET current_balance = current_balance - ? WHERE customer_id = ?", 
                    (amount, customer_id)
                )
            conn.commit()
            return f"Credit of ${amount} for {customer_id} processed. Status: {status}."
    except Exception as e:
        return f"Failed to apply credit: {str(e)}"

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="""You are a Billing Resolution Specialist.
    Your job is to investigate customer accounts, find duplicate charges, and apply credits.
    Always use your tools to query the live SQLite database. Never guess customer balances.
    If a customer asks for a credit, check their account first.""",
    tools=[lookup_billing_account, check_duplicate_charges, apply_billing_credit]
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
    print("Starting Billing Resolution FastAPI Service on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)