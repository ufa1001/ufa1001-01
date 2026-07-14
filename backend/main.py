"""
直播间智能分配系统 - 飞书多维表格 API 代理服务
提供 RESTful API，让前端应用实时读写飞书多维表格数据
"""
import os
import time
import httpx
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="直播间智能分配系统 API",
    description="飞书多维表格代理服务，支持7张表的实时CRUD操作",
    version="1.0.0"
)

# CORS 配置 - 允许所有前端来源访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 配置 ====================
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
BASE_TOKEN = os.getenv("BASE_TOKEN", "BLa2b1zJmaniVws3GhccrJfSnvc")

# 7张表的名称与ID映射（来自多维表格实际结构）
TABLE_MAP = {
    "直播间明细": "tblsnwgk4YwNZ6yU",
    "运营分析汇总": "tblC9Og3HqSJeB17",
    "运营巡检任务": "tblH49EgNnFrotqm",
    "项目进度总表": "tblm6NfVswtwYtfw",
    "新主播分配记录": "tbltH4UxFwRdJDKg",
    "主播-房间变更历史": "tblM0gAlALUpCH70",
    "百万独占动态规则": "tbl7uSOxbKwix8zt",
}

# Token 缓存（tenant_access_token 有效期约2小时）
_token_cache = {"token": None, "expire_at": 0}


# ==================== 飞书 API 封装 ====================
async def get_tenant_token() -> str:
    """获取飞书 tenant_access_token，带缓存机制"""
    now = time.time()
    if _token_cache["token"] and _token_cache["expire_at"] > now + 60:
        return _token_cache["token"]

    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        raise HTTPException(
            status_code=500,
            detail="未配置 FEISHU_APP_ID 或 FEISHU_APP_SECRET，请在 .env 文件中设置"
        )

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
            timeout=30
        )
        data = resp.json()
        if data.get("code") != 0:
            raise HTTPException(
                status_code=500,
                detail=f"飞书认证失败: {data.get('msg', '未知错误')}"
            )
        token = data["tenant_access_token"]
        expire = data.get("expire", 7200)
        _token_cache["token"] = token
        _token_cache["expire_at"] = now + expire
        return token


async def feishu_request(method: str, path: str, **kwargs) -> dict:
    """发送飞书 API 请求"""
    token = await get_tenant_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        url = f"https://open.feishu.cn/open-apis{path}"
        resp = await client.request(method, url, headers=headers, timeout=30, **kwargs)
        return resp.json()


# ==================== API 路由 ====================
@app.get("/api/health")
async def health_check():
    """健康检查 + 配置状态"""
    return {
        "status": "ok",
        "base_token": BASE_TOKEN,
        "app_id_configured": bool(FEISHU_APP_ID),
        "app_secret_configured": bool(FEISHU_APP_SECRET),
        "tables": list(TABLE_MAP.keys()),
    }


@app.get("/api/tables")
async def list_tables():
    """获取所有表的基本信息"""
    return {
        "tables": [
            {"name": name, "table_id": tid}
            for name, tid in TABLE_MAP.items()
        ]
    }


@app.get("/api/records/{table_name}")
async def list_records(table_name: str, page_size: int = 500):
    """
    获取指定表的所有记录（自动分页）
    示例: GET /api/records/直播间明细?page_size=500
    """
    table_id = TABLE_MAP.get(table_name)
    if not table_id:
        raise HTTPException(status_code=404, detail=f"表 '{table_name}' 不存在。可用表: {list(TABLE_MAP.keys())}")

    all_items = []
    page_token = None
    while True:
        params = {"page_size": min(page_size, 500)}
        if page_token:
            params["page_token"] = page_token

        result = await feishu_request(
            "GET",
            f"/bitable/v1/apps/{BASE_TOKEN}/tables/{table_id}/records",
            params=params
        )
        if result.get("code") != 0:
            raise HTTPException(status_code=500, detail=result)

        data = result.get("data", {})
        items = data.get("items", [])
        all_items.extend(items)

        if not data.get("has_more"):
            break
        page_token = data.get("page_token")

    return {
        "table": table_name,
        "table_id": table_id,
        "total": len(all_items),
        "items": all_items
    }


@app.post("/api/records/{table_name}")
async def create_record(table_name: str, fields: dict = Body(...)):
    """
    在指定表中创建新记录
    示例: POST /api/records/直播间明细
    Body: {"房间号": "A10-999", "位置": "临港", "状态": "空置", "设备": "单反"}
    """
    table_id = TABLE_MAP.get(table_name)
    if not table_id:
        raise HTTPException(status_code=404, detail=f"表 '{table_name}' 不存在")

    result = await feishu_request(
        "POST",
        f"/bitable/v1/apps/{BASE_TOKEN}/tables/{table_id}/records",
        json={"fields": fields}
    )
    if result.get("code") != 0:
        raise HTTPException(status_code=500, detail=result)
    return result.get("data", {})


@app.put("/api/records/{table_name}/{record_id}")
async def update_record(table_name: str, record_id: str, fields: dict = Body(...)):
    """
    更新指定记录
    示例: PUT /api/records/直播间明细/recXXXXXX
    Body: {"状态": "占满", "使用人1": "张三"}
    """
    table_id = TABLE_MAP.get(table_name)
    if not table_id:
        raise HTTPException(status_code=404, detail=f"表 '{table_name}' 不存在")

    result = await feishu_request(
        "PUT",
        f"/bitable/v1/apps/{BASE_TOKEN}/tables/{table_id}/records/{record_id}",
        json={"fields": fields}
    )
    if result.get("code") != 0:
        raise HTTPException(status_code=500, detail=result)
    return result.get("data", {})


@app.delete("/api/records/{table_name}/{record_id}")
async def delete_record(table_name: str, record_id: str):
    """
    删除指定记录
    示例: DELETE /api/records/直播间明细/recXXXXXX
    """
    table_id = TABLE_MAP.get(table_name)
    if not table_id:
        raise HTTPException(status_code=404, detail=f"表 '{table_name}' 不存在")

    result = await feishu_request(
        "DELETE",
        f"/bitable/v1/apps/{BASE_TOKEN}/tables/{table_id}/records/{record_id}"
    )
    if result.get("code") != 0:
        raise HTTPException(status_code=500, detail=result)
    return {"deleted": True, "record_id": record_id, "table": table_name}


@app.get("/api/records/{table_name}/{record_id}")
async def get_record(table_name: str, record_id: str):
    """
    获取单条记录详情
    示例: GET /api/records/直播间明细/recXXXXXX
    """
    table_id = TABLE_MAP.get(table_name)
    if not table_id:
        raise HTTPException(status_code=404, detail=f"表 '{table_name}' 不存在")

    result = await feishu_request(
        "GET",
        f"/bitable/v1/apps/{BASE_TOKEN}/tables/{table_id}/records/{record_id}"
    )
    if result.get("code") != 0:
        raise HTTPException(status_code=500, detail=result)
    return result.get("data", {})


# ==================== 启动 ====================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
