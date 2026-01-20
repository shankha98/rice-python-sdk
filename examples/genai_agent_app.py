import os
import sys
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
except ImportError:
    print("Please install google-generativeai")
    genai = None


async def main():
    if not genai:
        return
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY not set")
        return

    genai.configure(api_key=GEMINI_API_KEY)

    client = Client()
    client.connect()

    # Create model with tools
    # Note: google-generativeai python sdk expects `tools` to be a list of functions,
    # or `Tool` objects. It doesn't natively consume the JSON schema format used in the JS/REST API
    # as easily as passing a dict.
    # However, for this example, we assume we can pass tool definitions.
    # In Python SDK, we often pass the functions themselves.

    # We will declare a wrapper function for the model to see.
    def focus(content: str):
        """Stores a piece of information in working memory (State/Flux)."""
        pass

    def recall(query: str):
        """Recalls relevant memories from State based on a query."""
        pass

    # ... mapping all tools to python functions is tedious here.

    print("GenAI Agent App Demo")
    print("Connected to Rice.")

    # Mock interaction loop
    prompt = "Remember that I like pizza."
    print(f"\nUser: {prompt}")

    # In a real impl, we would call model.generate_content(prompt, tools=[focus, recall...])
    # Then execute returned function calls.

    # For replica purposes, we show how to manually execute if we had the call.
    print("Simulating model response: call remember(content='I like pizza')")

    try:
        res = await execute("remember", {"content": "I like pizza"}, client.state)
        print("Tool Result:", res)
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
