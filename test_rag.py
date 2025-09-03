#!/usr/bin/env python3
"""
Test RAG agent directly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.rag_agent import rag_agent


def test_rag_agent():
    print("Testing RAG agent...")

    query = "什么是深度学习？有哪些主要的神经网络类型？"

    try:
        result = rag_agent.process_question(query=query, session_id="test_session")

        print("✅ RAG agent test successful!")
        print(f"Success: {result['success']}")
        if result["success"]:
            print(
                f"Answer: {result.get('answer', {}).get('text', 'No answer')[:200]}..."
            )
        else:
            print(f"Error: {result.get('error')}")
        return result["success"]

    except Exception as e:
        print(f"❌ RAG agent test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_rag_agent()
