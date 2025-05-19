# Solana RPC节点连接指南 (中国大陆用户)

## 问题解决

如果你在运行程序时遇到"获取数据失败"的错误，这很可能是由于Solana RPC节点连接问题导致的。这个指南将帮助你选择合适的RPC节点并解决连接问题。

## 测试你的连接

我们提供了一个简单的测试脚本 `debug_api.py` 来检查不同Solana RPC节点的连接状态：

```bash
# 运行测试脚本
python debug_api.py
```

如果所有默认节点都无法连接，你需要使用可在中国大陆访问的节点，通常需要API密钥。

## 获取RPC节点API密钥

以下是几个可用于中国大陆的Solana RPC服务提供商及获取API密钥的步骤：

### 1. GetBlock

1. 访问 https://getblock.io/ 并注册账号
2. 注册完成后，进入控制面板
3. 点击"Add API key"，选择Solana作为区块链
4. 创建完成后，你将得到类似 `https://go.getblock.io/YOUR_API_KEY/` 格式的URL
5. 将你的API密钥复制到 `debug_api.py` 中的相应位置

### 2. NOWNodes

1. 访问 https://nownodes.io/ 并注册账号
2. 注册完成后，进入控制面板
3. 点击"Create API key"，然后添加Solana节点
4. 创建完成后，你将获得API密钥
5. 完整URL格式为 `https://solana.nownodes.io/API_KEY`

### 3. 付费使用Chainstack

1. 访问 https://chainstack.com/ 并注册账号
2. 创建一个项目，然后添加Solana节点
3. 选择共享节点计划或专用节点计划
4. 获取API端点URL

## 配置你的应用

获取API密钥后，你需要更新配置文件：

1. 打开 `app/core/config.py` 文件
2. 修改RPC URL配置：

```python
# Solana链配置
SOLANA_RPC_URL: str = "https://go.getblock.io/YOUR_API_KEY/solana/mainnet"  # 替换为你的API URL
SOLANA_WS_URL: str = "wss://go.getblock.io/YOUR_API_KEY/solana/mainnet"  # WebSocket URL
```

## 使用代理解决方案

如果你无法获取API密钥或仍然无法连接，可以考虑使用代理连接官方节点：

1. 设置本地HTTP代理
2. 修改 `app/utils/solana.py` 文件，添加代理支持：

```python
def __init__(self, rpc_url=None, ws_url=None):
    """初始化Solana连接"""
    self.rpc_url = rpc_url or settings.SOLANA_RPC_URL
    self.ws_url = ws_url or settings.SOLANA_WS_URL
    # 添加代理支持
    self.client = AsyncClient(
        self.rpc_url, 
        # 取消注释下面一行并设置你的代理地址
        # connector=aiohttp.TCPConnector(ssl=False),
        # proxy="http://your-proxy-address:port"
    )
    self.session = None
    logger.info(f"初始化Solana连接: {self.rpc_url}")
```

## 自建节点方案

如果你需要更稳定和可靠的服务，可以考虑自建Solana RPC节点。自建节点需要较高配置的服务器以及技术支持，但能够提供最佳的性能和稳定性。

## 支持的免费RPC节点列表

以下是一些可能在中国大陆工作的公共节点，但可能有速率限制：

1. Ankr: `https://rpc.ankr.com/solana` (可能需要API密钥)
2. GetBlock: `https://go.getblock.io/[YOUR_API_KEY]/solana/mainnet`
3. NOWNodes: `https://solana.nownodes.io/[YOUR_API_KEY]`

始终检查最新的可用性，因为这些服务可能随时变化。 