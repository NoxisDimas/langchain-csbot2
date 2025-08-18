from fastapi import APIRouter

router = APIRouter()


@router.get("/design")
def design_overview():
	return {
		"nodes": [
			"start",
			"router",
			"order_status",
			"product_reco",
			"general_qa",
			"handover",
			"end",
		],
		"state": [
			"conversation_history",
			"user_query",
			"current_task",
			"user_profile",
			"knowledge_refs",
			"sentiment_score",
			"handoff_to_human",
			"locale",
			"pii_redactions",
			"detected_language",
			"order_id",
			"assistant_response",
		],
	}