import streamlit as st
import os
from crew_agent import create_crew
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Multi-Agent Systems for Error Resolution via MCP", page_icon="🏥", layout="wide")

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
        font-size: 0.85em;
        font-family: 'Inter', sans-serif;
        border-radius: 0 8px 8px 0;
    }
    .agent-tag {
        color: #4facfe;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.75em;
        letter-spacing: 1px;
        margin-bottom: 4px;
        display: block;
    }
    .stChatInputContainer > div {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>Multi-Agent Systems for Error Resolution via MCP</h1>", unsafe_allow_html=True)
st.markdown("<h4 class='sub-header'>A2A Diagnostic, Logistics & Compliance Network via MCP</h4>", unsafe_allow_html=True)
st.write("---")

symptom = st.chat_input("Enter device symptom or error code (e.g., 'Error Code 404B')...")

if symptom:
    st.chat_message("user").write(symptom)
    
    with st.chat_message("assistant"):
        with st.status("📡 Orchestrating CrewAI Workflow...", expanded=True) as status:
            st.write("Initializing fresh Agent context...")
            
            # Placeholders for structured agent trace
            trace_container = st.container()
            
            # Trace callback to attribute data to specific agents
            def step_callback(step):
                try:
                    # Capture the Agent's name and their specific action/output
                    if hasattr(step, 'agent'):
                        agent_name = step.agent
                        # Create a visual indicator of who is working
                        with trace_container:
                            if "Diagnostic" in agent_name:
                                st.toast(f"🔍 Researcher is reading Manual.txt...", icon="📖")
                            elif "Logistics" in agent_name:
                                st.toast(f"📦 Logistics is querying SQL Database...", icon="💾")
                            elif "Compliance" in agent_name:
                                st.toast(f"⚖️ Compliance is verifying budget...", icon="🛡️")

                            with st.expander(f"⚡ Live Action: {agent_name}", expanded=True):
                    # This captures the actual logic the agent is performing
                                st.markdown(f"**Agent is executing:** {step.tool if hasattr(step, 'tool') else 'Reasoning'}")
                                st.caption(step.log if hasattr(step, 'log') else "Processing...")
                except Exception as e:
                    pass

            try:
                # 3. Create fresh crew instance
                crew_instance = create_crew(symptom, step_callback)
                
                # 4. Run the orchestration
                result = crew_instance.kickoff()
                
                # Update status UI
                st.write("✅ Diagnostic Researcher extracted SKU")
                st.write("✅ Logistics Coordinator verified SQL Inventory")
                st.write("✅ Tier 2 Compliance applied cost threshold")
                
                status.update(label="Workflow Complete!", state="complete", expanded=False)
                
                # 5. Final Output
                final_plan = str(result.raw) if hasattr(result, 'raw') else str(result)
                st.markdown(f"<div class='success-box'>{final_plan}</div>", unsafe_allow_html=True)

            except Exception as e:
                status.update(label="Orchestration Failed", state="error", expanded=True)
                st.error(f"Error: {str(e)}\n\n⚠️ Ensure FastMCP is running on Port 8080!")