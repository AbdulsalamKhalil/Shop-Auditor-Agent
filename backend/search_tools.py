import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

API_KEY = os.getenv("KEY_API_TAVILY")

if not API_KEY:
    raise ValueError("KEY_API_TAVILY is missing from the .env file.")

client = TavilyClient(api_key=API_KEY)


def stores_search(query: str, results_max: int = 5):
    try:
        response = client.search(
            query=query,
            max_results=results_max,
            search_depth="advanced"
        )

        results = []

        for result in response.get("results", []):
            results.append({
                "title": result.get("title", "غير متوفر"),
                "url": result.get("url", "غير متوفر"),
                "content": result.get("content", "غير متوفر")
            })

        return results

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    query = input("Enter search query: ").strip()

    if query:
        print(stores_search(query))
    else:
        print("Please enter a search query.")

