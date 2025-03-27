def analyze_code_in_chunks(code_snippet, chunk_size=2000):
    """
    Split code into chunks for analysis, attempting to break at newlines.
    
    Args:
        code_snippet (str): Code to be chunked
        chunk_size (int): Approximate size of each chunk in tokens
    
    Returns:
        Union[str, List[str]]: Chunked code
    """
    # Rough approximation: 1 token ≈ 4 characters
    char_limit = chunk_size * 4
    
    if len(code_snippet) <= char_limit:
        return code_snippet
    
    # Split code into chunks, trying to break at newlines
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in code_snippet.split('\n'):
        line_size = len(line) + 1  # +1 for newline
        if current_size + line_size > char_limit and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = line_size
        else:
            current_chunk.append(line)
            current_size += line_size
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def chunk_chat_context(code_snippet, llm_analysis, chunk_size=1500):
    """
    Split chat context into manageable chunks.
    
    Args:
        code_snippet (str): Original code
        llm_analysis (str): LLM's security analysis
        chunk_size (int): Size of chunks in tokens
    
    Returns:
        Tuple[str, str]: Chunked code and analysis
    """
    total_text = f"{code_snippet}\n\n{llm_analysis}"
    if len(total_text) <= chunk_size * 4:  # Using same 4 char/token approximation
        return code_snippet, llm_analysis
    
    # If we need to chunk, prioritize keeping the analysis intact
    analysis_size = len(llm_analysis)
    max_code_size = (chunk_size * 4) - analysis_size - 100  # Buffer for other content
    
    if max_code_size < 100:  # If even minimal code won't fit
        # Chunk both code and analysis
        return (code_snippet[:max_code_size], 
                llm_analysis[:chunk_size * 2])  # Give more space to analysis
    
    # Otherwise just truncate the code
    return code_snippet[:max_code_size], llm_analysis

def chunk_rule_context(code_snippet, llm_analysis, chunk_size=1500):
    """
    Split rule generation context into manageable chunks.
    
    Args:
        code_snippet (str): Original code
        llm_analysis (str): LLM's security analysis
        chunk_size (int): Size of chunks in tokens
    
    Returns:
        Tuple[str, str]: Chunked code and analysis
    """
    total_text = f"{code_snippet}\n\n{llm_analysis}"
    if len(total_text) <= chunk_size * 4:
        return code_snippet, llm_analysis
    
    # For rules, we need both code context and analysis
    max_size_each = (chunk_size * 2)  # Split token budget between code and analysis
    
    chunked_code = code_snippet[:max_size_each * 4]  # Convert tokens to chars
    chunked_analysis = llm_analysis[:max_size_each * 4]
    
    return chunked_code, chunked_analysis