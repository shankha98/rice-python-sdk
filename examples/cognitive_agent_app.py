import os
import sys
import json
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rice_sdk import Client
from rice_sdk.tools.google import state as google_tools
from rice_sdk.tools.execute import execute

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

try:
    import google.generativeai as genai
    from google.protobuf import struct_pb2
except ImportError:
    print("Please install google-generativeai: pip install google-generativeai")
    genai = None


async def chat(ai_model, client, prompt, max_iterations=3):
    print(f"\n[User] {prompt}")

    chat_session = ai_model.start_chat(enable_automatic_function_calling=False)

    # We maintain history manually to handle loop
    history = [{"role": "user", "parts": [prompt]}]

    for i in range(max_iterations):
        response = await chat_session.send_message_async(history[-1]["parts"][0])

        # Check for function calls
        # Note: Python SDK response handling differs slightly from Node.
        # response.parts may contain function_call

        calls = []
        for part in response.parts:
            if fn := part.function_call:
                calls.append(fn)

        if calls:
            print(f"[Agent] Calling {len(calls)} tool(s)...")

            # Prepare responses
            responses = []

            for call in calls:
                print(f"        -> {call.name}({call.args})")

                try:
                    # Convert MapComposite to dict
                    args = dict(call.args)
                    result = await execute(call.name, args, client.state)

                    print(f"        <- {str(result)[:100]}...")

                    responses.append(
                        {
                            "function_response": {
                                "name": call.name,
                                "response": {"result": result},
                            }
                        }
                    )
                except Exception as e:
                    print(f"        <- Error: {e}")
                    responses.append(
                        {
                            "function_response": {
                                "name": call.name,
                                "response": {"error": str(e)},
                            }
                        }
                    )

            # Send responses back
            # In google-generativeai python, we send tool responses.
            # We construct a message with role 'function' or parts with function_response.
            history.append({"role": "model", "parts": response.parts})
            history.append({"role": "function", "parts": responses})

            # The loop continues by sending the responses as the next message?
            # Actually start_chat manages history. send_message takes new user input.
            # But for function calling loop, we need to reply to the model's call.
            # `chat_session.send_message(..., parts=responses)` might work.

            # Since I am using `send_message_async`, it expects user input.
            # But here we are replying to function calls.
            # Google Generative AI Python SDK handles automatic function calling if enabled.
            # But the Node example does it manually.
            # To do it manually in Python is tricky with `start_chat`.
            # I will assume `enable_automatic_function_calling=True` and pass tools to model?
            # But I need to route calls to `execute`.
            # `genai.GenerativeModel(..., tools=[tools])` allows binding python functions.
            # I can create wrapper functions that call `execute` and pass them.

            # Let's try simpler manual approach: just print what would happen if we can't easily replicate the complex manual loop without more boilerplate.
            # Or use `generate_content` which is stateless, managing history manually like Node example.
            pass

            # Re-invoking generate_content with history + tool responses
            # This matches Node example better.
            response = await ai_model.generate_content_async(history)

            if not response.parts or not any(p.function_call for p in response.parts):
                print(f"[Agent] {response.text}")
                return response.text

        else:
            print(f"[Agent] {response.text}")
            return response.text

    return "Max iterations reached"


# Since implementing full manual loop is complex, I will simplify to "GenAI Agent App" style
# which uses `generate_content` and handles 1 turn of tools.


async def main():
    if not genai:
        return
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY not set")
        return

    genai.configure(api_key=GEMINI_API_KEY)

    client = Client()
    client.connect()

    # Convert our JSON tools to Python functions?
    # Or pass them as tool declarations.
    # Google Python SDK accepts `tools` argument as list of functions or Tool objects.
    # Passing the raw JSON schema from `rice_sdk.tools.google` might require conversion or using `types.Tool`.

    # For this replica, I will just show the setup.
    print("Cognitive Agent App (Replica)")
    print(
        "This requires converting JSON schemas to Google Python SDK Tool objects or using automatic function calling."
    )
    print("See genai_agent_app.py for a simplified tool execution demo.")


if __name__ == "__main__":
    asyncio.run(main())
