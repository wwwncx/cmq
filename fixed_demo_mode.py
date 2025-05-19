"""
演示模式 - 使用模拟数据，无需连接到Solana网络
"""

import os
import random
import datetime
import json
from typing import List, Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# 创建FastAPI应用
app = FastAPI(title="Solana聪明钱包筛选器 (演示模式)")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="app/templates")

# 筛选参数设置
class Settings:
    # 筛选条件配置
    WIN_RATE_THRESHOLD: float = 70.0  # 胜率阈值 (%)
    PROFIT_LOSS_RATIO: float = 3.0    # 盈亏比
    MIN_DAILY_TRADES: float = 20.0    # 最小日交易量
    MAX_HOLDING_HOURS: float = 24.0   # 最大持仓时间 (小时)
    
    # 数据存储配置
    DATA_DIR: str = "app/data"        # 数据存储目录

settings = Settings()

class MockDataService:
    """模拟数据服务 - 生成假数据用于测试和演示"""
    
    def __init__(self):
        self.wallets = []
        self.transactions = []
        self._load_or_generate_data()
    
    def _load_or_generate_data(self):
        """加载或生成模拟数据"""
        mock_data_file = os.path.join(settings.DATA_DIR, "mock_data.json")
        
        if os.path.exists(mock_data_file):
            try:
                with open(mock_data_file, "r") as f:
                    data = json.load(f)
                    self.wallets = data.get("wallets", [])
                    self.transactions = data.get("transactions", [])
                return
            except Exception:
                pass
        
        # 生成模拟钱包数据
        self._generate_mock_wallets(50)
        self._generate_mock_transactions()
        
        # 保存模拟数据到文件
        os.makedirs(os.path.dirname(mock_data_file), exist_ok=True)
        try:
            with open(mock_data_file, "w") as f:
                json.dump({
                    "wallets": self.wallets,
                    "transactions": self.transactions
                }, f, indent=2)
        except Exception:
            pass
    
    def _generate_mock_wallets(self, count: int):
        """生成模拟钱包数据"""
        for i in range(count):
            # 生成Solana风格的随机地址
            address = ''.join(random.choices('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz', k=44))
            
            # 模拟钱包统计数据
            win_rate = random.uniform(30, 95)
            profit_loss_ratio = random.uniform(0.5, 8.0)
            daily_trades = random.uniform(5, 50)
            avg_holding_time = random.uniform(2, 48)
            
            # 根据筛选条件设置是否为聪明钱包
            is_smart_wallet = (
                win_rate >= settings.WIN_RATE_THRESHOLD and
                profit_loss_ratio >= settings.PROFIT_LOSS_RATIO and
                daily_trades >= settings.MIN_DAILY_TRADES and
                avg_holding_time <= settings.MAX_HOLDING_HOURS
            )
            
            wallet = {
                "address": address,
                "balance": round(random.uniform(0.1, 100), 4),
                "total_trades": random.randint(50, 500),
                "winning_trades": int(win_rate / 100 * random.randint(50, 500)),
                "win_rate": win_rate,
                "total_profit": round(random.uniform(1, 50), 4),
                "total_loss": round(random.uniform(0.1, 10), 4),
                "profit_loss_ratio": profit_loss_ratio,
                "avg_profit_per_trade": round(random.uniform(0.01, 0.5), 4),
                "daily_trades": daily_trades,
                "avg_holding_time": avg_holding_time,
                "first_seen": (datetime.datetime.now() - datetime.timedelta(days=random.randint(30, 180))).isoformat(),
                "last_active": (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 10))).isoformat(),
                "last_updated": datetime.datetime.now().isoformat(),
                "is_smart_wallet": is_smart_wallet
            }
            
            self.wallets.append(wallet)
    
    def _generate_mock_transactions(self):
        """为每个钱包生成模拟交易数据"""
        for wallet in self.wallets:
            # 为每个钱包生成10-50笔交易
            tx_count = random.randint(10, 50)
            for i in range(tx_count):
                # 模拟交易类型
                tx_type = random.choice(["buy", "sell", "swap", "transfer"])
                
                # 模拟代币符号
                token_symbol = random.choice(["SOL", "USDC", "BONK", "JTO", "RAY", "SRM", "FIDA", "MNGO"])
                
                # 模拟交易数量
                amount = round(random.uniform(1, 1000), 2)
                
                # 模拟交易价值
                value_in_sol = round(random.uniform(0.1, 10), 4)
                
                # 模拟盈亏
                is_profitable = random.random() > 0.3  # 70%概率盈利
                profit_loss = round(random.uniform(0.01, 2), 4) if is_profitable else round(random.uniform(-1, -0.01), 4)
                
                # 模拟交易哈希
                signature = ''.join(random.choices('0123456789abcdef', k=64))
                
                # 模拟交易时间
                timestamp = (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))).isoformat()
                
                transaction = {
                    "wallet_address": wallet["address"],
                    "signature": signature,
                    "tx_type": tx_type,
                    "token_symbol": token_symbol,
                    "amount": amount,
                    "value_in_sol": value_in_sol,
                    "profit_loss": profit_loss,
                    "is_profitable": is_profitable,
                    "timestamp": timestamp
                }
                
                self.transactions.append(transaction)
    
    def get_wallets(self, smart_only: bool = False, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取钱包列表"""
        filtered_wallets = [w for w in self.wallets if not smart_only or w["is_smart_wallet"]]
        return filtered_wallets[offset:offset+limit]
    
    def get_wallet_by_address(self, address: str) -> Optional[Dict[str, Any]]:
        """根据地址获取钱包信息"""
        for wallet in self.wallets:
            if wallet["address"] == address:
                return wallet
        return None
    
    def get_transactions(self, wallet_address: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取交易列表"""
        if wallet_address:
            filtered_txs = [tx for tx in self.transactions if tx["wallet_address"] == wallet_address]
        else:
            filtered_txs = self.transactions
        
        return filtered_txs[offset:offset+limit]
    
    def get_wallet_stats(self) -> Dict[str, Any]:
        """获取钱包统计信息"""
        smart_wallets = [w for w in self.wallets if w["is_smart_wallet"]]
        
        return {
            "total_wallets": len(self.wallets),
            "smart_wallet_count": len(smart_wallets),
            "avg_win_rate": sum(w["win_rate"] for w in smart_wallets) / len(smart_wallets) if smart_wallets else 0,
            "avg_profit_loss_ratio": sum(w["profit_loss_ratio"] for w in smart_wallets) / len(smart_wallets) if smart_wallets else 0,
            "avg_daily_trades": sum(w["daily_trades"] for w in smart_wallets) / len(smart_wallets) if smart_wallets else 0
        }

# 创建模拟数据服务实例
mock_service = MockDataService()

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
        is_active = bool(round(max(0.2, min(0.8, random.random()))))
        if active_only and not is_active:
            continue
            
        positions.append({
            "token_symbol": token,
            "amount": round(random.random() * 1000, 2),
            "avg_buy_price": round(random.random() * 10, 4),
            "cost_basis": round(random.random() * 50, 4),
            "buy_count": random.randint(1, 20),
            "sell_count": random.randint(0, 10),
            "realized_profit": round(random.random() * 5, 4),
            "avg_holding_time": round(random.random() * 24, 1),
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