import streamlit as st

from ..core.llm import initialize_llm
from ..core.security import security_chat

def render_chat_tab():
    """Render the security vulnerability chat tab."""
    st.subheader("💬 Security Vulnerability Chat")
    
    # Add direct code input for chat
    code_input = st.text_area(
        "Enter code to discuss", 
        height=200,
        value=st.session_state.get('code_content', ''),
        key="chat_code_input"
    )
    
    if code_input:
        st.session_state.code_content = code_input
    
    # Allow direct vulnerability input
    vulnerability_input = st.text_area(
        "Enter known vulnerabilities or security concerns",
        height=150,
        value=st.session_state.get('llm_analysis', ''),
        key="chat_vulnerability_input"
    )
    
    if vulnerability_input:
        st.session_state.llm_analysis = vulnerability_input
    
    # Display chat interface
    for message in st.session_state.get('chat_history', []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if user_query := st.chat_input("Ask about security concerns..."):
        st.session_state.chat_history = st.session_state.get('chat_history', [])
        st.session_state.chat_history.append({"role": "human", "content": user_query})
        
        with st.chat_message("human"):
            st.markdown(user_query)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Use LLM settings from sidebar
                llm = initialize_llm(
                    model=st.session_state.get('model_selection', "deepseek-r1-distill-llama-70b"),
                    temperature=st.session_state.get('llm_temperature', 0.2)
                )
                
                if llm:
                    response = security_chat(
                        st.session_state.code_content,
                        st.session_state.llm_analysis,
                        st.session_state.chat_history[:-1],
                        user_query,
                        llm
                    )
                    st.markdown(response)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": response}
                    )