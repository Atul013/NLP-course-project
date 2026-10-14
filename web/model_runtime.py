"""Exact sparse TF-IDF + binary logistic inference from exported fitted weights.

Mirrors the source pipeline's word unigrams/bigrams, sublinear TF, stored IDF,
L2 normalization, and sigmoid. No fitting, approximation, or heuristic scoring.
"""
from collections import Counter
import json
import math
from pathlib import Path
import re


def load_weights(path: Path) -> dict:
    model = json.loads(path.read_text(encoding="utf-8"))
    if model["format"] != "phish-lens-linear-v1":
        raise ValueError("Unsupported exported model")
    return model


def predict_weights(model: dict, processed: str, top_k: int = 8) -> dict:
    words = re.findall(model["token_pattern"], processed)
    features = words + [f"{left} {right}" for left, right in zip(words, words[1:])]
    counts = Counter(model["vocabulary"][term] for term in features if term in model["vocabulary"])
    weighted = {index: (1 + math.log(count)) * model["idf"][index] for index, count in counts.items()}
    # sklearn's sparse vectors are ordered by ascending feature index.
    indices = sorted(weighted)
    norm = math.sqrt(sum(weighted[index] ** 2 for index in indices))
    contributions = {index: weighted[index] / norm * model["coefficients"][index] for index in indices} if norm else {}
    logit = model["intercept"] + sum(contributions.values())
    probability = 1 / (1 + math.exp(-logit)) if logit >= 0 else math.exp(logit) / (1 + math.exp(logit))
    names = {index: term for term, index in model["vocabulary"].items()}
    ordered = sorted(indices, key=lambda index: abs(contributions[index]), reverse=True)[:top_k]
    return {
        "label": "phishing" if probability >= 0.5 else "benign",
        "phishing_probability": probability,
        "probability_note": "Uncalibrated model probability; not a security risk score.",
        "influential_terms": [{
            "term": names[index],
            "direction": "phishing" if contributions[index] > 0 else "benign",
            "contribution": contributions[index],
        } for index in ordered],
        "matched_features": len(indices),
    }
