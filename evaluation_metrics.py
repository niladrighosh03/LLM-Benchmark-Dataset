import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Load model globally to avoid reloading often
# 'all-MiniLM-L6-v2' is a good balance of speed and performance
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except:
    print("SentenceTransformer model not found. Please install sentence-transformers.")
    model = None

def get_embeddings(texts):
    if model is None:
        return []
    return model.encode(texts)

def calculate_coverage_score(questions, source_chunks):
    """
    Calculates the coverage score of questions against source chunks.
    
    Metric: Mean of the maximum cosine similarity for each source chunk against all questions.
    This tells us: "For every part of the source text, is there a question that is semantically close to it?"
    
    Args:
        questions (list of str): List of question texts.
        source_chunks (list of str): List of source text chunks (e.g., pages).
        
    Returns:
        float: Coverage score (0 to 1).
        list of float: Per-chunk max similarity scores.
    """
    if not questions or not source_chunks:
        return 0.0, []
    
    q_embeddings = get_embeddings(questions)
    s_embeddings = get_embeddings(source_chunks)
    
    # Similarity matrix: Use cosine_similarity
    # shape: (n_source_chunks, n_questions)
    sim_matrix = cosine_similarity(s_embeddings, q_embeddings)
    
    # For each source chunk, find the max similarity to ANY question
    max_sim_per_chunk = np.max(sim_matrix, axis=1)
    
    coverage_score = np.mean(max_sim_per_chunk)
    
    return coverage_score, max_sim_per_chunk

def calculate_diversity_score(questions):
    """
    Calculates the diversity score of the questions.
    
    Metric: 1 - Mean pairwise cosine similarity among questions.
    Higher is better (more diverse).
    
    Args:
        questions (list of str): List of question texts.
        
    Returns:
        float: Diversity score (0 to 1).
    """
    if len(questions) < 2:
        return 1.0 # Trivial diversity
        
    q_embeddings = get_embeddings(questions)
    
    # Pairwise similarity
    sim_matrix = cosine_similarity(q_embeddings)
    
    # We want to ignore the diagonal (self-similarity is always 1)
    # Get upper triangle indices
    triu_indices = np.triu_indices_from(sim_matrix, k=1)
    
    mean_pairwise_sim = np.mean(sim_matrix[triu_indices])
    
    diversity_score = 1.0 - mean_pairwise_sim
    return diversity_score

def calculate_topic_depth(questions, source_chunks, threshold=0.4):
    """
    Calculates how many unique source chunks are 'covered' by at least one question.
    
    Args:
        questions (list of str): List of questions.
        source_chunks (list of str): List of source chunks.
        threshold (float): Similarity threshold to consider a chunk 'covered'.
        
    Returns:
        float: Fraction of chunks covered (0.0 to 1.0).
        int: Absolute number of chunks covered.
    """
    if not questions or not source_chunks:
        return 0.0, 0
        
    q_embeddings = get_embeddings(questions)
    s_embeddings = get_embeddings(source_chunks)
    
    # helper for calculating similarity
    sim_matrix = cosine_similarity(s_embeddings, q_embeddings)
    
    # Max sim for each chunk
    max_sims = np.max(sim_matrix, axis=1)
    
    # Count chunks with max_sim > threshold
    covered_count = np.sum(max_sims > threshold)
    fraction = covered_count / len(source_chunks)
    
    return fraction, int(covered_count)

def llm_evaluate_question(question_row, source_text, llm_func=None):
    """
    Evaluates a single question using an LLM.
    
    Args:
        question_row (dict/Series): Row from the dataframe containing question, options, answer.
        source_text (str): Relevant source text for verification.
        llm_func (callable): Function that takes a prompt and returns a response string.
        
    Returns:
        dict: Evaluation results (correctness_bool, quality_score, reason).
    """
    if llm_func is None:
        return {"error": "No LLM function provided"}

    prompt = f"""
    You are an expert evaluator for educational content. 
    Analyze the following Multiple Choice Question (MCQ) based on the provided Source Text.
    
    Source Text:
    {source_text[:2000]}... (truncated)
    
    Question: {question_row['question']}
    Options:
    A) {question_row['option_A']}
    B) {question_row['option_B']}
    C) {question_row['option_C']}
    D) {question_row['option_D']}
    Correct Answer: {question_row['correct_answer']}
    
    Task:
    1. Verify if the 'Correct Answer' is indeed correct according to the Source Text.
    2. Rate the quality of the question on a scale of 1-5 based on clarity, relevance, and lack of ambiguity.
    
    Output Format:
    Correctness: [True/False]
    Quality Score: [1-5]
    Reasoning: [Brief explanation]
    """
    
    response = llm_func(prompt)
    # In a real scenario, we would parse the response.
    # For now, returning raw response or a mock structure if we were mocking.
    return response

