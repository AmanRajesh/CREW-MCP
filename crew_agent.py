from crewai import Agent, Task, Crew, Process
import os
from dotenv import load_dotenv
from tools import MCPSearchManualTool, MCPCheckInventoryTool

load_dotenv()

# We define the model name as a string for the agents to bypass Pydantic ValidationError
llm_model = "groq/llama-3.3-70b-versatile"

diagnostic_agent = Agent(
    role="Diagnostic_Researcher",
    goal="Extract the SKU and Safety info from the technical manual for a given symptom.",
    backstory=(
        "You are a Philips Technical Support Specialist. "
        "When a user reports a symptom, your ABSOLUTE FIRST STEP is to call the 'search_technical_manual' tool."
    ),
    tools=[MCPSearchManualTool()],
    llm=llm_model, 
    verbose=True,
    allow_delegation=False
)

logistics_agent = Agent(
    role="Logistics_Coordinator",
    goal="Fetch stock level and unit cost for an exact SKU.",
    backstory=(
        "You are a Logistics Expert at Philips. Given a Part Number (SKU), "
        "you use the 'check_hospital_inventory' tool."
    ),
    tools=[MCPCheckInventoryTool()],
    llm=llm_model, 
    verbose=True,
    allow_delegation=False
)

compliance_agent = Agent(
    role="Tier_2_Compliance",
    goal="Determine Authorization constraints based strictly on unit cost.",
    backstory=(
        "You are the Tier 2 Compliance Auditor. Given part cost data, "
        "check if the unit cost exceeds the $500 threshold."
    ),
    llm=llm_model, 
    verbose=True,
    allow_delegation=False
)

def create_crew(symptom: str, step_callback=None):
    # Pass the step callback to each agent
    diagnostic_agent.step_callback = step_callback
    logistics_agent.step_callback = step_callback
    compliance_agent.step_callback = step_callback

    diagnostic_task = Task(
        description=f"Find the SKU and Safety information for the following symptom: '{symptom}'.",
        expected_output="A summary containing the SKU and the safety precautions.",
        agent=diagnostic_agent
    )

    logistics_task = Task(
        description=(
            "Using the SKU identified, find its stock level and unit cost. "
            "Do not use XML tags or special function syntax in your thought process."
        ),
        expected_output="The stock level and exact unit cost.",
        agent=logistics_agent
    )

    reporting_task = Task(
        description=(
            "Synthesize EVERYTHING into a complete Repair Action Plan. "
            "Determine if authorization is required (threshold is $500)."
        ),
        expected_output="A complete structured Repair Action Plan.",
        agent=compliance_agent
    )

    crew = Crew(
        agents=[diagnostic_agent, logistics_agent, compliance_agent],
        tasks=[diagnostic_task, logistics_task, reporting_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew