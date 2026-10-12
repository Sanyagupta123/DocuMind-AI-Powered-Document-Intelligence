from __future__ import annotations

import math
from abc import ABC, abstractmethod

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    @abstractmethod
    def embed_many(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, max_features: int = 512) -> None:
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=max_features)
        self.fitted = False

    def fit(self, texts: list[str]) -> None:
        if not texts:
            return
        self.vectorizer.fit(texts)
        self.fitted = True

    def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            return []
        if not self.fitted:
            self.fit([text])
        vector = self.vectorizer.transform([text]).toarray()[0]
        return [float(value) for value in vector]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        texts = [text for text in texts if text and text.strip()]
        if not texts:
            return []
        self.fit(texts)
        matrix = self.vectorizer.transform(texts).toarray()
        return [[float(value) for value in row] for row in matrix]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    if len(left) != len(right):
        raise ValueError("Embedding vectors must have the same length.")
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    cosine = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)) if np.linalg.norm(a) and np.linalg.norm(b) else 0.0
    return float(cosine)
