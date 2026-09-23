from typing import Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from agent_core import run_agent
from data_parser import json_to_format

app = FastAPI(title="Shop Auditor Agent API")

# إعدادات CORS لضمان اتصال الفرونت إند بالسيرفر بدون أي محاذاة أخطاء
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Shop Auditor Agent API is running successfully!"}


@app.post("/api/audit")
async def audit_market(
    query: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    if not query and not image:
        raise HTTPException(
            status_code=400, 
            detail="يرجى إدخال نص للبحث أو إرفاق صورة للمنتج."
        )

    search_query = query.strip() if query and query.strip() else "Samsung Galaxy S25 Ultra"

    try:
        # 1. تشغيل الـ Agent لتنفيذ البحث
        agent_result = run_agent(search_query)
        raw_results = agent_result.get("raw_data", [])

        # 2. تحليل النتائج وتنظيفها عبر data_parser المحدث
        if raw_results:
            parsed = json_to_format(raw_results)
            formatted_products = parsed.get("products", [])
            if formatted_products:
                return formatted_products

        # 3. إرجاع نتيجة افتراضية منسقة في حال عدم العثور على صفقات حقيقية
        # return [{
        #     "title": "Samsung Galaxy S25 Ultra",
        #     "price": "61,999.00",
        #     "currency": "EGP",
        #     "store": "Amazon.eg",
        #     "rating": 4.2,
        #     "specs": ["SILVER", "12GB RAM", "512GB", "AI", "S Pen"],
        #     "image": "https://m.media-amazon.com/images/I/71WjsA0L7VL._AC_SL1500_.jpg",
        #     "link": "#"
        # }]
    
        return [{
                "title": "title",
                "price": "***,***.**",
                "currency": "EGP",
                "store": "store",
                "rating": "**.**",
                "specs": ["1", "2", "3", "4", "5"],
                "image": "image_url",
                "link": "#"
            }]

    except Exception as e:
        print(f"[MAIN API ERROR]: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
