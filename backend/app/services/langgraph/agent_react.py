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

	Use the following format:
	Question: {{input}}
	Thought: you should always think about what to do
	Action: the tool to use, should be one of [{{tool_names}}]
	Action Input: the input to the tool
	Final Answer: the final answer to the original input question

	Begin!
	{{agent_scratchpad}}
	"""
	return PromptTemplate.from_template(template)


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
	)
	model = get_chat_model(temperature=0.0)
	tools = _order_status_tools()
	agent = create_react_agent(model, tools, _react_prompt(system))
	return AgentExecutor(agent=agent, tools=tools, verbose=False)


def make_product_reco_agent() -> AgentExecutor:
	system = (
		"You are a helpful product recommendation assistant."
		" Understand preferences and return 1-3 options with titles and links."
	)
	model = get_chat_model(temperature=0.2)
	tools = _product_reco_tools()
	agent = create_react_agent(model, tools, _react_prompt(system))
	return AgentExecutor(agent=agent, tools=tools, verbose=False)


def make_general_qa_agent() -> AgentExecutor:
	system = (
		"You are a knowledgeable assistant."
		" Translate the query to English for retrieval and synthesize a concise answer from snippets."
		" If not found, say you're not sure and suggest contacting support."
	)
	model = get_chat_model(temperature=0.2)
	try :
		tools = _general_qa_tools()
		agent = create_react_agent(model, tools, _react_prompt(system))
		return AgentExecutor(agent=agent, tools=tools, verbose=False)
	except Exception as e:
		logging.error(f"[General agent]: {e}")
		return None


def make_handover_agent() -> AgentExecutor:
	system = (
		"You are a handover coordinator."
		" Apologize and inform that a human agent will take over, then notify support channels."
	)
	model = get_chat_model(temperature=0.0)
	tools = _handover_tools()
	agent = create_react_agent(model, tools, _react_prompt(system))
	return AgentExecutor(agent=agent, tools=tools, verbose=False)