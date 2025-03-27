import os
import streamlit as st
from langchain_groq import ChatGroq
import dotenv

def initialize_llm(model="deepseek-r1-distill-llama-70b", temperature=0):
    """
    Initialize and return a Groq Language Model.
    
    Args:
        model (str): Name of the model to use
        temperature (float): Controls randomness of output
    
    Returns:
        ChatGroq: Initialized language model or None
    """
    # Load environment variables
    dotenv.load_dotenv()

    # Check if API key is set
    if "GROQ_API_KEY" not in os.environ:
        st.error("⚠️ GROQ_API_KEY not found in environment variables. Please add it to your .env file.")
        return None

    try:
        llm = ChatGroq(
            model=model,
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        return llm
    except Exception as e:
        st.error(f"❌ Error initializing Groq LLM: {str(e)}")
        return None