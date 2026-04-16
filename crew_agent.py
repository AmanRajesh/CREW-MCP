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
        "When a user reports a symptom, your ABSOLUTE FIRST STEP is to call the 'search_technical_manual' tool. "
        "DO NOT guess the SKU. You must extract it from the tool's output."
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
        "you MUST call the 'check_hospital_inventory' tool. "
        "DO NOT hallucinate or assume stock levels or costs. You MUST wait to get the real numbers from the tool."
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
        "check if the unit cost exceeds the $500 threshold. "
        "Make sure to extract and display the EXACT numerical cost and stock level provided by the Logistics Coordinator."
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
        description=(
            f"Find the SKU and Safety information for the following symptom: '{symptom}'.\n"
            "CRITICAL API INSTRUCTION: When calling tools, you MUST correctly format the function invocation. "
            "You MUST include the closing bracket `>` after the function name before the JSON payload! "
            "Example Correct: `<function=search_technical_manual>{\"symptom_or_error\": \"value\"}</function>`\n"
            "Example INCORRECT: `<function=search_technical_manual{\"symptom_or_error\": \"value\"}</function>`"
        ),
        expected_output="A summary containing the SKU and the safety precautions.",
        agent=diagnostic_agent
    )

    logistics_task = Task(
        description=(
            "Using the exact SKU identified by the diagnostic agent, find its stock level and unit cost. "
            "STRICT REQUIREMENT: You MUST successfully call the `check_hospital_inventory` tool with the SKU, wait for the response, and output the exact Stock Level and Unit Cost values returned. DO NOT simply output what you plan to do.\n"
            "CRITICAL API INSTRUCTION: When calling tools, you MUST correctly format the function invocation. "
            "You MUST include the closing bracket `>` after the function name before the JSON payload! "
            "Example Correct: `<function=check_hospital_inventory>{\"part_number\": \"value\"}</function>`\n"
            "Example INCORRECT: `<function=check_hospital_inventory{\"part_number\": \"value\"}</function>`"
        ),
        expected_output="The actual stock level and exact numerical unit cost from the database.",
        agent=logistics_agent
    )

    reporting_task = Task(
        description=(
            "Synthesize EVERYTHING into a complete Repair Action Plan. "
            "Ensure you state the ACTUAL unit cost and stock numbers retrieved. "
            "Determine if authorization is required (threshold is $500)."
        ),
        expected_output="A complete structured Repair Action Plan containing actual data, not generic placeholders.",
        agent=compliance_agent
    )

    crew = Crew(
        agents=[diagnostic_agent, logistics_agent, compliance_agent],
        tasks=[diagnostic_task, logistics_task, reporting_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew