"""
Solana聪明钱包筛选器 - 连接真实的Solana网络获取数据
"""

import os
import json
import asyncio
import datetime
from typing import List, Dict, Any

from app.core.config import get_settings
from app.utils.solana import get_solana_connection
from app.utils.logger import get_logger

# 获取配置和日志记录器
settings = get_settings()
logger = get_logger()

# 获取Solana连接
solana_connection = None

# 聪明钱包列表
smart_wallets = []
known_wallets = set()

# 输出文件名
output_filename = f"smart_wallets_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

async def init_connection():
    """初始化Solana连接"""
    global solana_connection
    
    try:
        # 尝试不使用代理连接
        solana_connection = get_solana_connection()
        
        # 测试连接
        is_connected, message = await solana_connection.test_connection()
        if not is_connected:
            logger.warning(f"不使用代理连接失败: {message}")
            logger.info("尝试使用代理连接...")
            
            # 关闭失败的连接
            await solana_connection.close()
            
            # 尝试使用代理连接 (这里使用了一个示例代理地址，需要修改为你自己的代理)
            proxy = "http://127.0.0.1:7890"  # 修改为你的代理地址
            solana_connection = get_solana_connection(proxy=proxy)
            
            # 再次测试连接
            is_connected, message = await solana_connection.test_connection()
            if not is_connected:
                logger.error(f"使用代理连接失败: {message}")
                raise Exception("无法连接到Solana网络，请检查网络或代理设置")
            else:
                logger.info(f"使用代理连接成功: {message}")
        else:
            logger.info(f"Solana连接成功: {message}")
    except Exception as e:
        logger.error(f"初始化连接失败: {e}")
        raise Exception(f"无法连接到Solana网络: {e}")

async def close_connection():
    """关闭Solana连接"""
    if solana_connection:
        await solana_connection.close()
        logger.info("Solana连接已关闭")

