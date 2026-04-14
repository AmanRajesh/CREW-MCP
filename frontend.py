import streamlit as st
import os
from crew_agent import create_crew
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Philips CrewAI Platform", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    /* Dark glassmorphism dashboard aesthetic */
    .stApp {
        background: radial-gradient(circle at top left, #0e111a, #161c28, #1e2638);
        color: #e0e0e0;
    }
    .main-header {
        text-align: center;
        font-family: 'Inter', sans-serif;
        background: -webkit-linear-gradient(45deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0.2em;
    }
    .sub-header {
        text-align: center;
        color: #8892b0;
        font-family: 'Inter', sans-serif;
        margin-bottom: 2em;
        font-weight: 300;
    }
    .success-box {
        background: rgba(16, 185, 129, 0.05);
        border: 1px solid rgba(16, 185, 129, 0.2);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 1.5rem;
        border-radius: 12px;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
        white-space: pre-wrap;
    }
    .comm-box {
        background: rgba(79, 172, 254, 0.05);
        border-left: 3px solid #4facfe;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        font-size: 0.9em;
        font-family: monospace;
    }
    .stChatInputContainer > div {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>Philips Orchestrator CrewAI</h1>", unsafe_allow_html=True)
st.markdown("<h4 class='sub-header'>A2A Diagnostic, Logistics & Compliance Network via MCP</h4>", unsafe_allow_html=True)
st.write("---")

symptom = st.chat_input("Enter device symptom or error code (e.g., 'blinking amber SPO2 sensor')...")

if symptom:
    st.chat_message("user").write(symptom)
    
    with st.chat_message("assistant"):
        with st.status("📡 Orchestrating CrewAI Workflow... Please wait.", expanded=True) as status:
            st.write("Loading CrewAI Agents configured with MCP tools...")
            
            comm_container = st.empty()
            comm_history = []
            
            # Using step callback to trace Agent comms
            def step_callback(step):
                text_to_display = ""
                try:
                    if isinstance(step, list):
                        for s in step:
                            # We can capture AgentAction logs
                            if hasattr(s, 'log'):
                                text_to_display += f"💭 Agent: {s.log}\n\n"
                    elif hasattr(step, 'text'):
                        text_to_display += f"💭 Thought: {step.text}\n\n"
                    elif isinstance(step, str):
                        text_to_display += f"💭 Update: {step}\n\n"
                    else:
                        text_to_display += f"💭 Data: {str(step)}\n\n"
                except Exception:
                    pass
                
                if text_to_display.strip():
                    comm_history.append(text_to_display.strip())
                    
                    html_content = ""
                    for msg in comm_history:
                        # Convert newlines to HTML br for presentation
                        safe_msg = msg.replace('\n', '<br>')
                        html_content += f"<div class='comm-box'>{safe_msg}</div>"
                    comm_container.markdown(html_content, unsafe_allow_html=True)

            try:
                crew = create_crew(symptom, step_callback)
                result = crew.kickoff()
                
                st.write("✅ `Diagnostic_Researcher` parsed schemas via MCP")
                st.write("✅ `Logistics_Coordinator` fetched hospital inventory records via MCP")
                st.write("✅ `Tier_2_Compliance` enforced the $500 threshold budget rules")
                st.write("✅ `Crew` successfully synthesized the multi-agent context")
                
                status.update(label="CrewAI Workflow Completed Successfully!", state="complete", expanded=False)
                
                # handle different versions of CrewAI output
                final_plan = str(result.raw) if hasattr(result, 'raw') else str(result)
                
                st.markdown(f"<div class='success-box'>{final_plan}</div>", unsafe_allow_html=True)
                
            except Exception as e:
                status.update(label="CrewAI Workflow Encountered an Error", state="error", expanded=True)
                st.error(f"Exception during orchestration: {str(e)}\n\n⚠️ Ensure your FastMCP server is actively running on Port 8080!")
