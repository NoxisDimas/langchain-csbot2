from typing import Dict, Any
import logging
from langchain_core.exceptions import OutputParserException
from app.services.llm.provider import get_chat_model
from app.services.langgraph.state import GraphState
from app.utils.sentiment import compute_sentiment
from app.services.langgraph.policies import apply_safety_policies
from app.utils.agent_utils import handle_parsing_error, sanitize_agent_input
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
	try:
		agent = make_order_status_agent()
		if agent is None:
			logging.error("[Order Status Agent] Failed to create agent")
			return {**state, "assistant_response": "Maaf, saya mengalami kendala memproses pertanyaan tentang status pesanan. Mohon coba lagi atau hubungi customer service kami."}
		
		user_query = sanitize_agent_input(state.get("user_query", ""))
		resp = agent.invoke({"input": user_query})
		answer = resp.get("output", "")
		return {**state, "assistant_response": answer}
	except OutputParserException as e:
		fallback_response = handle_parsing_error(e, state.get("user_query", ""), "order_status")
		return {**state, "assistant_response": fallback_response}
	except Exception as e:
		logging.error(f"[Order Status Agent] error: {e}")
		return {**state, "assistant_response": "Maaf, saya mengalami kendala memproses pertanyaan Anda."}


def node_product_reco_handler(state: GraphState) -> GraphState:
	try:
		agent = make_product_reco_agent()
		if agent is None:
			logging.error("[Product Reco Agent] Failed to create agent")
			return {**state, "assistant_response": "Maaf, saya mengalami kendala memproses permintaan rekomendasi produk. Mohon coba lagi atau hubungi customer service kami."}
		
		user_query = sanitize_agent_input(state.get("user_query", ""))
		resp = agent.invoke({"input": user_query})
		answer = resp.get("output", "")
		return {**state, "assistant_response": answer}
	except OutputParserException as e:
		fallback_response = handle_parsing_error(e, state.get("user_query", ""), "product_reco")
		return {**state, "assistant_response": fallback_response}
	except Exception as e:
		logging.error(f"[Product Reco Agent] error: {e}")
		return {**state, "assistant_response": "Maaf, saya mengalami kendala memproses pertanyaan Anda."}


def node_general_qa_handler(state: GraphState) -> GraphState:
	try:
		agent = make_general_qa_agent()
		if agent is None:
			logging.error("[General Agent] Failed to create agent")
			return {**state, "assistant_response": "Maaf, saya mengalami kendala memproses pertanyaan Anda. Mohon coba lagi atau hubungi customer service kami."}
		
		user_query = sanitize_agent_input(state.get("user_query", ""))
		resp = agent.invoke({"input": user_query})
		answer = resp.get("output", "")
		return {**state, "assistant_response": answer}
	except OutputParserException as e:
		fallback_response = handle_parsing_error(e, state.get("user_query", ""), "general_qa")
		return {**state, "assistant_response": fallback_response}
	except Exception as e:
		logging.error(f"[General Agent] error: {e}")
		return {**state, "assistant_response": "Maaf, saya mengalami kendala memproses pertanyaan Anda."}


def node_handover(state: GraphState) -> GraphState:
	try:
		agent = make_handover_agent()
		if agent is None:
			logging.error("[Handover Agent] Failed to create agent")
			return {**state, "assistant_response": "Mohon maaf, saya tidak bisa membantu dengan pertanyaan ini. Saya akan mengalihkan Anda ke agen manusia kami. Mohon tunggu sebentar.", "handoff_to_human": True}
		
		user_query = sanitize_agent_input(state.get("user_query", ""))
		resp = agent.invoke({"input": user_query})
		apology = resp.get("output", "Mohon maaf, saya tidak bisa membantu dengan pertanyaan ini. Saya akan mengalihkan Anda ke agen manusia kami. Mohon tunggu sebentar.")
		return {**state, "assistant_response": apology, "handoff_to_human": True}
	except OutputParserException as e:
		fallback_response = handle_parsing_error(e, state.get("user_query", ""), "handover")
		return {**state, "assistant_response": fallback_response, "handoff_to_human": True}
	except Exception as e:
		logging.error(f"[Handover Agent] error: {e}")
		return {**state, "assistant_response": "Mohon maaf, saya mengalami kendala. Saya akan mengalihkan Anda ke agen manusia kami.", "handoff_to_human": True}


def node_end(state: GraphState) -> GraphState:
	if state.get("assistant_response"):
		return state
	closing = "Apakah ada pertanyaan lain? Jika tidak, terima kasih telah menghubungi kami."
	return {**state, "assistant_response": closing}