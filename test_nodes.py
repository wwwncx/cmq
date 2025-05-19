"""
测试Solana节点连接情况
"""

import asyncio
import aiohttp
import sys
import time

# 测试的节点列表
TEST_NODES = [
    {"name": "Solana官方主网", "url": "https://api.mainnet-beta.solana.com"},
    {"name": "Ankr公共节点", "url": "https://rpc.ankr.com/solana"},
    {"name": "ChainUp节点", "url": "https://solana.chainupcdn.com"},
    {"name": "Triton节点", "url": "https://rpc.triton.one:7000"},
    {"name": "GenesysGo节点", "url": "https://ssc-dao.genesysgo.net"},
    {"name": "Serum节点", "url": "https://solana-api.projectserum.com"}
]

# 测试超时设置(秒)
TIMEOUT = 10

async def test_node(session, node):
    """测试单个节点连接"""
    start_time = time.time()
    try:
        # 发送基本的JSON-RPC请求(getVersion)
        async with session.post(
            node["url"], 
            json={"jsonrpc": "2.0", "id": 1, "method": "getVersion"},
            timeout=TIMEOUT
        ) as response:
            elapsed = time.time() - start_time
            
            if response.status == 200:
                # 解析响应
                data = await response.json()
                if "result" in data:
                    return {
                        "success": True,
                        "node": node,
                        "status": response.status,
                        "result": data["result"],
                        "elapsed": elapsed
                    }
                else:
                    return {
                        "success": False,
                        "node": node,
                        "status": response.status,
                        "error": "无法获取响应结果",
                        "elapsed": elapsed
                    }
            else:
                return {
                    "success": False,
                    "node": node,
                    "status": response.status,
                    "error": f"HTTP状态码: {response.status}",
                    "elapsed": elapsed
                }
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        return {
            "success": False,
            "node": node,
            "error": f"连接超时 (>{TIMEOUT}秒)",
            "elapsed": elapsed
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "success": False,
            "node": node,
            "error": f"连接错误: {e}",
            "elapsed": elapsed
        }

async def test_slot(session, node):
    """测试获取当前slot(区块高度)"""
    try:
        # 发送请求获取当前slot
        async with session.post(
            node["url"], 
            json={"jsonrpc": "2.0", "id": 1, "method": "getSlot"},
            timeout=TIMEOUT
        ) as response:
            if response.status == 200:
                data = await response.json()
                if "result" in data:
                    return {"success": True, "slot": data["result"]}
            return {"success": False}
    except Exception:
        return {"success": False}

async def main():
    """主函数"""
    print("=" * 80)
    print(" Solana节点连接测试")
    print(" 测试您的网络环境能否连接到各个Solana节点")
    print("=" * 80)
    print()
    
    # 创建会话
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        # 测试所有节点
        tasks = [test_node(session, node) for node in TEST_NODES]
        results = await asyncio.gather(*tasks)
        
        # 显示结果
        successful_nodes = []
        print(f"测试结果 (超时设置: {TIMEOUT}秒):")
        print("-" * 80)
        print(f"{'节点名称':<20} {'连接状态':<10} {'响应时间':<10} {'详情'}")
        print("-" * 80)
        
        for result in results:
            node = result["node"]
            if result["success"]:
                status = "✅ 可连接"
                successful_nodes.append(node)
                details = f"Solana版本: {result['result'].get('solana-core', '未知')}"
            else:
                status = "❌ 不可连接"
                details = result.get("error", "未知错误")
            
            print(f"{node['name']:<20} {status:<10} {result['elapsed']:.2f}秒  {details}")
        
        # 测试slot
        if successful_nodes:
            print("\n获取区块高度测试:")
            print("-" * 80)
            for node in successful_nodes:
                try:
                    slot_result = await test_slot(session, node)
                    if slot_result["success"]:
                        print(f"{node['name']:<20} 当前slot: {slot_result['slot']}")
                    else:
                        print(f"{node['name']:<20} 无法获取slot")
                except Exception as e:
                    print(f"{node['name']:<20} 测试出错: {e}")
        
        # 给出建议
        print("\n推荐使用的节点:")
        if successful_nodes:
            # 按响应时间排序
            sorted_nodes = sorted(successful_nodes, key=lambda n: next((r["elapsed"] for r in results if r["node"] == n), float('inf')))
            
            for i, node in enumerate(sorted_nodes[:3]):
                elapsed = next((r["elapsed"] for r in results if r["node"] == node), 0)
                print(f"{i+1}. {node['name']} ({node['url']}) - 响应时间: {elapsed:.2f}秒")
                
            # 修改配置提示
            print("\n要在程序中使用这些节点，请修改app/core/config.py文件中的配置:")
            print(f"""
# Solana链配置
SOLANA_RPC_URL: str = "{sorted_nodes[0]['url']}"  # {sorted_nodes[0]['name']}
SOLANA_WS_URL: str = "{sorted_nodes[0]['url'].replace('https://', 'wss://')}"
            """)
        else:
            print("无法连接到任何Solana节点，请检查网络连接或尝试使用代理。")
            print("\n修改real_mode.py中的代理设置:")
            print("""
# 尝试使用代理连接
proxy = "http://127.0.0.1:7890"  # 修改为你的代理地址
solana_connection = get_solana_connection(proxy=proxy)
            """)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试出错: {e}")
        sys.exit(1) 