import os
import tempfile
from datetime import datetime

def save_uploaded_file(uploaded_file):
    """
    Save an uploaded file to a temporary directory.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        str: Path to the saved file
    """
    # Create temp dir if it doesn't exist
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique file path
    file_path = os.path.join(temp_dir, uploaded_file.name)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def read_file_content(file_path):
    """
    Read content of a file.
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        str: File content or error message
    """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_files_from_folder(folder_path, max_files=5):
    """
    Collect code files from a folder.
    
    Args:
        folder_path (str): Path to the folder
        max_files (int): Maximum number of files to collect
    
    Returns:
        dict: Mapping of file paths to their contents
    """
    code_files = {}
    file_count = 0
    
    for file in os.listdir(folder_path):
        if file_count >= max_files:
            break
        
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and not file.startswith('.'):
            try:
                with open(file_path, 'r') as f:
                    code_files[file_path] = f.read()
                    file_count += 1
            except:
                pass
    
    return code_files

def save_code_to_temp_file(code_content, file_extension=".py"):
    """
    Save code content to a temporary file.
    
    Args:
        code_content (str): Code content to save
        file_extension (str): File extension to use (default: .py)
    
    Returns:
        str: Path to the saved temporary file
    """
    # Create temp dir if it doesn't exist
    temp_dir = "temp_code"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"code_{timestamp}{file_extension}"
    file_path = os.path.join(temp_dir, filename)
    
    # Save the code content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code_content)
    
    return file_path

def generate_report(code_content, llm_analysis):
    """
    Generate a markdown report for security analysis.
    
    Args:
        code_content (str): Code that was analyzed
        llm_analysis (str): LLM's security analysis
    
    Returns:
        str: Markdown-formatted report
    """
    return f"""# Security Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Code Analyzed
```
{code_content[:1000]}... [truncated if longer]
```

## Security Analysis
{llm_analysis}
"""

def cleanup_temp_files():
    """
    Clean up temporary files and directories.
    """
    import shutil
    try:
        # List of directories to clean
        dirs_to_clean = ["temp_code", "temp_uploads", "results", "configs"]
        
        for dir_path in dirs_to_clean:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    print(f"Error cleaning {dir_path}: {str(e)}")
        
        # Recreate necessary directories
        os.makedirs("temp_code", exist_ok=True)
        os.makedirs("temp_uploads", exist_ok=True)
        os.makedirs("results", exist_ok=True)
        os.makedirs("configs", exist_ok=True)
        
    except Exception as e:
        raise Exception(f"Error during cleanup: {str(e)}")