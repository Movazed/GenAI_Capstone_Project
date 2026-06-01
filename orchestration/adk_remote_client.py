import requests

def ask_network_agent(prompt: str) -> str:
    try:
        url = "http://localhost:8001/chat"
        payload = {"messages": [{"role": "user", "content": prompt}]}
        response = requests.post(url, json=payload, timeout=30)
        return str(response.json().get("result", response.text))
    except Exception as e:
        return f"Network Agent Error: {str(e)}"

def ask_billing_agent(prompt: str) -> str:
    try:
        url = "http://localhost:8002/chat"
        payload = {"messages": [{"role": "user", "content": prompt}]}
        response = requests.post(url, json=payload, timeout=30)
        return str(response.json().get("result", response.text))
    except Exception as e:
        return f"Billing Agent Error: {str(e)}"