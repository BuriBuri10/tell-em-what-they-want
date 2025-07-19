import logging
from typing import List, Dict, Optional

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from data_preprocessing_pipeline.user_data_analyzer import UserDataAnalyzer

logger = logging.getLogger(__name__)


class Segmenter:
    """
    Clusters users into segments using KMeans on user feature embeddings.
    """

    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        """
        Initializes the Segmenter with clustering config.

        Args:
            n_clusters: Number of customer segments to create.
            random_state: Ensures reproducibility in clustering.
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        self.scaler = StandardScaler()

    def _extract_features(self, user_profiles: List[Dict]) -> np.ndarray:
        """
        Extracts numeric vectors from user profiles.

        Args:
            user_profiles: List of user metadata dicts.

        Returns:
            A 2D NumPy array of features.
        """
        logger.debug("Extracting features from user profiles...")
        feature_vectors = []
        for profile in user_profiles:
            vector = UserDataAnalyzer.extract_numeric_features(profile)
            feature_vectors.append(vector)
        return np.array(feature_vectors)

    def fit(self, user_profiles: List[Dict]) -> None:
        """
        Fits the clustering model to user data.

        Args:
            user_profiles: List of user metadata for training.
        """
        features = self._extract_features(user_profiles)
        scaled = self.scaler.fit_transform(features)
        self.kmeans.fit(scaled)
        logger.info("Segmenter model fitted to user data.")

    def predict(self, user_profiles: List[Dict]) -> List[int]:
        """
        Assigns cluster labels to new user profiles.

        Args:
            user_profiles: List of new user metadata.

        Returns:
            List of segment labels.
        """
        features = self._extract_features(user_profiles)
        scaled = self.scaler.transform(features)
        return self.kmeans.predict(scaled).tolist()

    def segment_users(self, user_profiles: List[Dict]) -> List[Dict]:
        """
        Annotates each user profile with a predicted segment ID.

        Args:
            user_profiles: Raw user profile dicts.

        Returns:
            List of enriched user dicts with 'segment_id'.
        """
        logger.debug("Segmenting users...")
        labels = self.predict(user_profiles)
        for profile, label in zip(user_profiles, labels):
            profile["segment_id"] = label
        logger.info("User segmentation completed.")
        return user_profiles
