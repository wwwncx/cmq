"""
Solana链聪明钱包筛选机器人

筛选标准:
- 胜率阈值：筛选近30天交易胜率≥70%的地址
- 盈亏比优化：要求平均盈利/亏损比≥3:1
- 交易频次：日均交易次数≥20次
- 持仓周期：单币种持仓时间≤24小时
"""

import os
import asyncio
import uvicorn
from dotenv import load_dotenv

from app.core.config import get_settings
from app.api.server import app
from app.services.wallet_scanner import start_scanner
from app.core.database import init_db
from app.utils.logger import get_logger

# 加载环境变量
load_dotenv()

# 获取日志记录器
logger = get_logger()

# 获取设置
settings = get_settings()

# 确保数据目录存在
os.makedirs(settings.DATA_DIR, exist_ok=True)

# 初始化数据库
init_db()

# 启动钱包扫描器
@app.on_event("startup")
async def startup_scanner():
    """应用启动时启动钱包扫描器"""
    asyncio.create_task(start_scanner())
    logger.info("钱包扫描器后台任务已启动")

@app.on_event("shutdown")
async def shutdown():
    """应用关闭时的清理操作"""
    # 关闭连接等操作
    logger.info("应用关闭，执行清理操作")

if __name__ == "__main__":
    # 启动Web服务器
    logger.info(f"启动Web服务器，监听地址: {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 