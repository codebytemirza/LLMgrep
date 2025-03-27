import os
import atexit
import streamlit as st
from dotenv import load_dotenv

from .scanner_tab import render_scanner_tab
from .chat_tab import render_chat_tab
from .rules_tab import render_rules_tab
from ..core.file_utils import cleanup_temp_files

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    default_states = {
        'chat_history': [],
        'code_content': "",
        'analysis_results': None,
        'llm_analysis': "",
        'current_file': None
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(page_title="SecureCode - Enhanced Security Scanner", layout="wide")
    st.title("🛡️ SecureCode - Enhanced Security Scanner")
    st.markdown("Combining Semgrep and LLM for intelligent security analysis")

def render_sidebar():
    """Render application sidebar with settings."""
    with st.sidebar:
        st.title("⚙️ Scan Settings")

        # Add cleanup button to sidebar
        if st.button("🗑️ Cleanup Temp Files", key="cleanup_button"):
            try:
                # Clean up temp directories
                cleanup_temp_files()
                
                # Reset session state
                st.session_state.chat_history = []
                st.session_state.code_content = ""
                st.session_state.analysis_results = None
                st.session_state.llm_analysis = ""
                st.session_state.current_file = None
                
                # Remove results directory if it exists
                import shutil
                if os.path.exists("results"):
                    shutil.rmtree("results")
                if os.path.exists("configs"):
                    shutil.rmtree("configs")
                    
                st.success("✅ Temporary files and session data cleaned up!")
                st.rerun()  # Rerun the app to refresh the UI
            except Exception as e:
                st.error(f"Error during cleanup: {str(e)}")

        # Change Upload Folder label
        scan_target_type = st.radio(
            "Select Scan Target Type", 
            ["📝 Direct Code Input", "📤 Upload File", "📤 Upload Multiple Files"]  # Changed label here
        )

        # File upload options based on scan type
        uploaded_file = None
        uploaded_files = None
        code_input = None

        if scan_target_type == "📤 Upload File":
            uploaded_file = st.file_uploader(
                "Upload a file to scan", 
                type=["py", "js", "java", "cpp", "c", "cs", "php", "rb", "go", "ts", "html", "css", "sql"]
            )

        elif scan_target_type == "📤 Upload Multiple Files":  # Changed condition here
            uploaded_files = st.file_uploader(
                "Select multiple files to scan", 
                type=["py", "js", "java", "cpp", "c", "cs", "php", "rb", "go", "ts", "html", "css", "sql"], 
                accept_multiple_files=True,
                help="You can select multiple files by holding Ctrl/Cmd while clicking"
            )

        else:  # Direct code input
            code_input = st.text_area(
                "📝 Enter code to analyze", 
                height=300,
                value="""# Paste your code here for analysis
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query)
    return result.fetchone()
"""
            )

        # Other settings
        metrics_enabled = st.toggle("Enable Metrics", value=False)
        custom_config = st.file_uploader("📄 Upload Custom Semgrep Rules (.yaml)", type="yaml")

        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            llm_temperature = st.slider(
                "LLM Temperature", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.0, 
                step=0.1,
                help="Higher values make output more creative, lower values more deterministic"
            )
            
            model_selection = st.selectbox(
                "LLM Model", 
                options=[
                    "deepseek-r1-distill-llama-70b",
                    "llama3-70b-8192",
                    "llama-3.1-8b-instant",
                    "llama-3.2-11b-vision-preview",
                    "llama-3.2-1b-preview",
                    "llama-3.2-3b-preview",
                    "llama-3.3-70b-specdec",
                    "llama-3.3-70b-versatile",
                    "qwen-2.5-32b",
                    "qwen-2.5-coder-32b",
                    "mistral-saba-24b"
                ],
                help="Select the model to use for analysis"
            )

        # Store the settings in session state
        st.session_state['model_selection'] = model_selection
        st.session_state['llm_temperature'] = llm_temperature

        return {
            "scan_target_type": scan_target_type,
            "uploaded_file": uploaded_file,
            "uploaded_files": uploaded_files,
            "code_input": code_input,
            "metrics_enabled": metrics_enabled,
            "custom_config": custom_config,
            "llm_temperature": llm_temperature,
            "model_selection": model_selection
        }

def main():
    """Main application entry point."""
    # Load environment variables
    load_dotenv()

    # Initialize session state
    initialize_session_state()

    # Configure page
    configure_page()

    # Render sidebar and get settings
    settings = render_sidebar()

    # Create tabs
    tabs = st.tabs(["📊 Scanner", "💬 Security Chat", "📋 Custom Rules"])

    # Scanner Tab
    with tabs[0]:
        # Initialize empty results dictionary
        analysis_results = {
            'code_content': "",
            'llm_analysis': "",
            'report': ""
        }
        
        # Run scanner tab and get results
        if settings['uploaded_file'] or settings['uploaded_files'] or settings['code_input']:
            analysis_results = render_scanner_tab(**settings)
            
            # Update session state only if we got valid results
            if analysis_results and isinstance(analysis_results, dict):
                st.session_state.code_content = analysis_results.get('code_content', '')
                st.session_state.analysis_results = analysis_results
                st.session_state.llm_analysis = analysis_results.get('llm_analysis', '')

    # Chat Tab
    with tabs[1]:
        render_chat_tab()

    # Rules Tab
    with tabs[2]:
        render_rules_tab()

    # Footer
    st.markdown("---")
    st.markdown("SecureCode Scanner: Combining Semgrep and LLM for Advanced Vulnerability Detection")

if __name__ == "__main__":
    # Register cleanup function
    atexit.register(cleanup_temp_files)
    
    main()