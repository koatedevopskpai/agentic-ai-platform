# =============================================================================
# src/services/tools.py — Agent Tool Definitions
# =============================================================================
# Context:
#   Three LangChain tools the agent can invoke: calculate
#   (math expressions), analyze_text (text statistics), and
#   knowledge_base (internal Q&A). All run offline with no
#   external API dependencies.
#
# Architectural Reasoning:
#   - @tool decorator from LangChain: provides automatic schema
#     generation from function signatures + docstrings, binds to
#     LLM function-calling, and supports .invoke() for direct
#     execution. Adding a tool is a one-function change.
#   - calculate uses a restricted eval with a whitelist (math
#     module, builtins blocked). Safe for user-provided expressions
#     that need math operations; not safe for arbitrary code.
#   - knowledge_base uses simple keyword matching over a hardcoded
#     dict. No vector DB, no embedding cost, zero dependencies.
#     For portfolio demo, keyword coverage > semantic search.
#   - TOOL_MAP dict bridges tool name strings to callable objects
#     for runtime dispatch. run_tool() is the single entry point
#     used by the agent loop — no conditional logic per tool.
#
# Trade-offs:
#   - Restricted eval vs AST parsing. Eval is simpler but cannot
#     provide safe error messages for syntax errors. AST parsing
#     (ast.parse + whitelist walk) would be safer but ~4x more code.
#   - Keyword matching vs vector search for knowledge_base. Vector
#     search handles synonyms and phrasing differences. Keyword
#     matching is deterministic and works with zero setup — the
#     right choice for a portfolio demo.
#
# Opinionated Stance:
#   Tools are the agent's interface to the world. Each tool should
#   do one thing well, accept typed inputs, and return structured
#   string output. Function-calling tools must be deterministic
#   — no randomness, no hidden state.
# =============================================================================
from __future__ import annotations

import logging
import math
import time
from typing import Any

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Input must be a valid Python math expression using +, -, *, /, **, math.sqrt, math.sin, etc."""
    allowed_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "int": int, "float": float,
        "math": math,
    }
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {e}"


@tool
def analyze_text(text: str) -> str:
    """Analyze text and return statistics: word count, character count, sentence count, estimated reading time, and unique words."""
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    sentence_count = text.count(".") + text.count("!") + text.count("?")
    reading_time = max(1, round(word_count / 200))
    unique_words = len(set(w.lower().strip(".,!?;:'\"") for w in words))
    return (
        f"Word count: {word_count}\n"
        f"Character count: {char_count}\n"
        f"Sentence count: {sentence_count}\n"
        f"Estimated reading time: {reading_time} min\n"
        f"Unique words: {unique_words}"
    )


@tool
def knowledge_base(query: str) -> str:
    """Search the internal knowledge base for information about AI engineering, software architecture, and best practices."""
    knowledge: dict[str, str] = {
        "rag": (
            "Retrieval-Augmented Generation (RAG) combines retrieval from a vector database "
            "with LLM generation. It grounds answers in external knowledge, reduces hallucination, "
            "and enables updating knowledge without retraining."
        ),
        "agent": (
            "An AI agent is an LLM-powered system that can use tools, maintain state across steps, "
            "and make decisions about which actions to take next. Agents use reasoning loops: "
            "observe -> think -> act -> observe."
        ),
        "langgraph": (
            "LangGraph is a framework for building stateful, multi-actor LLM applications. "
            "It extends LangChain by adding: cyclic graphs (loops), conditional edges, "
            "persistent state, and human-in-the-loop patterns. Nodes represent functions; "
            "edges define the control flow."
        ),
        "mcp": (
            "Model Context Protocol (MCP) is an open standard for connecting AI assistants "
            "to external tools and data sources. It provides a unified interface for tool "
            "discovery, authentication, and invocation."
        ),
        "prompt engineering": (
            "Prompt engineering is the practice of designing inputs to LLMs to produce "
            "desired outputs. Key techniques: system prompts, few-shot examples, chain-of-thought "
            "reasoning, structured output formatting, and persona assignment."
        ),
        "vector database": (
            "Vector databases store embeddings (vector representations of data) and enable "
            "semantic similarity search. Examples: Chroma (embedded/local), Pinecone (managed), "
            "Qdrant (self-hosted). They are the foundation of RAG systems."
        ),
        "fine tuning": (
            "Fine-tuning updates LLM weights on domain-specific data. It changes model behaviour "
            "permanently. Use for tone/style adaptation or specialized output formats. RAG is "
            "preferred for knowledge retrieval; fine-tuning for behaviour modification."
        ),
        "evaluation": (
            "LLM evaluation measures output quality. Metrics: faithfulness (is the answer "
            "grounded in context?), relevance (does it address the query?), and precision "
            "(does it avoid extra information?). Frameworks: RAGAS, LangSmith, custom LLM-as-judge."
        ),
    }
    query_lower = query.lower()
    best_key = None
    best_score = 0
    for key in knowledge:
        if key in query_lower:
            score = len(key) / len(query_lower)
            if score > best_score:
                best_score = score
                best_key = key
    if best_key:
        return f"Source: AI Knowledge Base\n\n{knowledge[best_key]}"
    return "No relevant information found in the internal knowledge base."


TOOL_MAP: dict[str, Any] = {
    "calculate": calculate,
    "analyze_text": analyze_text,
    "knowledge_base": knowledge_base,
}


def run_tool(name: str, args: dict[str, Any]) -> str:
    tool_func = TOOL_MAP.get(name)
    if not tool_func:
        return f"Error: unknown tool '{name}'"
    try:
        result = tool_func.invoke(args)
        return str(result)
    except Exception as e:
        return f"Error executing {name}: {e}"
