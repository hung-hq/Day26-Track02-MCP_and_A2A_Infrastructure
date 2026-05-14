"""Stage 1: Direct LLM Calling

The simplest way to use an LLM — send a message, get a response.
No tools, no memory, no agents. Just a direct API call.

This is stateless: the LLM has no access to external data sources,
cannot look things up, and relies entirely on its training data.
"""

import asyncio
import os
import sys

# Allow running directly: python stages/stage_1_direct_llm/main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from common.llm import get_llm

QUESTION = (
    "Nếu một công ty vi phạm thỏa thuận bảo mật (NDA), "
    "hậu quả pháp lý có thể là gì?"
)


async def main():
    print("=" * 70)
    print("STAGE 1: Direct LLM Calling")
    print("=" * 70)
    print()
    print("[How it works]")
    print("  1. Gửi SystemMessage + HumanMessage trực tiếp cho LLM")
    print("  2. LLM trả lời chỉ từ dữ liệu huấn luyện")
    print("  3. Không tools, không retrieval, không external memory")
    print()
    print(f"Question: {QUESTION}")
    print("-" * 70)

    llm = get_llm()

    messages = [
        SystemMessage(
            content=(
                "You are a legal expert. Provide a clear, concise analysis "
                "of the legal question asked. Keep your response under 300 words."
            )
        ),
        HumanMessage(content=QUESTION),
    ]

    print("\n>>> Gọi LLM trực tiếp (không tools, không RAG)...\n")
    response = await llm.ainvoke(messages)
    print(response.content)

    print()
    print("-" * 70)
    print("[Limitations of Stage 1]")
    print("  - Stateless: không nhớ hội thoại giữa các lần gọi")
    print("  - No tools: không thể tra cứu database hoặc tính toán")
    print("  - Knowledge cutoff: chỉ biết dữ liệu trong training")
    print("  - No grounding: không tự tra cứu luật/case law mới")
    print()
    print("Next: Stage 2 adds RAG and tools to ground responses in real data.")
    print("=" * 70)


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())