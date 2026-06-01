# 📡 Prodapt Telecom AI Assistant (Capstone Project)

Welcome to the Prodapt Telecom Multi-Agent System! 

This project is a fully autonomous AI customer support center. Instead of being a standard "chatbot" that just guesses answers, this system acts like a real company. It has different AI "departments" that talk to each other, look up real customer data, strictly follow company financial rules, and write professional emails to resolve issues.

## 🧠 How It Works (The Departments)

Think of this app as a digital office building. When a customer asks a question, here is what happens:

1. **The Front Desk (LangGraph):** Reads the customer's message and decides which department needs to handle it.
2. **The IT Department (Network Agent):** If the customer has bad 5G service, this agent looks into the live database to check tower health, packet loss, and signal strength.
3. **The Finance Department (Billing Agent):** If the customer has a bill issue, this agent checks their account. It can issue refunds, but it is programmed with strict rules (e.g., any refund over $50 requires manager approval).
4. **The Policy Team (RAG/LlamaIndex):** If the customer asks about policies, this team reads the company's official text documents (like the SLA Policy or 5G FAQ) to find the answer.
5. **The PR Representative (CrewAI):** Once the departments find the raw data, this agent takes those numbers and writes a highly empathetic, professional email back to the customer.

---

## 🚀 How to Run the App (Step-by-Step)

To run this system, you need to open three separate terminal windows. Think of this as turning on the lights in three different offices so the AI workers can do their jobs.

### Step 1: Preparation
1. Ensure you have **Python** installed on your computer.
2. Ensure you have a file named exactly `.env` in the main project folder. Inside that file, paste your Google API key like this:
   ```text
   GOOGLE_API_KEY=your_actual_api_key_here
Open a terminal, ensure your virtual environment (venv) is activated, and build the fresh database by running:

Bash
python build_official_db.py
Step 2: Wake up the IT Department
Open your first terminal window, activate your virtual environment, and run:

Bash
python adk-services/network_diagnostics/agent.py
(Leave this window open and running. It will say it is listening on Port 8001).

Step 3: Wake up the Finance Department
Open a second terminal window, activate your virtual environment, and run:

Bash
python adk-services/billing_resolution/agent.py
(Leave this window open and running. It will say it is listening on Port 8002).

Step 4: Open the Customer Chat Window
Open a third terminal window, activate your virtual environment, and run:

Bash
streamlit run ui/app.py
(This will automatically open a beautiful chat website in your web browser).

🧪 Try It Out! (Test Prompts)
Once the website opens in your browser, copy and paste these exact sentences into the chat box to watch the AI do its job:

1. Test the IT Department: > "My connection is dropping. Can you check tower TWR-104?"

What happens: The AI finds a broken tower in the database and dispatches a technician.

2. Test the Finance Department: > "I noticed a duplicate charge of $65.99 on account CUST-10002. Please investigate and apply a credit immediately." * What happens: The AI finds the error and applies a credit, but automatically flags it for "Manager Approval" because the company rule limits instant refunds to $50.

3. Test the Policy Team: > "What is your SLA policy for network outages, and how do I get a refund?"

What happens: The AI reads the company policy documents and explains the rules clearly.