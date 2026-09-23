import json
import os
from typing import Any, List
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field, field_validator

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is missing from the .env file.")

client = Groq(api_key=api_key)


class Product(BaseModel):
    title: str = Field(default="Not Available")
    price: str = Field(default="Not Available")
    currency: str = Field(default="EGP")
    store: str = Field(default="Not Available")
    rating: float = Field(default=4.2)
    image: str = Field(default="")
    specs: List[str] = Field(default_factory=list)
    link: str = Field(default="#")

    @field_validator("rating", mode="before")
    @classmethod
    def validate_rating(cls, v):
        if v is None or v == "N/A":
            return 4.2
        try:
            return float(v)
        except (ValueError, TypeError):
            return 4.2


class ParserOutput(BaseModel):
    status: str
    summary: str
    products: List[Product]


def json_to_format(data_raw: Any) -> dict:
    if not data_raw:
        return ParserOutput(
            status="success", summary="No products were found.", products=[]
        ).model_dump()

    cleaned_raw = []
    if isinstance(data_raw, list):
        for item in data_raw[:6]:
            if isinstance(item, dict):
                cleaned_raw.append(
                    {
                        "title": str(item.get("title", ""))[:120],
                        "content": str(item.get("content", ""))[:250],
                        "url": item.get("url", "#"),
                        "image": item.get("image", ""),
                    }
                )

    if not cleaned_raw:
        return ParserOutput(
            status="success", summary="No raw search results to parse.", products=[]
        ).model_dump()

    prompt = f"""
    You are a precise Data Extraction Engine for e-commerce products.
    Parse the following raw web search data and extract product deals into JSON format.

    Raw Search Data:
    {json.dumps(cleaned_raw, ensure_ascii=False)}

    Strict Rules:
    1. "title": Clean product name only.
    2. "price": Extract numerical value (e.g., "84,422.00"). If missing, set "Not Available".
    3. "currency": Always "EGP".
    4. "store": Marketplace name (e.g., "Amazon.eg", "Jumia", "Noon").
    5. "rating": Number out of 5.0 (default to 4.2 if unknown).
    6. "specs": Array of uppercase feature tags (e.g., ["256GB", "5G"]).
    7. "image": Valid direct product image URL.
    8. "link": Product web link.

    Return ONLY a JSON object with this exact structure:
    {{
        "products": [
            {{
                "title": "Product Name",
                "price": "50,000.00",
                "currency": "EGP",
                "store": "Amazon.eg",
                "rating": 4.5,
                "specs": ["256GB", "BLACK"],
                "image": "https://...",
                "link": "https://..."
            }}
        ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",  # موديل خفيف ومستقر جداً مع الـ JSON
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON generator. You must response ONLY in valid JSON format.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=2048,
        )

        parsed_json = json.loads(response.choices[0].message.content)
        raw_products = parsed_json.get("products", [])

        products_list = [Product(**item) for item in raw_products]

        return ParserOutput(
            status="success",
            summary=f"Found {len(products_list)} deal(s) for comparison.",
            products=products_list,
        ).model_dump()

    except Exception as e:
        print(f"[PARSER ERROR]: {e}")
        return ParserOutput(
            status="error",
            summary=f"Data processing error: {str(e)}",
            products=[],
        ).model_dump()
