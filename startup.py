import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# 创建简单的FastAPI应用
app = FastAPI(title="Solana聪明钱包筛选器")

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """返回主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """返回仪表盘页面"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "smart_wallet_count": 10,
        "top_wallets": []
    })

if __name__ == "__main__":
    # 确保目录存在
    os.makedirs("app/data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 启动服务器
    uvicorn.run(app, host="127.0.0.1", port=9000) 