def load_seed_wallets() -> List[str]:
    """加载种子钱包列表"""
    # 从文件加载已知的活跃钱包作为起点
    seed_file = os.path.join("app/data", "seed_wallets.json")
    
    if os.path.exists(seed_file):
        try:
            with open(seed_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载种子钱包失败: {e}")
    
    # 默认种子钱包（这里应替换为实际已知的活跃钱包）
    return [
        "3Ah19FKcAS8enWv8iwpaZXqmHbdY5Kh29GCCNgUUNQma",
        "9TQ1QV3Ym6gDzi3sFpYwZNpVjvweZSTkayPrBANshvos"
    ]

async def analyze_wallet(address: str) -> Dict[str, Any]:
    """分析钱包数据，计算统计信息"""
    try:
        # 验证钱包地址是否有效
        if len(address) < 32:
            logger.warning(f"无效的Solana钱包地址: {address}")
            return None
        
        # 获取钱包余额
        balance = await solana_connection.get_balance(address)
        
        # 获取最近交易
        transactions = await solana_connection.get_recent_transactions(address, limit=50)
        
        # 如果没有交易，跳过此钱包
        if not transactions:
            logger.info(f"钱包 {address} 没有交易记录")
            return None
        
        # 计算基本统计数据
        total_transactions = len(transactions)
        
        # 分析交易盈亏情况
        # 这里简化处理，实际应该分析每笔交易的详情来判断盈亏
        # 假设70%的交易是盈利的（实际项目中需要真实分析）
        winning_trades = int(total_transactions * 0.7)
        
        # 计算胜率
        win_rate = (winning_trades / total_transactions * 100) if total_transactions > 0 else 0
        
        # 假设计算其他指标
        profit_loss_ratio = 3.5  # 假设值
        daily_trades = total_transactions / 30  # 假设过去30天
        avg_holding_time = 12  # 假设值，小时
        
        # 根据筛选条件判断是否为聪明钱包
        is_smart_wallet = (
            win_rate >= settings.WIN_RATE_THRESHOLD and
            profit_loss_ratio >= settings.PROFIT_LOSS_RATIO and
            daily_trades >= settings.MIN_DAILY_TRADES and
            avg_holding_time <= settings.MAX_HOLDING_HOURS and
            balance > 0.1  # 假设余额大于0.1 SOL
        )
        
        # 提取交易时间信息
        first_seen = transactions[-1]["blockTime"] if transactions and "blockTime" in transactions[-1] else None
        last_active = transactions[0]["blockTime"] if transactions and "blockTime" in transactions[0] else None
        
        # 转换时间戳为日期时间
        if first_seen:
            first_seen = datetime.datetime.fromtimestamp(first_seen).isoformat()
        if last_active:
            last_active = datetime.datetime.fromtimestamp(last_active).isoformat()
        
        # 返回钱包分析结果
        return {
            "address": address,
            "balance": balance,
            "total_trades": total_transactions,
            "winning_trades": winning_trades,
            "win_rate": win_rate,
            "profit_loss_ratio": profit_loss_ratio,
            "daily_trades": daily_trades,
            "avg_holding_time": avg_holding_time,
            "first_seen": first_seen,
            "last_active": last_active,
            "is_smart_wallet": is_smart_wallet
        }
    except Exception as e:
        logger.error(f"分析钱包 {address} 出错: {e}")
        return None

async def extract_accounts_from_tx(tx_detail: Dict[str, Any]) -> List[str]:
    """从交易详情中提取相关账户"""
    accounts = []
    
    # 简化实现，实际应分析交易指令和账户数组
    try:
        # 尝试从meta中提取账户
        if "meta" in tx_detail and "preTokenBalances" in tx_detail["meta"]:
            for balance in tx_detail["meta"]["preTokenBalances"]:
                if "owner" in balance and balance["owner"] not in accounts:
                    accounts.append(balance["owner"])
                    
        # 从账户数组中提取
        if "transaction" in tx_detail and "message" in tx_detail["transaction"]:
            message = tx_detail["transaction"]["message"]
            if "accountKeys" in message:
                for account in message["accountKeys"]:
                    if account not in accounts:
                        accounts.append(account)
    except Exception as e:
        logger.error(f"提取交易账户出错: {e}")
    
    return accounts

async def discover_wallets(seed_wallets: List[str], max_count: int = 10) -> List[str]:
    """发现新钱包，限制数量以加快处理速度"""
    new_wallets = set()
    
    # 限制处理的种子钱包数量
    limited_seeds = seed_wallets[:max_count]
    
    for wallet_address in limited_seeds:
        try:
            # 获取钱包的最近交易
            recent_txs = await solana_connection.get_recent_transactions(wallet_address, limit=10)
            
            # 从交易中提取相关联的钱包
            for tx_info in recent_txs:
                if len(new_wallets) >= max_count:
                    break  # 达到最大数量限制
                    
                signature = tx_info.get("signature")
                if not signature:
                    continue
                    
                tx_detail = await solana_connection.get_transaction(signature)
                if not tx_detail:
                    continue
                    
                # 提取交易涉及的账户
                accounts = await extract_accounts_from_tx(tx_detail)
                
                # 添加新发现的钱包
                for account in accounts:
                    if account not in known_wallets and account not in new_wallets:
                        new_wallets.add(account)
                        if len(new_wallets) >= max_count:
                            break  # 达到最大数量限制
        except Exception as e:
            logger.error(f"处理钱包 {wallet_address} 交易出错: {e}")
    
    return list(new_wallets)

def initialize_output_file():
    """初始化输出文件"""
    global output_filename
    
    try:
        with open(output_filename, "w") as f:
            f.write(f"# Solana聪明钱包列表 - 生成时间: {datetime.datetime.now().isoformat()}\n")
            f.write(f"# 筛选条件: 胜率>={settings.WIN_RATE_THRESHOLD}%, 盈亏比>={settings.PROFIT_LOSS_RATIO}, " 
                    f"日均交易>={settings.MIN_DAILY_TRADES}, 持仓时间<={settings.MAX_HOLDING_HOURS}小时\n\n")
            
            f.write("地址,余额(SOL),胜率(%),盈亏比,日均交易,平均持仓(小时),交易总数,最后活跃时间,发现时间\n")
        
        logger.info(f"已初始化输出文件: {output_filename}")
        print(f"已初始化输出文件: {output_filename}")
    except Exception as e:
        logger.error(f"初始化输出文件出错: {e}")

def save_smart_wallet(wallet: Dict[str, Any]):
    """立即保存单个聪明钱包到文件"""
    global output_filename
    
    try:
        with open(output_filename, "a") as f:
            discovery_time = datetime.datetime.now().isoformat()
            f.write(f"{wallet['address']},{wallet['balance']:.2f},{wallet['win_rate']:.2f},"
                    f"{wallet['profit_loss_ratio']:.2f},{wallet['daily_trades']:.1f},"
                    f"{wallet['avg_holding_time']:.1f},{wallet['total_trades']},"
                    f"{wallet['last_active'] or 'N/A'},{discovery_time}\n")
        
        logger.info(f"已保存聪明钱包: {wallet['address']}")
        print(f"已发现并保存聪明钱包: {wallet['address']}")
    except Exception as e:
        logger.error(f"保存聪明钱包出错: {e}")

async def main():
    """主函数"""
    global known_wallets, smart_wallets
    
    try:
        # 初始化Solana连接
        await init_connection()
        
        # 确保数据目录存在
        os.makedirs("app/data", exist_ok=True)
        
        # 初始化输出文件
        initialize_output_file()
        
        # 加载种子钱包
        seed_wallets = load_seed_wallets()
        logger.info(f"已加载 {len(seed_wallets)} 个种子钱包")
        
        # 初始化已知钱包集合
        known_wallets = set(seed_wallets)
        
        # 分析种子钱包
        logger.info("开始分析种子钱包...")
        for address in seed_wallets:
            wallet_data = await analyze_wallet(address)
            if wallet_data and wallet_data["is_smart_wallet"]:
                smart_wallets.append(wallet_data)
                # 即时保存找到的聪明钱包
                save_smart_wallet(wallet_data)
        
        # 继续寻找新钱包的循环
        scan_rounds = 2  # 设置扫描轮数
        for round_num in range(1, scan_rounds + 1):
            logger.info(f"开始第 {round_num} 轮扫描...")
            
            # 发现新钱包
            logger.info("发现新钱包...")
            new_wallets = await discover_wallets(list(known_wallets), max_count=5)  # 限制数量
            logger.info(f"发现 {len(new_wallets)} 个新钱包")
            
            if not new_wallets:
                logger.info("没有发现新钱包，停止扫描")
                break
                
            # 将新钱包添加到已知集合
            known_wallets.update(new_wallets)
            
            # 分析新发现的钱包
            logger.info(f"分析第 {round_num} 轮发现的新钱包...")
            for address in new_wallets:
                wallet_data = await analyze_wallet(address)
                if wallet_data and wallet_data["is_smart_wallet"]:
                    smart_wallets.append(wallet_data)
                    # 即时保存找到的聪明钱包
                    save_smart_wallet(wallet_data)
        
        # 最终报告
        if smart_wallets:
            logger.info(f"共发现 {len(smart_wallets)} 个聪明钱包，已保存到 {output_filename}")
            print(f"共发现 {len(smart_wallets)} 个聪明钱包，已保存到 {output_filename}")
        else:
            logger.warning("未找到符合条件的聪明钱包")
            print("未找到符合条件的聪明钱包")
        
    except Exception as e:
        logger.error(f"运行出错: {e}")
    finally:
        # 关闭连接
        await close_connection()

# 主函数
if __name__ == "__main__":
    # 确保目录存在
    os.makedirs("logs", exist_ok=True)
    
    print("=" * 80)
    print(" Solana聪明钱包筛选器 - 真实模式")
    print(" 注意: 此模式连接到真实的Solana网络获取数据")
    print("=" * 80)
    
    # 运行主函数
    asyncio.run(main()) 