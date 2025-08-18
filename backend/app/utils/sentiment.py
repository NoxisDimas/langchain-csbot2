from typing import Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def compute_sentiment(text: str) -> float:
	scores = _analyzer.polarity_scores(text)
	# compound is already in [-1,1]
	return float(scores.get("compound", 0.0))