import re
import yaml
import streamlit as st

from ..core.llm import initialize_llm
from ..core.security import suggest_rules

def extract_yaml_blocks(text):
    """
    Extract and validate YAML blocks from text.
    
    Args:
        text (str): Text containing YAML blocks
        
    Returns:
        list: List of valid YAML blocks
    """
    # Find all text blocks between ``` markers
    yaml_blocks = []
    pattern = r"```yaml\n(.*?)\n```"
    matches = re.finditer(pattern, text, re.DOTALL)
    
    for match in matches:
        yaml_text = match.group(1).strip()
        try:
            # Validate YAML by attempting to parse it
            yaml_obj = yaml.safe_load(yaml_text)
            if yaml_obj:  # Only add if parsing produced a valid object
                yaml_blocks.append(yaml_text)
        except yaml.YAMLError:
            continue
            
    return yaml_blocks

def render_rules_tab():
    """Render the custom rules generation tab."""
    st.subheader("📋 Generate Custom Semgrep Rules")
    
    # Add direct code input for rule generation
    code_input = st.text_area(
        "Enter code for rule generation", 
        height=200,
        value=st.session_state.get('code_content', ''),
        key="rules_code_input"
    )
    
    # Add vulnerability description input
    vulnerability_input = st.text_area(
        "Describe vulnerabilities to create rules for",
        height=150,
        value=st.session_state.get('llm_analysis', ''),
        key="rules_vulnerability_input"
    )
    
    if st.button("🔍 Generate Rules", key="generate_rules_button"):
        with st.spinner("Generating Semgrep rules..."):
            # Use LLM settings from sidebar
            llm = initialize_llm(
                model=st.session_state.get('model_selection', "deepseek-r1-distill-llama-70b"),
                temperature=st.session_state.get('llm_temperature', 0.1)
            )
            
            if llm and code_input:
                try:
                    rules = suggest_rules(code_input, vulnerability_input, llm)
                    
                    st.markdown("## 📋 Generated Rules")
                    st.markdown(rules)
                    
                    # Extract and validate YAML blocks
                    yaml_blocks = extract_yaml_blocks(rules)
                    if yaml_blocks:
                        combined_yaml = "\n---\n".join(yaml_blocks)
                        st.download_button(
                            "📥 Download Rules",
                            combined_yaml,
                            file_name="custom_semgrep_rules.yaml",
                            mime="text/yaml",
                            key="download_rules_button"
                        )
                except Exception as e:
                    st.error(f"Error generating rules: {str(e)}")