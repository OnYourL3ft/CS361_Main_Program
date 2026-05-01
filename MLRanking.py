# Brandon Smith
# CS361
# Spring 2026
# Main Project - TV Show App, ML Ranking
 
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
 
# feature columns used for KMeans clustering - must match CS432 project
FEATURE_COLS = ['Average Runtime', 'Critic_Rating', 'Total Seasons', 'Total Episodes', 'User_Rating', 'vote_count']
 
# number of clusters, determined by silhouette score
K = 5
 
# variables to hold fitted model and scaler 
kmeans_TV = None
scaler_TV = None
 
# -----------------------------------------------------------------------
# Function: fits KMeans model and scaler on the full AppData dataset at startup.
# Must be called once before rank_shows() is used.
#  input: AppData dataframe (full unfiltered dataset)
#  returns: None. Model is declared as global variable for use outside function
# -----------------------------------------------------------------------
def fit_model(AppData):

    # global 
    global kmeans_TV, scaler_TV
 
    # extract the six feature columns used for clustering
    features = AppData[FEATURE_COLS]
 
    # scale features to standardize before clustering
    scaler_TV = StandardScaler()
    features_scaled = scaler_TV.fit_transform(features)
 
    # fit KMeans on the full dataset using k=5
    kmeans_TV = KMeans(n_clusters=K, max_iter=100, random_state=42)
    kmeans_TV.fit(features_scaled)
 
 
# -----------------------------------------------------------------------
# Function: ranks a filtered set of TV shows using the KMeans model.
# Ranks using cluster centroids and sorts results by ml_score descending.
# Ties are broken by Critic_Rating descending.
#  input: user filtered dataframe of candidate TV shows
#  returns: dataframe sorted by ml_score descending, with ml_score and
#           Cluster columns added. Returns empty dataframe if input is empty.
# -----------------------------------------------------------------------
def rank_shows(candidates):
 
    # return empty dataframe if no candidates passed in
    if candidates.empty:
        return candidates
 
    # extract feature columns from candidates
    features = candidates[FEATURE_COLS]
 
    # scale candidates using the scaler fit on the full dataset
    features_scaled = scaler_TV.transform(features)
 
    # get cluster assignments for each candidate
    cluster_labels = kmeans_TV.predict(features_scaled)
 
    # get distances from each show to all cluster centroids
    distances = kmeans_TV.transform(features_scaled)
 
    # get distance to each show's assigned centroid
    assigned_centroid_distances = distances[np.arange(len(distances)), cluster_labels]
 
    # normalize distance to produce ml_score between 0 and 1
    # shows closer to their centroid receive a higher score
    max_distance = assigned_centroid_distances.max()
    if max_distance == 0:
        # all shows are at the same distance - assign equal scores
        ml_scores = np.ones(len(assigned_centroid_distances))
    else:
        ml_scores = 1 - (assigned_centroid_distances / max_distance)
 
    # add ml_score and Cluster columns to results, won't be displayed to user
    ranked = candidates.copy()
    ranked['ml_score'] = ml_scores.round(4)
    ranked['Cluster'] = cluster_labels
 
    # sort by ml_score descending, ties broken by Critic_Rating descending
    ranked = ranked.sort_values(by=['ml_score', 'Critic_Rating'], ascending=[False, False])
    ranked = ranked.reset_index(drop=True)
 
    return ranked