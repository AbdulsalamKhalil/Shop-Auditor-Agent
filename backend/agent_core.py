import json
import os
from dotenv import load_dotenv
from groq import Groq
from search_tools import stores_search

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from the .env file.")

client = Groq(api_key=api_key)

system_prompt = """You are an expert AI E-Commerce Auditor & Product Comparison Agent specializing in real-time market search.

### PRIMARY GOAL:
Your sole objective is to discover, analyze, and compare live product deals, pricing, and specs across e-commerce platforms.

### STRICT OPERATIONAL RULES:
1. **Mandatory Tool Usage**: For ANY query involving products, prices, availability, or comparisons, you MUST call the `stores_search` tool immediately. NEVER rely on internal knowledge or construct fake product deals.
2. **Query Optimization**: Refine user queries into clean, highly effective search strings (e.g., include exact brand, model, capacity, or key specs).
3. **Zero Hallucination**: Use ONLY the raw context returned by `stores_search`. If no results are returned, explicitly report that no live deals were found instead of inventing placeholder products.
4. **Multi-Deal Retrieval**: Always attempt to retrieve multiple competing store listings (up to 5-8 deals) to enable objective price comparison."""

tools = [
    {
        "type": "function",
        "function": {
            "name": "stores_search",
            "description": "Search for e-commerce product listings, deals, prices, and specifications.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The product name to search for (e.g., Samsung Galaxy S25 Ultra)."
                    }
                },
                "required": ["query"],
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
                model="qwen/qwen3.8-27b",  # موديل مستقر وسريع ويدعم الأدوات على Groq
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # إذا لم يطلب الموديل استدعاء أي أداة إضافية، نقوم بإنهاء الدورة
            if not tool_calls:
                return {
                    "response": response_message.content or "Completed search.",
                    "raw_data": all_raw_results
                }

            # إضافة الاستجابة المباشرة إلى سجل الرسائل
            messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                if function_name == "stores_search":
                    function_args = json.loads(tool_call.function.arguments)
                    result = stores_search(**function_args)
                    
                    # تجميع النتائج الخام
                    if isinstance(result, list):
                        all_raw_results.extend(result)
                    else:
                        all_raw_results.append(result)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })

        return {"response": "Search completed.", "raw_data": all_raw_results}

    except Exception as e:
        print(f"[AGENT ERROR]: {str(e)}")
        return {"response": f"Error: {str(e)}", "raw_data": all_raw_results}
