import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

API_KEY = os.getenv("KEY_API_TAVILY")

if not API_KEY:
    raise ValueError("KEY_API_TAVILY is missing from the .env file.")

client = TavilyClient(api_key=API_KEY)


def stores_search(query: str, results_max: int = 6):
    try:
        # توجيه البحث تلقائياً لصفحات الشراء والمتاجر المباشرة
        store_query = f"{query} سعر شراء متجر مصر amazon.eg noon jumia btech"

        response = client.search(
            query=store_query,
            max_results=results_max,
            search_depth="advanced",
            include_images=True
        )

        results = []
        fetched_images = response.get("images", [])

        # صورة افتراضية عالية الجودة في حال عدم توفر صورة بالنتيجة
        default_img = "https://m.media-amazon.com/images/I/71WjsA0L7VL._AC_SL1500_.jpg"

        for idx, result in enumerate(response.get("results", [])):
            img = result.get("image") or result.get("primary_image")
            if not img and idx < len(fetched_images):
                img_item = fetched_images[idx]
                img = img_item if isinstance(img_item, str) else img_item.get("url")

            if not img:
                img = default_img

            results.append({
                "title": result.get("title", "غير متوفر"),
                "url": result.get("url", "#"),
                "content": result.get("content", ""),
                "image": img
            })

        return results

    except Exception as e:
        print(f"[SEARCH ERROR]: {str(e)}")
        return []


if __name__ == "__main__":
    query = input("Enter search query: ").strip()
    if query:
        print(stores_search(query))
    else:
        print("Please enter a search query.")
