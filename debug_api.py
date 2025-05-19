import requests
import json
import time

# 测试不同的RPC节点
rpc_endpoints = [
    {
        "name": "官方节点",
        "url": "https://api.mainnet-beta.solana.com",
        "api_key": None
    },
    {
        "name": "Ankr公共节点",
        "url": "https://rpc.ankr.com/solana",
        "api_key": None
    },
    {
        "name": "GetBlock示例 (需要API密钥)",
        "url": "https://go.getblock.io/YOUR_API_KEY/solana/mainnet",
        "api_key": None  # 替换为你的API密钥
    }
]

def test_rpc_connection(endpoint):
    """测试RPC连接是否正常"""
    headers = {"Content-Type": "application/json"}
    if endpoint["api_key"]:
        headers["X-API-Key"] = endpoint["api_key"]
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getHealth"
    }
    
    print(f"\n测试节点: {endpoint['name']} ({endpoint['url']})")
    
    try:
        start_time = time.time()
        response = requests.post(endpoint["url"], headers=headers, json=payload, timeout=10)
        elapsed = time.time() - start_time
        
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {elapsed:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

def test_get_account(endpoint, address="vines1vzrYbzLMRdu58ou5XTby4qAqVRLmqo36NKPTg"):
    """测试获取帐户信息"""
    headers = {"Content-Type": "application/json"}
    if endpoint["api_key"]:
        headers["X-API-Key"] = endpoint["api_key"]
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [
            address,
            {"encoding": "jsonParsed"}
        ]
    }
    
    print(f"\n测试获取帐户信息: {address}")
    
    try:
        response = requests.post(endpoint["url"], headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result and result["result"] is not None:
                print("✅ 成功获取帐户信息")
                return True
            else:
                print(f"❌ 未能获取帐户信息: {json.dumps(result, ensure_ascii=False)}")
                return False
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False

# 开始测试
print("====== Solana RPC节点连接测试 ======")

working_endpoints = []

for endpoint in rpc_endpoints:
    if test_rpc_connection(endpoint):
        print("✅ 连接测试成功")
        working_endpoints.append(endpoint)
    else:
        print("❌ 连接测试失败")

# 测试获取帐户信息
if working_endpoints:
    print("\n\n====== 对连接成功的节点进行进一步测试 ======")
    best_endpoint = None
    
    for endpoint in working_endpoints:
        if test_get_account(endpoint):
            best_endpoint = endpoint
            break
    
    if best_endpoint:
        print(f"\n\n推荐使用的节点: {best_endpoint['name']} ({best_endpoint['url']})")
        print("请将此URL复制到app/core/config.py文件中的SOLANA_RPC_URL配置项")
    else:
        print("\n\n❌ 所有节点都无法获取帐户信息，建议:")
        print("1. 检查网络连接")
        print("2. 尝试使用代理")
        print("3. 申请付费RPC节点服务")
else:
    print("\n\n❌ 所有节点连接失败，建议:")
    print("1. 检查网络连接")
    print("2. 尝试使用代理")
    print("3. 申请付费RPC节点服务") 