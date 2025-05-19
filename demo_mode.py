"""
演示模式 - 使用模拟数据，无需连接到Solana网络
"""

import os
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import get_settings
from app.services.mock_service import get_mock_service

# 获取配置
settings = get_settings()

# 创建FastAPI应用
app = FastAPI(title="Solana聪明钱包筛选器 (演示模式)")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="app/templates")

# 获取模拟数据服务
mock_service = get_mock_service()

# 首页
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """返回主页"""
    return templates.TemplateResponse("index.html", {"request": request})

# 仪表盘
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """返回仪表盘页面"""
    stats = mock_service.get_wallet_stats()
    top_wallets = mock_service.get_wallets(smart_only=True, limit=10)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "smart_wallet_count": stats["smart_wallet_count"],
        "top_wallets": top_wallets
    })

# 钱包详情
@app.get("/wallet/{address}", response_class=HTMLResponse)
async def wallet_detail(address: str, request: Request):
    """展示钱包详情页面"""
    wallet = mock_service.get_wallet_by_address(address)
    if not wallet:
        return templates.TemplateResponse("error.html", {
            "request": request, 
            "error": "钱包未找到",
            "details": f"地址 {address} 不存在或无法访问"
        }, status_code=404)
        
    return templates.TemplateResponse("wallet_detail.html", {
        "request": request, 
        "wallet": wallet
    })

# API端点 - 获取钱包列表
@app.get("/api/wallets", response_class=JSONResponse)
async def api_get_wallets(smart_only: bool = False, limit: int = 100, offset: int = 0):
    """获取钱包列表"""
    wallets = mock_service.get_wallets(smart_only=smart_only, limit=limit, offset=offset)
    return wallets

# API端点 - 获取钱包统计信息
@app.get("/api/wallets/stats/overview", response_class=JSONResponse)
async def api_get_wallet_stats():
    """获取钱包统计信息"""
    return mock_service.get_wallet_stats()

# API端点 - 获取交易列表
@app.get("/api/transactions", response_class=JSONResponse)
async def api_get_transactions(wallet_address: str = None, limit: int = 100, offset: int = 0):
    """获取交易列表"""
    transactions = mock_service.get_transactions(wallet_address=wallet_address, limit=limit, offset=offset)
    return transactions

# API端点 - 模拟获取钱包持仓数据
@app.get("/api/transactions/wallet/{address}/positions", response_class=JSONResponse)
async def api_get_wallet_positions(address: str, active_only: bool = False):
    """模拟获取钱包持仓数据"""
    # 这里只是简单模拟一些持仓数据
    positions = []
    tokens = ["SOL", "USDC", "BONK", "JTO", "RAY"]
    
    for token in tokens:
        is_active = bool(round(max(0.2, min(0.8, os.urandom(1)[0] / 255))))
        if active_only and not is_active:
            continue
            
        positions.append({
            "token_symbol": token,
            "amount": round(os.urandom(1)[0] / 255 * 1000, 2),
            "avg_buy_price": round(os.urandom(1)[0] / 255 * 10, 4),
            "cost_basis": round(os.urandom(1)[0] / 255 * 50, 4),
            "buy_count": os.urandom(1)[0] % 20 + 1,
            "sell_count": os.urandom(1)[0] % 10,
            "realized_profit": round(os.urandom(1)[0] / 255 * 5, 4),
            "avg_holding_time": round(os.urandom(1)[0] / 255 * 24, 1),
            "is_active": is_active
        })
    
    return positions

# 主函数
if __name__ == "__main__":
    # 确保目录存在
    os.makedirs("app/data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print("=" * 80)
    print(" Solana聪明钱包筛选器 - 演示模式")
    print(" 注意: 此模式使用模拟数据，不连接到Solana网络")
    print("=" * 80)
    
    # 启动服务器
    uvicorn.run(app, host="127.0.0.1", port=9000) 