import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import os
api_key=os.getenv("GROQ_API_KEY")
client=Groq(api_key=api_key)
model="openai/gpt-oss-20b"
from search_tools import stores_search

system_prompt="""you are an AI product comparison assistant Search for the product requested by the user and compare it with similar products
based on price,quality,and the user’s preferences.
Identify the lowest price and highest quality options,and provide a clear comparison.
Do not make up any information."""

tools=[
    {
        "type":"function",
        "function":{
            "name":"stores_search",
            "description":(
                "Ai-powered product comparison agent that helps users find and compare similar products based on price,quality,ratings,and user prefernces"
            ),
            "parameters":{
                "type":"object",
                "properties":{
                    "query":{
                        "type":"string",
                        "description":"The product name to search for and compare prices on"
                    }
                },
                "required":["query"],
            },
        },     
    
    }
]
def run_agent(user_query: str) -> dict:
    if not user_query or not user_query.strip():
        return {"response": "Please enter a valid question.", "raw_data": []}

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    all_raw_results = []
    max_turns = 5

    try:
        for _ in range(max_turns):
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if not tool_calls:
                if not response_message.content:
                    return {"response": "Sorry, I received an empty response. Please try again.", "raw_data": all_raw_results}
                return {"response": response_message.content, "raw_data": all_raw_results}

            messages.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in tool_calls
                ]
            })

            for tool_call in tool_calls:
                function_args = json.loads(tool_call.function.arguments)
                result = stores_search(**function_args)
                all_raw_results.append(result)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

        return {"response": "Sorry, I couldn't reach a final answer.", "raw_data": all_raw_results}

    except Exception as e:
        return {"response": f"An error occurred while processing your request: {str(e)}", "raw_data": all_raw_results}

