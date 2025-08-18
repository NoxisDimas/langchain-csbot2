from typing import Dict, Any
import logging
from app.services.llm.provider import get_chat_model
from app.services.langgraph.state import GraphState
from app.utils.sentiment import compute_sentiment
from app.services.langgraph.policies import apply_safety_policies
from app.services.langgraph.agent_react import (
	make_order_status_agent,
	make_product_reco_agent,
	make_general_qa_agent,
	make_handover_agent,
)

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = (
	"You are an AI customer service assistant. Default language to Indonesian for user-facing messages unless the user language is different."
	" Use English for internal reasoning and tool usage. Be concise, empathetic, and helpful."
)


def node_start(state: GraphState) -> GraphState:
	greeting = "Halo! Ada yang bisa saya bantu hari ini? Anda bisa menanyakan tentang status pesanan, rekomendasi produk, atau informasi umum lainnya."
	return {**state, "assistant_response": greeting}


def node_router(state: GraphState) -> GraphState:
	# Apply sentiment-based safety first
	state = apply_safety_policies(state)
	if state.get("handoff_to_human"):
		return {**state, "current_task": "Complaint"}

	model = get_chat_model(temperature=0.0)
	prompt = (
		f"{SYSTEM_PROMPT}\n"
		"Classify the user intent into one of: Order_Status, Product_Recommendation, General_Inquiry, Complaint."
		" Return ONLY the label.\n"
		f"User: {state.get('user_query','')}"
	)
	label = model.invoke(prompt).content.strip()
	current = label if label in {"Order_Status", "Product_Recommendation", "General_Inquiry", "Complaint"} else "Complaint"
	return {**state, "current_task": current}


def node_order_status_handler(state: GraphState) -> GraphState:
	agent = make_order_status_agent()
	resp = agent.invoke({"input": state.get("user_query", "")})
	answer = resp.get("output", "")
	return {**state, "assistant_response": answer}


def node_product_reco_handler(state: GraphState) -> GraphState:
	agent = make_product_reco_agent()
	resp = agent.invoke({"input": state.get("user_query", "")})
	answer = resp.get("output", "")
	return {**state, "assistant_response": answer}


def node_general_qa_handler(state: GraphState) -> GraphState:
	try:
		agent = make_general_qa_agent()
		resp = agent.invoke({"input": state.get("user_query", "")})
		answer = resp.get("output", "")
		return {**state, "assistant_response": answer}
	except Exception as e:
		logging.error(f"[General Agent] error: {e}")


def node_handover(state: GraphState) -> GraphState:
	agent = make_handover_agent()
	resp = agent.invoke({"input": state.get("user_query", "")})
	apology = resp.get("output", "Mohon maaf, saya tidak bisa membantu dengan pertanyaan ini. Saya akan mengalihkan Anda ke agen manusia kami. Mohon tunggu sebentar.")
	return {**state, "assistant_response": apology, "handoff_to_human": True}


def node_end(state: GraphState) -> GraphState:
	closing = "Apakah ada pertanyaan lain? Jika tidak, terima kasih telah menghubungi kami."
	return {**state, "assistant_response": closing}