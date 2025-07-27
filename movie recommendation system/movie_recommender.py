import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from recommender_utils import evaluate_recommendations, plot_metrics, plot_rating_distribution
import matplotlib.pyplot as plt
import os

# Set random seed for reproducibility
np.random.seed(42)

class MovieRecommender:
    def __init__(self, movies_file='data/movies.csv', ratings_file='data/ratings.csv'):
        """Initialize recommender with movie and rating data."""
        self.movies = pd.read_csv(movies_file)
        self.ratings = pd.read_csv(ratings_file)
        self.movies['genres'] = self.movies['genres'].fillna('').str.replace('|', ' ')
        
        # Content-based: TF-IDF on genres
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.movies['genres'])
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        
        # Collaborative filtering: SVD
        reader = Reader(rating_scale=(1, 5))
        self.data = Dataset.load_from_df(self.ratings[['userId', 'movieId', 'rating']], reader)
        self.trainset, self.testset = train_test_split(self.data, test_size=0.2, random_state=42)
        self.svd = SVD(random_state=42)
        self.svd.fit(self.trainset)
        
        # Store movie titles for output
        self.movie_titles = self.movies.set_index('movieId')['title'].to_dict()

    def content_based_recommendations(self, movie_id, n=10):
        """Get content-based recommendations for a given movie."""
        idx = self.movies[self.movies['movieId'] == movie_id].index[0]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:n+1]
        movie_indices = [i[0] for i in sim_scores]
        return [(self.movies.iloc[i]['movieId'], self.movies.iloc[i]['title'], sim_scores[i][1]) 
                for i in movie_indices]

    def collaborative_filtering_recommendations(self, user_id, n=10):
        """Get collaborative filtering recommendations for a user using SVD."""
        movie_ids = self.movies['movieId'].unique()
        user_ratings = self.ratings[self.ratings['userId'] == user_id]['movieId'].values
        unrated_movies = [mid for mid in movie_ids if mid not in user_ratings]
        
        predictions = [(mid, self.svd.predict(user_id, mid).est) for mid in unrated_movies]
        predictions = sorted(predictions, key=lambda x: x[1], reverse=True)[:n]
        return [(mid, self.movie_titles[mid], score) for mid, score in predictions]

    def hybrid_recommendations(self, user_id, n=10, alpha=0.5):
        """Combine content-based and collaborative filtering recommendations."""
        user_ratings = self.ratings[self.ratings['userId'] == user_id]
        if user_ratings.empty:
            return []
        
        # Get collaborative filtering scores
        collab_recs = self.collaborative_filtering_recommendations(user_id, n*2)
        collab_scores = {mid: score for mid, _, score in collab_recs}
        
        # Get content-based scores for rated movies
        content_scores = {}
        for _, row in user_ratings.iterrows():
            movie_id = row['movieId']
            cb_recs = self.content_based_recommendations(movie_id, n*2)
            for mid, _, score in cb_recs:
                content_scores[mid] = content_scores.get(mid, 0) + score * row['rating'] / 5
        
        # Combine scores
        hybrid_scores = {}
        for mid in set(collab_scores.keys()) | set(content_scores.keys()):
            collab = collab_scores.get(mid, 0)
            content = content_scores.get(mid, 0)
            hybrid_scores[mid] = alpha * collab + (1 - alpha) * content
        
        # Sort and return top N
        top_movies = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:n]
        return [(mid, self.movie_titles[mid], score) for mid, score in top_movies]

    def get_recommendations(self, user_id, n=10, method='hybrid'):
        """Get top N recommendations for a user using specified method."""
        if method == 'content':
            user_ratings = self.ratings[self.ratings['userId'] == user_id]
            if user_ratings.empty:
                return []
            movie_id = user_ratings.sort_values('rating', ascending=False).iloc[0]['movieId']
            return self.content_based_recommendations(movie_id, n)
        elif method == 'collaborative':
            return self.collaborative_filtering_recommendations(user_id, n)
        else:  # hybrid
            return self.hybrid_recommendations(user_id, n)

    def evaluate_system(self, k=10):
        """Evaluate recommendation system using precision@k, recall@k, and NDCG."""
        predictions = self.svd.test(self.testset)
        return evaluate_recommendations(predictions, self.movie_titles, k)

    def plot_results(self):
        """Generate visualizations for ratings and evaluation metrics."""
        os.makedirs('plots', exist_ok=True)
        
        # Rating distribution
        plot_rating_distribution(self.ratings, 'plots/rating_distribution.png')
        
        # Precision-Recall curve
        metrics = self.evaluate_system(k=10)
        plot_metrics(metrics, 'plots/precision_recall.png')

def main():
    """Run the movie recommendation system."""
    recommender = MovieRecommender()
    
    # Evaluate system
    metrics = recommender.evaluate_system(k=10)
    print("Evaluation Metrics (k=10):")
    print(f"Precision@10: {metrics['precision']:.2%}")
    print(f"Recall@10: {metrics['recall']:.2%}")
    print(f"NDCG@10: {metrics['ndcg']:.2%}")
    
    # Generate recommendations for sample users
    sample_users = [1, 100, 200]
    for user_id in sample_users:
        print(f"\nTop 10 Recommendations for User {user_id} (Hybrid):")
        recs = recommender.get_recommendations(user_id, n=10, method='hybrid')
        for i, (movie_id, title, score) in enumerate(recs, 1):
            print(f"{i}. {title} (MovieID: {movie_id}, Score: {score:.2f})")
    
    # Plot results
    recommender.plot_results()
    print("\nPlots saved in 'plots/' directory")

if __name__ == '__main__':
    main()