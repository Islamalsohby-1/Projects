import pandas as pd
import numpy as np
from openai import OpenAI
import os
from tqdm import tqdm
import time
from sentence_transformers import SentenceTransformer, util
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import logging
import csv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_prompts(file_path):
    """Load prompt variations from a CSV or TXT file."""
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        return df['prompt'].tolist(), df['type'].tolist()
    elif file_path.endswith('.txt'):
        with open(file_path, 'r') as f:
            prompts = [line.strip() for line in f if line.strip()]
        return prompts, ['unknown'] * len(prompts)
    else:
        raise ValueError("File must be .csv or .txt")

def mock_openai_response(prompt):
    """Simulate an OpenAI response for testing without an API key."""
    return {
        'choices': [{'message': {'content': f"Mock response to: {prompt}"}}],
        'usage': {'total_tokens': len(prompt.split()) * 2}
    }

def get_openai_response(prompt, client=None):
    """Send prompt to OpenAI API or return mock response."""
    if client:
        try:
            start_time = time.time()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            latency = time.time() - start_time
            return response, latency
        except Exception as e:
            logger.error(f"Error with OpenAI API: {e}")
            return None, 0
    else:
        return mock_openai_response(prompt), 0

def score_response(response, prompt, expected_answer=None):
    """Score a response based on coherence, relevance, and length."""
    if not response or not hasattr(response, 'choices') or not response.choices:
        return 0, 0, 0

    text = response.choices[0].message.content
    tokens = response.usage.total_tokens if hasattr(response, 'usage') else len(text.split())

    # Coherence: Simple heuristic based on sentence count and length consistency
    sentences = text.split('.')
    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    coherence = min(1.0, len(sentences) / 10.0) if sentence_lengths else 0
    if sentence_lengths:
        coherence *= 1 - (np.std(sentence_lengths) / (np.mean(sentence_lengths) + 1))

    # Relevance: Cosine similarity with prompt
    vectorizer = CountVectorizer().fit_transform([prompt, text])
    relevance = cosine_similarity(vectorizer)[0][1]

    # Length: Normalize by desired length range (50-500 tokens)
    length_score = min(1.0, max(0.0, (tokens - 50) / (500 - 50)))

    # Optional: Semantic similarity to expected answer
    semantic_score = 0
    if expected_answer:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode([text, expected_answer])
        semantic_score = util.cos_sim(embeddings[0], embeddings[1]).item()

    # Weighted average score
    total_score = (coherence * 0.3 + relevance * 0.4 + length_score * 0.2 + semantic_score * 0.1)
    return total_score, tokens, coherence, relevance, length_score, semantic_score

def generate_wordcloud(texts, title, filename):
    """Generate and save a word cloud from texts."""
    text = ' '.join(texts)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    plt.savefig(filename)
    plt.close()

def visualize_results(df):
    """Generate visualizations: bar chart and word clouds."""
    # Bar chart of top 10 prompt scores
    top_10 = df.nlargest(10, 'Score')
    plt.figure(figsize=(12, 6))
    plt.barh(top_10['Prompt'].str[:50] + '...', top_10['Score'])
    plt.xlabel('Score')
    plt.title('Top 10 Prompt Performance')
    plt.tight_layout()
    plt.savefig('prompt_performance.png')
    plt.close()

    # Word clouds for high/low scoring responses
    high_scoring = df.nlargest(20, 'Score')['Response'].tolist()
    low_scoring = df.nsmallest(20, 'Score')['Response'].tolist()
    generate_wordcloud(high_scoring, 'High Scoring Responses', 'high_scoring_wordcloud.png')
    generate_wordcloud(low_scoring, 'Low Scoring Responses', 'low_scoring_wordcloud.png')

def optimize_prompts(file_path, base_task, expected_answer=None, api_key=None):
    """Main function to optimize prompts."""
    logger.info("Starting prompt optimization")
    
    # Initialize OpenAI client if API key provided
    client = OpenAI(api_key=api_key) if api_key else None
    
    # Load prompts
    prompts, prompt_types = load_prompts(file_path)
    
    # Initialize results
    results = []
    
    # Process each prompt
    for prompt, p_type in tqdm(zip(prompts, prompt_types), total=len(prompts), desc="Processing prompts"):
        response, latency = get_openai_response(prompt, client)
        score, tokens, coherence, relevance, length_score, semantic_score = score_response(response, prompt, expected_answer)
        
        results.append({
            'Prompt': prompt,
            'Type': p_type,
            'Response': response.choices[0].message.content if response and response.choices else '',
            'Score': score,
            'Tokens': tokens,
            'Latency': latency,
            'Coherence': coherence,
            'Relevance': relevance,
            'Length_Score': length_score,
            'Semantic_Score': semantic_score
        })
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Generate summary statistics
    logger.info("\nSummary Statistics:")
    logger.info("\nTop 5 Prompts:")
    logger.info(df.nlargest(5, 'Score')[['Prompt', 'Score', 'Type']].to_string())
    
    logger.info("\nAverage Scores by Prompt Type:")
    type_stats = df.groupby('Type')['Score'].agg(['mean', 'count']).round(3)
    logger.info(type_stats.to_string())
    
    # Save results
    df.to_csv('results.csv', index=False)
    
    # Generate visualizations
    visualize_results(df)
    
    logger.info("\nResults saved to results.csv")
    logger.info("Visualizations saved: prompt_performance.png, high_scoring_wordcloud.png, low_scoring_wordcloud.png")

if __name__ == "__main__":
    # Example usage
    file_path = "prompts.csv"
    base_task = "Summarize an article"
    expected_answer = "A concise summary capturing the main points of the article in 100-200 words."
    api_key = os.getenv("OPENAI_API_KEY")  # Set to None for mock responses
    
    optimize_prompts(file_path, base_task, expected_answer, api_key)