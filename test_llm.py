#!/usr/bin/env python3
"""
Test LLM service directly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.llm_service import llm_service
from langchain.schema import Document


def test_llm_service():
    print("Testing LLM service...")

    # Create a test document
    test_doc = Document(
        page_content="深度学习是机器学习的一个子领域，使用人工神经网络来模拟人脑处理信息的方式。主要包括CNN（卷积神经网络）用于图像处理，RNN（循环神经网络）用于序列数据，以及Transformer架构用于自然语言处理。",
        metadata={"source": "test_doc", "type": "text"},
    )

    # Test query
    query = "什么是深度学习？有哪些主要的神经网络类型？"

    try:
        result = llm_service.generate_answer(
            query=query, context_documents=[test_doc], session_id="test_session"
        )

        print("✅ LLM service test successful!")
        print(f"Answer: {result['text'][:200]}...")
        return True

    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_llm_service()
