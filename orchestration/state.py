from typing import TypedDict, Optional

class TelecomState(TypedDict):
    customer_message: str          
    route_decision: Optional[str]  
    raw_worker_data: Optional[str] 
    final_email: Optional[str]     