import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from config.config import GROQ_API_KEY, GROQ_MODEL


def get_chatgroq_model():
    """Initialize and return the Groq chat model"""
    try:
        groq_model = ChatGroq(
            api_key=GROQ_API_KEY,
            model=GROQ_MODEL,
        )
        return groq_model
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Groq model: {str(e)}")


def get_chat_response(chat_model, messages: list, system_prompt: str, context: str = "", mode: str = "Concise") -> str:
    """Get response from the chat model with RAG context and response mode"""
    try:
        mode_instruction = (
            "Reply concisely in 2-3 sentences. Be direct and to the point."
            if mode == "Concise"
            else "Reply in detail with clear structure, examples, and explanations where relevant."
        )

        full_system_prompt = f"""{system_prompt}

Use the following retrieved context to answer the user's question about compliance frameworks.
{mode_instruction}

Context:
{context}

If the context is insufficient to answer the question, clearly say so and provide
what general knowledge you have about the topic."""

        formatted_messages = [SystemMessage(content=full_system_prompt)]

        for msg in messages[:-1]:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            else:
                formatted_messages.append(AIMessage(content=msg["content"]))

        formatted_messages.append(HumanMessage(content=messages[-1]["content"]))

        response = chat_model.invoke(formatted_messages)
        return response.content

    except Exception as e:
        return f"Error getting response: {str(e)}"