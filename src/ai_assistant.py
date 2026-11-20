
import os
import json
import httpx

from typing import Any
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

# Connect to Groq using the OpenAI Python SDK
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-20b"
API_BASE_URL = "http://127.0.0.1:8000"


# Tools available to the AI
tools: list[Any] = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search HYFUX products by name or keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Product name or keyword."
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_products",
            "description": (
                "Get HYFUX products, optionally filtered by category "
                "or maximum price. Can return only orderable products."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": ["string", "null"]
                    },
                    "max_price": {
                        "type": ["number", "null"]
                    },
                    "orderable_only": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "category",
                    "max_price",
                    "orderable_only"
                ],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_categories",
            "description": "Get all categories in the HYFUX menu.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        }
    }
]


# Execute the selected tool through our FastAPI
def execute_tool(name, arguments):
    with httpx.Client(timeout=10.0) as http:

        if name == "search_products":
            response = http.get(
                f"{API_BASE_URL}/products/search",
                params={"q": arguments["query"]}
            )

        elif name == "get_products":
            params = {
                "orderable_only": arguments["orderable_only"]
            }
            if arguments["category"] is not None:
                params["category"] = arguments["category"]
            if arguments["max_price"] is not None:
                params["max_price"] = arguments["max_price"]
            response = http.get(
                f"{API_BASE_URL}/products",
                params=params
            )

        elif name == "get_categories":
            response = http.get(
                f"{API_BASE_URL}/categories"
            )

        else:
            raise ValueError(f"Unknown tool: {name}")

        response.raise_for_status()
        return response.json()


# Ask the AI a question
def ask_hyfux(question):

    messages = [
        {
            "role": "system",
            "content": (
                "You are the customer assistant for HYFUX MIXBAR. "
                "Always use your tools to retrieve real business information. "
                "When a customer asks what drinks are available, what is on "
                "the menu, or asks to see the menu, call get_products with "
                "orderable_only=true to retrieve actual products and prices. "
                "When a customer asks about product categories, call "
                "get_categories. "
                "When a customer searches for a specific product, call "
                "search_products. "
                "Never invent products, prices, ingredients, or availability. "
                "If information is missing, say you do not have it. "
                "Prices are in Algerian dinars (DZD). "
                "Be friendly and concise."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    while True:

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # If the AI does not request a tool, return its answer
        if not assistant_message.tool_calls:
            return assistant_message.content or "I couldn't generate an answer."

        # Add the assistant's tool requests to conversation history
        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        # Execute each requested function
        for tool_call in assistant_message.tool_calls:
              # Ignore custom tool calls; we only support function tools
            if tool_call.type != "function":
                continue
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"\n[Calling tool: {function_name}]")

            result = execute_tool(function_name, arguments)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })


# Run the assistant in the terminal
if __name__ == "__main__":

    print("HYFUX MIXBAR AI Assistant (Groq)")
    print("Type 'exit' to stop.\n")

    while True:

        question = input("You: ").strip()

        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        if not question:
            continue

        try:
            answer = ask_hyfux(question)
            print(f"\nHYFUX AI: {answer}\n")

        except Exception as error:
            print(f"\nError: {error}\n")
