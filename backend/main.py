import base64
from typing import List, Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 1. استدعاء الـ Graph الخاص بالـ Agent من ملف agent_core.py
from agent_core import app_graph  

app = FastAPI(title="Shop Auditor Agent API")

# إعداد الـ CORS للتواصل مع الـ Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DealSchema(BaseModel):
    title: str
    price: str
    currency: str = "EGP"
    store: str
    rating: float
    image: str
    specs: List[str]
    link: str


@app.post("/api/audit", response_model=List[DealSchema])
async def audit_market(
    query: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    if not query and not image:
        raise HTTPException(
            status_code=400, 
            detail="يرجى إدخال نص للبحث أو إرفاق صورة للمنتج."
        )

    # 2. تجهيز الصورة وتحويلها إلى Base64 لو كان نموذج الـ Vision يحتاجها
    image_b64 = None
    if image:
        image_bytes = await image.read()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    try:
        # 3. بناء الـ Initial State الخاصة بـ LangGraph
        initial_state = {
            "query": query,
            "image_b64": image_b64,
            "deals": []
        }

        # 4. تشغيل الـ Graph بشكل Async
        final_state = await app_graph.ainvoke(initial_state)

        # 5. استخراج الصفقات المرتجعة من الـ State
        deals_result = final_state.get("deals", [])

        return deals_result

    except Exception as e:
        print(f"[ERROR] Exception during agent execution: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing agent pipeline: {str(e)}"
        )
