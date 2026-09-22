import json
import re
from typing import Any, List
from pydantic import BaseModel, Field


class Product(BaseModel):
    title: str = Field(default="Not Available")
    price: str = Field(default="Not Available")
    currency: str = Field(default="EGP")
    store: str = Field(default="Not Available")
    rating: float = Field(default=0.0)
    image: str = Field(default="")
    specs: List[str] = Field(default_factory=list)
    link: str = Field(default="#")


class ParserOutput(BaseModel):
    status: str
    summary: str
    products: List[Product]


def clean_text(value: Any) -> str:
    if value is None:
        return "Not Available"

    text = str(value)
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return "Not Available"

    return text


def json_to_format(data_raw: Any) -> dict:
    try:
        if isinstance(data_raw, str):
            try:
                data_raw = json.loads(data_raw)
            except json.JSONDecodeError:
                data_raw = [{"content": data_raw}]

        if isinstance(data_raw, dict):
            if "products" in data_raw:
                raw_products = data_raw["products"]
            elif "results" in data_raw:
                raw_products = data_raw["results"]
            else:
                raw_products = [data_raw]
        elif isinstance(data_raw, list):
            raw_products = data_raw
        else:
            raw_products = []

        products = []

        for item in raw_products:
            if not isinstance(item, dict):
                continue

            title = clean_text(
                item.get("title")
                or item.get("name")
                or item.get("product_name")
            )

            price = clean_text(item.get("price"))
            currency = clean_text(item.get("currency") or "EGP")
            store = clean_text(
                item.get("store")
                or item.get("source")
                or item.get("domain")
            )
            
            # استخراج التقييم وتحويله لـ float
            raw_rating = item.get("rating", 0.0)
            try:
                rating = float(raw_rating)
            except (ValueError, TypeError):
                rating = 0.0

            image = clean_text(item.get("image") or item.get("img_url") or "")
            link = clean_text(item.get("link") or item.get("url") or "#")

            # تجميع المواصفات في قائمة specs
            specs = item.get("specs", [])
            if not isinstance(specs, list):
                specs = [str(specs)]
            
            # إضافة البطارية لـ specs لو كانت موجودة بشكل منفصل
            battery = item.get("battery") or item.get("battery_capacity")
            if battery and clean_text(battery) != "Not Available":
                specs.append(f"Battery: {clean_text(battery)}")

            product = Product(
                title=title,
                price=price,
                currency=currency,
                store=store,
                rating=rating,
                image=image,
                specs=specs,
                link=link
            )

            products.append(product)

        status = "success"
        summary = f"Found {len(products)} product(s) for comparison." if products else "No products were found."

        final_output = ParserOutput(
            status=status,
            summary=summary,
            products=products
        )

        return final_output.model_dump()

    except Exception as e:
        error_output = ParserOutput(
            status="error",
            summary=f"Data processing error: {str(e)}",
            products=[]
        )
        return error_output.model_dump()
