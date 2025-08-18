import logging
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from app.services.llm.provider import get_chat_model
from app.services.langgraph import tools as toolset

logging.basicConfig(level=logging.INFO)

def _react_prompt(system_instructions: str) -> PromptTemplate:
	# Must include variables: input, tools, tool_names, agent_scratchpad
	template = f"""
	{system_instructions}

	You have access to the following tools:
	{{tools}}

	Tool names for reference:
	{{tool_names}}

	CRITICAL FORMATTING RULES:
	- You MUST follow the EXACT format below
	- Use EXACTLY one tool per Action step
	- If you output an Action, DO NOT output Final Answer in the same step
	- AFTER an Action, WAIT for an Observation before continuing
	- Only output Final Answer when you have enough information and no further Action is needed
	- NEVER combine multiple actions in one step
	- ALWAYS use the exact format with proper line breaks
	- NEVER use commas in Action Input - use separate lines

	REQUIRED FORMAT:
	Question: {{input}}
	Thought: you should always think about what to do
	Action: the tool to use, should be one of [{{tool_names}}]
	Action Input: the input to the tool

	Observation: the result of the action
	... (this Thought/Action/Action Input/Observation can repeat N times)
	Thought: I now know the final answer
	Final Answer: the final answer to the original input question

	Begin!
	{{agent_scratchpad}}
	"""
	return PromptTemplate.from_template(template)


def _create_agent_with_fallback(system: str, tools: list, temperature: float = 0.2):
	"""Create agent with fallback mechanism"""
	try:
		model = get_chat_model(temperature=temperature)
		agent = create_react_agent(model, tools, _react_prompt(system))
		return AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True, max_iterations=3)
	except Exception as e:
		logging.error(f"Failed to create agent: {e}")
		return None


def _order_status_tools():
	return [
		toolset.extract_order_id_tool,
		toolset.get_order_status_tool,
		toolset.analyze_sentiment_tool,
	]


def _product_reco_tools():
	return [
		toolset.search_products_tool,
		toolset.retrieve_memory_tool,
	]


def _general_qa_tools():
	return [
		toolset.translate_to_english_tool,
		toolset.retrieve_kb_snippets_tool,
	]


def _handover_tools():
	return [
		toolset.notify_email_support_tool,
		toolset.notify_telegram_support_tool,
	]


def make_order_status_agent() -> AgentExecutor:
	system = (
		"You are an expert customer service assistant focused on order status."
		" Extract order id if missing, else call the order status tool."
		" Keep answers brief and polite."
		" IMPORTANT: Follow the exact format specified above."
	)
	return _create_agent_with_fallback(system, _order_status_tools(), temperature=0.0)


def make_product_reco_agent() -> AgentExecutor:
	system = (
		"You are a helpful product recommendation assistant."
		" Understand preferences and return 1-3 options with titles and links."
		" IMPORTANT: Follow the exact format specified above."
	)
	return _create_agent_with_fallback(system, _product_reco_tools(), temperature=0.2)


def make_general_qa_agent() -> AgentExecutor:
	system = (
		"You are a knowledgeable assistant."
		" Translate the query to English for retrieval and synthesize a concise answer from snippets."
		" If not found, say you're not sure and suggest contacting support."
		" IMPORTANT: Follow the exact format specified above."
		" CRITICAL: Always use proper line breaks between Thought, Action, Action Input, and Observation."
		" CRITICAL: Never use commas in Action Input - use separate lines or spaces."
	)
	return _create_agent_with_fallback(system, _general_qa_tools(), temperature=0.2)


def make_handover_agent() -> AgentExecutor:
	system = (
		"You are a handover coordinator."
		" Apologize and inform that a human agent will take over, then notify support channels."
		" IMPORTANT: Follow the exact format specified above."
	)
	return _create_agent_with_fallback(system, _handover_tools(), temperature=0.0)