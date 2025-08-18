from langgraph.graph import StateGraph, END
from app.services.langgraph.state import GraphState
from app.services.langgraph.nodes import (
	node_start,
	node_router,
	node_order_status_handler,
	node_product_reco_handler,
	node_general_qa_handler,
	node_handover,
	node_end,
)


def _route_from_task(state: GraphState):
	intent = (state.get("current_task") or "").strip()
	if intent == "Order_Status":
		return "order_status"
	if intent == "Product_Recommendation":
		return "product_reco"
	if intent == "General_Inquiry":
		return "general_qa"
	return "handover"


def get_compiled_graph():
	workflow = StateGraph(GraphState)
	workflow.add_node("start", node_start)
	workflow.add_node("router", node_router)
	workflow.add_node("order_status", node_order_status_handler)
	workflow.add_node("product_reco", node_product_reco_handler)
	workflow.add_node("general_qa", node_general_qa_handler)
	workflow.add_node("handover", node_handover)
	workflow.add_node("end", node_end)

	# start -> router
	workflow.add_edge("start", "router")
	# router -> dynamic handler
	workflow.add_conditional_edges("router", _route_from_task, {
		"order_status": "order_status",
		"product_reco": "product_reco",
		"general_qa": "general_qa",
		"handover": "handover",
	})
	# handlers -> end (standard)
	workflow.add_edge("order_status", "end")
	workflow.add_edge("product_reco", "end")
	workflow.add_edge("general_qa", "end")
	workflow.add_edge("handover", "end")

	workflow.set_entry_point("start")
	return workflow.compile()