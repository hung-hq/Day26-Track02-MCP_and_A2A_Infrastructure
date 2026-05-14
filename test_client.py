"""End-to-end test client for the Legal Multi-Agent System.

Sends a legal question to the Customer Agent and prints the response.
"""

import asyncio
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

CUSTOMER_AGENT_URL = os.getenv("CUSTOMER_AGENT_URL", "http://localhost:10100")

QUESTION = (
    "If a company breaks a contract and avoids taxes, "
    "what are the legal and regulatory consequences?"
)


async def main() -> None:
    print(f"Connecting to Customer Agent at {CUSTOMER_AGENT_URL}")
    print(f"Question: {QUESTION}")
    print("-" * 60)

    async with httpx.AsyncClient(timeout=300.0) as http_client:
        # Resolve agent card
        card_url = f"{CUSTOMER_AGENT_URL}/.well-known/agent.json"
        try:
            card_resp = await http_client.get(card_url)
            card_resp.raise_for_status()
        except Exception as e:
            print(f"ERROR: Could not reach Customer Agent at {card_url}")
            print(f"  {e}")
            print("Make sure all services are running (./start_all.sh)")
            sys.exit(1)

        from a2a.types import AgentCard, Message, Part, Role, TextPart, MessageSendParams
        from a2a.client import A2AClient
        from uuid import uuid4

        agent_card = AgentCard.model_validate(card_resp.json())
        print(f"Connected to agent: {agent_card.name} v{agent_card.version}")
        print("-" * 60)

        # Build the legacy A2AClient
        client = A2AClient(httpx_client=http_client, agent_card=agent_card)

        # Construct the message
        from a2a.types import SendMessageRequest, MessageSendParams as MSP
        message = Message(
            role=Role.user,
            parts=[Part(root=TextPart(text=QUESTION))],
            message_id=str(uuid4()),
        )
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MSP(message=message),
        )

        print("Sending request (this may take 30-60s while agents chain)...\n")
        response = await client.send_message(request)

        # Parse response
        def _collect_text_from_parts(parts) -> str:
            out = ""
            for part in parts or []:
                p = part.root if hasattr(part, "root") else part
                if hasattr(p, "text") and p.text:
                    out += p.text
            return out

        result_text = ""
        task_state = None
        if hasattr(response, "root"):
            root = response.root
            if hasattr(root, "result"):
                result = root.result
                if hasattr(result, "status") and result.status:
                    task_state = getattr(result.status, "state", None)
                    if hasattr(result.status, "message") and result.status.message:
                        status_msg = _collect_text_from_parts(result.status.message.parts)
                        if status_msg:
                            result_text += status_msg
                # Task with artifacts
                if hasattr(result, "artifacts") and result.artifacts:
                    for artifact in result.artifacts:
                        result_text += _collect_text_from_parts(artifact.parts)
                # Message with parts
                elif hasattr(result, "parts") and result.parts:
                    result_text += _collect_text_from_parts(result.parts)
                # Fallback: read latest message in history
                elif hasattr(result, "history") and result.history:
                    for message in reversed(result.history):
                        history_text = _collect_text_from_parts(getattr(message, "parts", []))
                        if history_text:
                            result_text += history_text
                            break

        if result_text:
            title = "RESPONSE" if str(task_state) != "TaskState.failed" else "AGENT ERROR"
            print(f"{title}:")
            print("=" * 60)
            print(result_text)
            print("=" * 60)
        else:
            print("No text response received. Raw response:")
            print(response)


if __name__ == "__main__":
    asyncio.run(main())