import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import precision_score, recall_score

def dcg_score(relevant, k):
    """Calculate Discounted Cumulative Gain."""
    relevant = np.array(relevant)[:k]
    if len(relevant) == 0:
        return 0.0
    return np.sum(relevant / np.log2(np.arange(2, len(relevant) + 2)))

def ndcg_score(relevant, k):
    """Calculate Normalized Discounted Cumulative Gain."""
    dcg = dcg_score(relevant, k)
    ideal_relevant = sorted(relevant, reverse=True)
    idcg = dcg_score(ideal_relevant, k)
    return dcg / idcg if idcg > 0 else 0.0

def evaluate_recommendations(predictions, movie_titles, k=10):
    """Evaluate recommendations using precision@k, recall@k, and NDCG."""
    user_recs = {}
    user_relevant = {}
    
    # Group predictions by user
    for pred in predictions:
        uid, mid, true_r, est, _ = pred
        if true_r >= 4:  # Consider ratings >= 4 as relevant
            user_relevant.setdefault(uid, []).append(mid)
        user_recs.setdefault(uid, []).append((mid, est))
    
    precision_scores = []
    recall_scores = []
    ndcg_scores = []
    
    for uid in user_recs:
        # Sort recommendations by estimated rating
        recs = sorted(user_recs[uid], key=lambda x: x[1], reverse=True)[:k]
        rec_ids = [mid for mid, _ in recs]
        relevant = user_relevant.get(uid, [])
        
        # True positives: recommended movies that are relevant
        true_positives = [1 if mid in relevant else 0 for mid in rec_ids]
        
        # Precision@k
        precision = sum(true_positives) / k
        precision_scores.append(precision)
        
        # Recall@k
        recall = sum(true_positives) / len(relevant) if relevant else 0
        recall_scores.append(recall)
        
        # NDCG@k
        ndcg = ndcg_score(true_positives, k)
        ndcg_scores.append(ndcg)
    
    return {
        'precision': np.mean(precision_scores),
        'recall': np.mean(recall_scores),
        'ndcg': np.mean(ndcg_scores)
    }

def plot_rating_distribution(ratings, output_file):
    """Plot distribution of user ratings."""
    plt.figure(figsize=(10, 6))
    sns.histplot(ratings['rating'], bins=9, kde=True, color='skyblue')
    plt.title('Distribution of User Ratings')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def plot_metrics(metrics, output_file):
    """Plot precision-recall metrics."""
    plt.figure(figsize=(8, 6))
    plt.bar(['Precision@10', 'Recall@10', 'NDCG@10'], 
            [metrics['precision'], metrics['recall'], metrics['ndcg']],
            color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    plt.title('Recommendation System Evaluation Metrics')
    plt.ylabel('Score')
    for i, v in enumerate([metrics['precision'], metrics['recall'], metrics['ndcg']]):
        plt.text(i, v + 0.01, f'{v:.2%}', ha='center')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()