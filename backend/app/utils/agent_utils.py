"""
Utility functions for handling agent parsing errors and fallback responses
"""

import logging
from typing import Dict, Any, Optional
from langchain_core.exceptions import OutputParserException

logger = logging.getLogger(__name__)


def handle_parsing_error(error: OutputParserException, user_query: str, agent_type: str) -> str:
    """
    Handle parsing errors and provide appropriate fallback responses
    
    Args:
        error: The OutputParserException that occurred
        user_query: The original user query
        agent_type: Type of agent that failed (order_status, product_reco, general_qa, handover)
    
    Returns:
        Fallback response string
    """
    logger.error(f"[{agent_type.upper()}] Parsing error: {error}")
    
    # Extract the problematic output for debugging
    error_message = str(error)
    if "Could not parse LLM output:" in error_message:
        # Extract the actual output that failed to parse
        start_idx = error_message.find("`") + 1
        end_idx = error_message.rfind("`")
        if start_idx > 0 and end_idx > start_idx:
            problematic_output = error_message[start_idx:end_idx]
            logger.error(f"[{agent_type.upper()}] Problematic output: {problematic_output}")
    
    # Provide context-aware fallback responses
    query_lower = user_query.lower()
    
    if agent_type == "general_qa":
        return _get_general_qa_fallback(query_lower)
    elif agent_type == "order_status":
        return _get_order_status_fallback(query_lower)
    elif agent_type == "product_reco":
        return _get_product_reco_fallback(query_lower)
    elif agent_type == "handover":
        return _get_handover_fallback(query_lower)
    else:
        return _get_generic_fallback(query_lower)


def _get_general_qa_fallback(query: str) -> str:
    """Get fallback response for general QA agent"""
    if any(word in query for word in ["halo", "hello", "hi", "hai"]):
        return "Halo! Ada yang bisa saya bantu hari ini?"
    elif any(word in query for word in ["terima kasih", "thanks", "thank you"]):
        return "Sama-sama! Ada yang bisa saya bantu lagi?"
    elif any(word in query for word in ["selamat pagi", "selamat siang", "selamat sore", "selamat malam"]):
        return "Selamat! Ada yang bisa saya bantu hari ini?"
    elif any(word in query for word in ["apa kabar", "how are you"]):
        return "Baik, terima kasih! Ada yang bisa saya bantu?"
    else:
        return "Maaf, saya mengalami kendala memproses pertanyaan Anda. Mohon coba lagi atau hubungi customer service kami."


def _get_order_status_fallback(query: str) -> str:
    """Get fallback response for order status agent"""
    if any(word in query for word in ["pesanan", "order", "status"]):
        return "Maaf, saya mengalami kendala memproses pertanyaan tentang status pesanan. Mohon coba lagi atau hubungi customer service kami."
    else:
        return "Maaf, saya mengalami kendala memproses pertanyaan Anda."


def _get_product_reco_fallback(query: str) -> str:
    """Get fallback response for product recommendation agent"""
    if any(word in query for word in ["rekomendasi", "recommendation", "produk", "product"]):
        return "Maaf, saya mengalami kendala memproses permintaan rekomendasi produk. Mohon coba lagi atau hubungi customer service kami."
    else:
        return "Maaf, saya mengalami kendala memproses pertanyaan Anda."


def _get_handover_fallback(query: str) -> str:
    """Get fallback response for handover agent"""
    return "Mohon maaf, saya tidak bisa membantu dengan pertanyaan ini. Saya akan mengalihkan Anda ke agen manusia kami. Mohon tunggu sebentar."


def _get_generic_fallback(query: str) -> str:
    """Get generic fallback response"""
    return "Maaf, saya mengalami kendala memproses pertanyaan Anda. Mohon coba lagi atau hubungi customer service kami."


def validate_agent_output(output: str) -> bool:
    """
    Validate if agent output follows expected format
    
    Args:
        output: The agent output to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not output:
        return False
    
    # Check for basic ReAct format elements
    has_question = "Question:" in output
    has_thought = "Thought:" in output
    has_action = "Action:" in output
    has_action_input = "Action Input:" in output
    has_final_answer = "Final Answer:" in output
    
    # Basic validation - should have at least Question, Thought, and Final Answer
    if not (has_question and has_thought and has_final_answer):
        return False
    
    # Check for proper line breaks
    lines = output.split('\n')
    if len(lines) < 3:
        return False
    
    return True


def sanitize_agent_input(text: str) -> str:
    """
    Sanitize input text for agent processing
    
    Args:
        text: Input text to sanitize
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Limit length to prevent token overflow
    max_length = 1000
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text