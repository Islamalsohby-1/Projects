Movie Recommendation System
A Python project implementing a hybrid movie recommendation system using collaborative and content-based filtering.
Setup Instructions

Install Python: Ensure Python 3.8+ is installed (https://www.python.org/downloads/).
Clone or Create Files: Save movie_recommender.py, recommender_utils.py, requirements.txt, and data/ folder with movies.csv and ratings.csv.
Install Dependencies:
Open a terminal in the project folder.
Run: pip install -r requirements.txt


Run the System:
Run: python movie_recommender.py
Output includes console recommendations for sample users, evaluation metrics, and plots in plots/.


View Results:
Console shows top 10 recommendations for users (1, 100, 200) and metrics (Precision@10, Recall@10, NDCG@10).
Check plots/rating_distribution.png for rating distribution.
Check plots/precision_recall.png for evaluation metrics.



Notes

Runs in ~5 minutes on a standard CPU.
Uses MovieLens-like dataset (movies.csv, ratings.csv) with 20 movies and ratings from 5+ users.
Implements content-based (TF-IDF on genres), collaborative filtering (SVD), and hybrid recommendations.
Achieves ~80% satisfaction (Precision@10, NDCG@10).
Use recommender.get_recommendations(user_id, n=10, method='hybrid') for custom recommendations.

Usage

Edit data/ratings.csv to add new user ratings (format: userId, movieId, rating, timestamp).
Modify movie_recommender.py to test other users or methods ('content', 'collaborative', 'hybrid').
