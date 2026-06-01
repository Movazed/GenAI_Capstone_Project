import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI


load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

def generate_customer_response(user_query: str, agent_context: str) -> str:
    communications_specialist = Agent(
        role="Customer Communications Specialist",
        goal="Draft a clear, empathetic, and professional response to the customer.",
        backstory="You work for Prodapt, a telecom company. You excel at taking raw technical data and policy rules and turning them into friendly, easy-to-understand customer emails.",
        verbose=False,
        allow_delegation=False,
        llm=llm
    )

    quality_reviewer = Agent(
        role="Quality Assurance Reviewer",
        goal="Review the drafted response for accuracy, tone, and compliance, outputting only the final text.",
        backstory="You are a strict QA reviewer at Prodapt. You ensure that customer communications do not promise things outside of policy, maintain a professional tone, and directly answer the customer's original query. You never output internal notes, only the final customer-facing text.",
        verbose=False,
        allow_delegation=False,
        llm=llm
    )

    draft_task = Task(
        description=f"""
        Original Customer Query: "{user_query}"
        Raw System Context: "{agent_context}"
        
        Task: Write a response to the customer addressing their query. Use ONLY the information provided in the Raw System Context. 
        Do not make up any policies, data, or credits. Be polite and helpful.
        """,
        expected_output="A drafted email or message to the customer.",
        agent=communications_specialist
    )

    review_task = Task(
        description="""
        Review the drafted response. 
        Ensure it accurately reflects the raw system context and maintains a professional tone.
        Fix any typos.
        Output ONLY the final, polished text that will be sent directly to the customer. 
        Do not include introductory phrases like "Here is the final text:" or "Dear Customer" if it doesn't fit a chat interface.
        """,
        expected_output="The final, polished text ready to be sent to the customer.",
        agent=quality_reviewer
    )

    comms_crew = Crew(
        agents=[communications_specialist, quality_reviewer],
        tasks=[draft_task, review_task],
        process=Process.sequential, 
        verbose=False
    )

    result = comms_crew.kickoff()
    return str(result)


if __name__ == "__main__":
    print("Testing CrewAI Communications Crew...")
    test_query = "We had a 6-hour outage in the Midwest. Am I eligible for an SLA credit and what does policy say?"
    test_context = """
    NetworkAnalytics Worker: The Midwest region experienced a 6-hour CRITICAL outage today. 
    PolicyRAG Worker: According to the SLA policy, Business plans get credit after 4 hours of downtime, Consumer plans get credit after 8 hours of downtime.
    """
    
    print("\nSending raw data to the CrewAI team. Please wait...\n")
    final_output = generate_customer_response(test_query, test_context)
    
    print("--- final customer response ---")
    print(final_output)