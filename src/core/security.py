import json
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage

from ..utils.text_chunk import analyze_code_in_chunks, chunk_chat_context, chunk_rule_context

def analyze_security(semgrep_results, code_snippet, llm):
    """
    Analyze security of code using LLM and Semgrep results.
    
    Args:
        semgrep_results (dict): Results from Semgrep scan
        code_snippet (str): Code to analyze
        llm: Language Model for analysis
    
    Returns:
        str: Comprehensive security analysis
    """
    # Create prompt template for LLM
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert security analyst specializing in code vulnerability detection and remediation.
            
            Your task is to provide a comprehensive security analysis based on both:
            1. Semgrep scan results (which may detect known patterns)
            2. Your own expert analysis of the code (to catch vulnerabilities Semgrep might miss)
            
            For each vulnerability (whether detected by Semgrep or by your analysis), provide:
            1. VULNERABILITY: A clear name and explanation of the security issue
            2. CLASSIFICATION: The type of vulnerability (e.g., SQL Injection, XSS, CSRF, etc.)
            3. SEVERITY: Estimate the severity (Critical, High, Medium, Low)
            4. RISK: Explain the potential impact if exploited
            5. FIX: Provide specific code recommendations to fix the issue
            
            If Semgrep didn't detect any issues but you identify potential vulnerabilities, clearly indicate this.
            Use markdown formatting for better readability. Be specific and provide actionable advice.
            """
        ),
        ("human", """
        # Semgrep Results: 
        {semgrep_results}
        
        # Code for Analysis:
        ```
        {code_snippet}
        ```
        
        Please provide your comprehensive security assessment, focusing on both the Semgrep findings and your own expert analysis.
        """),
    ])
    
    try:
        # Check if code needs to be chunked
        code_chunks = analyze_code_in_chunks(code_snippet)
        
        if isinstance(code_chunks, list):
            # Analyze each chunk separately
            all_responses = []
            for i, chunk in enumerate(code_chunks, 1):
                chunk_prompt = f"[Analysis Part {i}/{len(code_chunks)}]\n\n"
                
                # Create and invoke chain for each chunk
                chain = (
                    {"semgrep_results": RunnablePassthrough(), "code_snippet": RunnablePassthrough()} 
                    | prompt 
                    | llm 
                    | StrOutputParser()
                )
                
                response = chain.invoke({
                    "semgrep_results": json.dumps(semgrep_results, indent=2),
                    "code_snippet": chunk
                })
                all_responses.append(chunk_prompt + response)
            
            # Combine all responses
            return "\n\n".join(all_responses)
        else:
            # Process single chunk normally
            chain = (
                {"semgrep_results": RunnablePassthrough(), "code_snippet": RunnablePassthrough()} 
                | prompt 
                | llm 
                | StrOutputParser()
            )
            
            return chain.invoke({
                "semgrep_results": json.dumps(semgrep_results, indent=2),
                "code_snippet": code_chunks
            })
            
    except Exception as e:
        if "413" in str(e) or "too large" in str(e).lower():
            return "❌ Error: Code size exceeds model's capacity even after chunking. Please try analyzing a smaller code sample."
        raise e

def security_chat(code_snippet, llm_analysis, chat_history, query, llm):
    """
    Generate security-focused chat responses.
    
    Args:
        code_snippet (str): Original code
        llm_analysis (str): Previous LLM security analysis
        chat_history (list): Conversation history
        query (str): User's current query
        llm: Language Model for response generation
    
    Returns:
        str: Chat response focused on vulnerabilities
    """
    # Chunk the context before processing
    chunked_code, chunked_analysis = chunk_chat_context(code_snippet, llm_analysis)
    
    # Convert chat history to the format expected by LangChain
    formatted_messages = []
    for msg in chat_history[-5:]:  # Only keep last 5 messages to manage context
        if msg["role"] == "human":
            formatted_messages.append(HumanMessage(content=msg["content"]))
        else:
            formatted_messages.append(AIMessage(content=msg["content"]))
    
    # Create prompt template for security chat
    chat_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert security advisor helping developers understand the vulnerabilities detected in their code.
            Focus on being educational, practical, and specific in your advice.
            Reference the identified vulnerabilities when relevant and provide concrete fixes.
            Answer questions specifically about the vulnerabilities that were identified in the previous analysis.
            """
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", """
        # Code Context:
        ```
        {code}
        ```
        
        # Previously Identified Vulnerabilities:
        {llm_analysis}
        
        # Query:
        {query}
        """),
    ])
    
    # Create and invoke chain
    chain = (
        {
            "code": lambda _: chunked_code, 
            "llm_analysis": lambda _: chunked_analysis,
            "query": lambda _: query, 
            "chat_history": lambda _: formatted_messages
        } 
        | chat_prompt 
        | llm 
        | StrOutputParser()
    )
    
    # Invoke the chain with an empty dict since we're using lambdas
    response = chain.invoke({})
    
    return response

def suggest_rules(code_snippet, llm_analysis, llm):
    """
    Generate custom Semgrep rules based on identified vulnerabilities.
    
    Args:
        code_snippet (str): Original code
        llm_analysis (str): Vulnerabilities analysis
        llm: Language Model for rule generation
    
    Returns:
        str: Generated Semgrep rules
    """
    # Chunk the context before processing
    chunked_code, chunked_analysis = chunk_rule_context(code_snippet, llm_analysis)
    
    # Create prompt template for rule suggestions
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a Semgrep rule expert. Based on the provided code and the vulnerabilities that were identified in the analysis, 
            create custom Semgrep rules that would help detect these specific vulnerabilities.
            
            Format each rule as valid YAML that can be directly used with Semgrep. Include:
            1. A brief description of what the rule detects
            2. The pattern to match
            3. The severity level
            4. The language it applies to
            
            Focus on creating rules that would have detected the specific vulnerabilities identified in the LLM analysis.
            """
        ),
        ("human", """
        # Code for Rule Generation:
        ```
        {code_snippet}
        ```
        
        # Identified Vulnerabilities:
        {llm_analysis}
        
        Please create custom Semgrep rules that would detect the specific vulnerabilities identified in the analysis.
        """),
    ])
    
    try:
        # Create and invoke chain with chunked content
        chain = (
            {"code_snippet": RunnablePassthrough(), "llm_analysis": RunnablePassthrough()} 
            | prompt 
            | llm 
            | StrOutputParser()
        )
        
        response = chain.invoke({
            "code_snippet": chunked_code,
            "llm_analysis": chunked_analysis
        })
        
        return response
    except Exception as e:
        if "413" in str(e) or "too large" in str(e).lower():
            return "❌ Error: Input size exceeds model's capacity even after chunking. Please try with a smaller code sample."
        raise e