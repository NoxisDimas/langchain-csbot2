from app.utils.sentiment import compute_sentiment
from app.services.langgraph.state import GraphState


def apply_safety_policies(state: GraphState) -> GraphState:
	text = state.get("user_query", "")
	s = compute_sentiment(text)
	if s <= -0.6:
		# escalate to human
		state["handoff_to_human"] = True
	return {**state, "sentiment_score": s}