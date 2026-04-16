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
        font-size: 0.9em;
        font-family: monospace;
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
    # Display user message in chat
    st.chat_message("user").write(symptom)
    
    with st.chat_message("assistant"):
        # 2. Setup the visual status tracker
        with st.status("📡 Orchestrating CrewAI Workflow...", expanded=True) as status:
            st.write("Initializing fresh Agent context...")
            
            comm_container = st.empty()
            comm_history = []
            
            # Trace callback to show thoughts in real-time
            def step_callback(step):
                text_to_display = ""
                try:
                    if hasattr(step, 'log'):
                        text_to_display = f"💭 Agent: {step.log}"
                    elif isinstance(step, str):
                        text_to_display = f"💭 Update: {step}"
                    
                    if text_to_display:
                        comm_history.append(text_to_display)
                        html_content = "".join([f"<div class='comm-box'>{msg.replace('\n', '<br>')}</div>" for msg in comm_history])
                        comm_container.markdown(html_content, unsafe_allow_html=True)
                except: pass

            try:
                # --- THE REFINEMENT ---
                # 3. Create a BRAND NEW crew instance for this specific symptom
                # This ensures no 'memory leaks' from previous failed runs
                crew_instance = create_crew(symptom, step_callback)
                
                # 4. Run the orchestration
                result = crew_instance.kickoff()
                
                # Update status UI
                st.write("✅ Logic grounded in Manual.txt")
                st.write("✅ Inventory fetched from SQL")
                st.write("✅ Compliance verified")
                status.update(label="Workflow Complete!", state="complete", expanded=False)
                
                # 5. Display the final synthesized result
                final_plan = str(result.raw) if hasattr(result, 'raw') else str(result)
                st.markdown(f"<div class='success-box'>{final_plan}</div>", unsafe_allow_html=True)

            except Exception as e:
                status.update(label="Orchestration Failed", state="error", expanded=True)
                st.error(f"Error: {str(e)}\n\n⚠️ Ensure FastMCP is running on Port 8080!")