from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import MCPSearchManualTool, MCPCheckInventoryTool
import os

# Set up Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

diagnostic_agent = Agent(
    role="Diagnostic_Researcher",
    goal="Extract the SKU and Safety info from the technical manual for a given symptom.",
    backstory="You are a Philips Technical Support Specialist. "
        "When a user reports a symptom, your ABSOLUTE FIRST STEP is to call the 'search_technical_manual' tool. "
        "Do not ask the user for details that are likely in the manual. "
        "Extract the SKU and Safety info yourself and pass it to the next agent.",
    tools=[MCPSearchManualTool()],
    llm=llm,
    verbose=True
)

logistics_agent = Agent(
    role="Logistics_Coordinator",
    goal="Fetch stock level and unit cost for an exact SKU.",
    backstory="You are a Logistics Expert at Philips. Given a Part Number (SKU), you use the 'check_hospital_inventory' tool to fetch the stock level and unit cost. Return the exact cost data.",
    tools=[MCPCheckInventoryTool()],
    llm=llm,
    verbose=True
)

compliance_agent = Agent(
    role="Tier_2_Compliance",
    goal="Determine Authorization constraints based strictly on unit cost.",
    backstory="You are the Tier 2 Compliance Auditor. Given part cost data, check if the unit cost exceeds the $500 threshold. If it does, mandate AUTHORIZATION REQUIRED. Otherwise, AUTHORIZATION NOT REQUIRED.",
    llm=llm,
    verbose=True
)

def create_crew(symptom: str, step_callback=None):
    # Pass the step callback to each agent
    diagnostic_agent.step_callback = step_callback
    logistics_agent.step_callback = step_callback
    compliance_agent.step_callback = step_callback

    diagnostic_task = Task(
        description=f"Find the SKU and Safety information for the following symptom: '{symptom}'. Make sure to extract the exact SKU string.",
        expected_output="A summary containing the SKU and the safety precautions related to the symptom.",
        agent=diagnostic_agent
    )

    logistics_task = Task(
        description="Using the SKU identified by the diagnostic researcher, find its stock level and unit cost.",
        expected_output="The stock level and exact unit cost of the identified SKU.",
        agent=logistics_agent
    )

    reporting_task = Task(
        description="""
        Using the unit cost identified from logistics, determine if authorization is required (threshold is $500).
        Finally, synthesize EVERYTHING into a complete Repair Action Plan for the field engineer formatting as a clear report.
        Summarize the diagnosis, exact SKU, cost, compliance status, AND explicitly list all safety precautions gathered initially.
        """,
        expected_output="A complete structured Repair Action Plan containing Diagnosis, SKU, Cost, Compliance Status, and Safety Precautions.",
        agent=compliance_agent
    )

    crew = Crew(
        agents=[diagnostic_agent, logistics_agent, compliance_agent],
        tasks=[diagnostic_task, logistics_task, reporting_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew
