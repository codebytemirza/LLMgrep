import os
import json
import subprocess
import streamlit as st
from datetime import datetime

from ..core.llm import initialize_llm
from ..core.security import analyze_security
from ..core.file_utils import save_uploaded_file, generate_report, save_code_to_temp_file

def render_scanner_tab(scan_target_type, uploaded_file=None, uploaded_files=None, 
                      code_input=None, metrics_enabled=False, custom_config=None, 
                      llm_temperature=0, model_selection="deepseek-r1-distill-llama-70b"):
    """Render the scanner tab with code preview and analysis results."""
    
    # Create columns for layout
    col1, col2 = st.columns([2, 3])
    
    code_content = ""
    target_path = None
    
    with col1:
        st.subheader("Code Preview")
        
        # Handle different input types
        if scan_target_type == "📝 Direct Code Input":
            code_content = code_input or ""
            st.code(code_content)
            if code_content:
                target_path = save_code_to_temp_file(code_content)
            
        elif scan_target_type == "📤 Upload File" and uploaded_file:
            code_content = uploaded_file.getvalue().decode("utf-8")
            st.code(code_content)
            target_path = save_uploaded_file(uploaded_file)
            
        elif scan_target_type == "📂 Upload Folder" and uploaded_files:
            st.info(f"Selected {len(uploaded_files)} files")
            selected_file = st.selectbox(
                "Select file to preview:",
                [file.name for file in uploaded_files]
            )
            for file in uploaded_files:
                if file.name == selected_file:
                    code_content = file.getvalue().decode("utf-8")
                    st.code(code_content)
                    break
            
            # Create folder for multiple files
            folder_path = os.path.join("temp_uploads", f"upload_folder_{datetime.now().strftime('%Y%m%d%H%M%S')}")
            os.makedirs(folder_path, exist_ok=True)
            for file in uploaded_files:
                file_path = os.path.join(folder_path, file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getvalue())
            target_path = folder_path
    
    with col2:
        st.subheader("Analysis Results")
        result_tabs = st.tabs(["LLM Analysis", "Semgrep Results"])
        
        # Run analysis button
        if st.button("🔍 Run Security Scan"):
            with st.spinner("Running security analysis..."):
                semgrep_results = run_semgrep_scan(target_path, metrics_enabled, custom_config, result_tabs[1])
                llm_analysis = run_llm_analysis(code_content, semgrep_results, llm_temperature, model_selection, result_tabs[0])
                
                report = generate_report(code_content, llm_analysis)
                
                return {
                    'code_content': code_content,
                    'llm_analysis': llm_analysis,
                    'semgrep_results': semgrep_results,
                    'report': report
                }
    
    return {
        'code_content': code_content,
        'llm_analysis': "",
        'report': ""
    }

def run_semgrep_scan(target_path, metrics_enabled, custom_config, result_tab):
    """Run Semgrep scan on the target."""
    if not target_path:
        return {"results": []}
    
    output_path = "results/result.json"
    os.makedirs("results", exist_ok=True)
    
    cmd = ["semgrep", "--json", "--output", output_path]
    if not metrics_enabled:
        cmd.append("--metrics=off")
    
    if custom_config:
        config_dir = "configs"
        os.makedirs(config_dir, exist_ok=True)
        config_filename = f"custom_config_{datetime.now().strftime('%Y%m%d%H%M%S')}.yaml"
        config_file = os.path.join(config_dir, config_filename)
        with open(config_file, "wb") as f:
            custom_config.seek(0)
            f.write(custom_config.read())
        cmd.append(f"--config={config_file}")
    else:
        cmd.append("--config=auto")
    
    cmd.append(target_path)
    
    with result_tab:
        with st.spinner("⏳ Running Semgrep scan..."):
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                try:
                    with open(output_path) as f:
                        semgrep_results = json.load(f)
                    display_semgrep_findings(semgrep_results)
                    return semgrep_results
                except Exception as e:
                    st.error(f"❌ Error parsing Semgrep results: {str(e)}")
            else:
                st.error("❌ Semgrep scan failed!")
                st.code(result.stderr)
    
    return {"results": []}

def run_llm_analysis(code_content, semgrep_results, temperature, model_selection, result_tab):
    """Run LLM analysis on the code."""
    with result_tab:
        with st.spinner("🧠 Running LLM analysis..."):
            llm = initialize_llm(model=model_selection, temperature=temperature)
            if llm and code_content:
                try:
                    llm_analysis = analyze_security(semgrep_results, code_content, llm)
                    st.markdown("## 🧠 Security Analysis")
                    st.markdown(llm_analysis)
                    return llm_analysis
                except Exception as e:
                    st.error(f"❌ Error during LLM analysis: {str(e)}")
    return ""

def display_semgrep_findings(semgrep_results):
    """Display formatted Semgrep findings."""
    st.subheader("🔍 Semgrep Findings:")
    if "results" in semgrep_results and semgrep_results["results"]:
        for i, finding in enumerate(semgrep_results["results"]):
            with st.expander(f"Finding #{i+1}: {finding.get('check_id', 'Unknown issue')}"):
                st.markdown(f"**Severity:** {finding.get('severity', 'Unknown')}")
                st.markdown(f"**Path:** {finding.get('path', 'Unknown')}")
                st.markdown(f"**Line:** {finding.get('start', {}).get('line', 'Unknown')}")
                st.markdown(f"**Message:** {finding.get('extra', {}).get('message', 'No message')}")
                st.code(finding.get('extra', {}).get('lines', 'No code available'))
    else:
        st.info("✅ No issues detected by Semgrep.")