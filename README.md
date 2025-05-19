# Solana聪明钱包筛选器

这是一个自动发现并保存Solana区块链上"聪明钱包"的工具。程序会连接到真实的Solana区块链网络，分析钱包行为，并将符合条件的"聪明钱包"即时保存到本地文件中。

## 功能特点

- 自动连接到Solana区块链网络
- 从种子钱包开始，通过交易关系发现更多相关钱包
- 分析钱包交易数据，计算胜率、盈亏比等指标
- 根据筛选条件识别"聪明钱包"
- 发现后即时保存到CSV格式文件

## 安装依赖

```bash
pip install solana pydantic-settings aiohttp
```

## 配置

### 修改Solana节点

在`app/core/config.py`文件中可以修改Solana节点URL：

```python
# Solana链配置
SOLANA_RPC_URL: str = "https://solana.chainupcdn.com"  # 修改为你喜欢的节点
```

可选节点:
- https://api.mainnet-beta.solana.com (官方节点)
- https://rpc.ankr.com/solana (Ankr节点)
- https://solana.chainupcdn.com (ChainUp节点)

### 配置代理

如果无法直接访问Solana网络，可以在`real_mode.py`中配置代理：

```python
# 尝试使用代理连接 (这里使用了一个示例代理地址，需要修改为你自己的代理)
proxy = "http://127.0.0.1:7890"  # 修改为你的代理地址
```

### 修改筛选条件

在`app/core/config.py`文件中可以修改聪明钱包的筛选条件：

```python
# 聪明钱包筛选条件
WIN_RATE_THRESHOLD: float = 70.0  # 胜率阈值(%)
PROFIT_LOSS_RATIO: float = 3.0    # 盈亏比
MIN_DAILY_TRADES: int = 20        # 最小日均交易次数
MAX_HOLDING_HOURS: int = 24       # 最大持仓时间(小时)
```

## 使用方法

运行以下命令启动程序：

```bash
python real_mode.py
```

程序会自动:
1. 连接到Solana网络
2. 分析种子钱包
3. 发现新钱包并分析
4. 将符合条件的聪明钱包保存到CSV文件中

输出文件格式为`smart_wallets_YYYYMMDD_HHMMSS.txt`，包含以下信息：
- 钱包地址
- 余额(SOL)
- 胜率(%)
- 盈亏比
- 日均交易
- 平均持仓时间(小时)
- 交易总数
- 最后活跃时间
- 发现时间

## 注意事项

1. 程序需要网络能够连接到Solana节点
2. 如遇连接问题，请尝试配置代理或更换节点
3. 处理大量钱包可能需要较长时间
4. 当前算法使用了简化的分析方法，实际项目中应使用更复杂的算法

## 技术栈

* **后端**：Python 3.9+, FastAPI, SQLAlchemy
* **区块链**：Solana-py
* **数据库**：SQLite
* **前端**：Bootstrap 5, Chart.js

## 快速开始

### 环境要求

* Python 3.9或更高版本
* pip包管理器

### 安装

1. 克隆仓库
```bash
git clone https://github.com/yourusername/solana-smart-wallet-tracker.git
cd solana-smart-wallet-tracker
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 复制环境变量示例文件
```bash
cp .env.example .env
```

4. 根据需要修改环境变量中的配置

### 运行

```bash
python main.py
```

访问 http://localhost:8080 查看Web界面。

## 部署

要在生产环境中部署，建议：

1. 使用更稳定的数据库（如PostgreSQL）
2. 设置反向代理（如Nginx）
3. 使用进程管理器（如Supervisor或Systemd）
4. 设置HTTPS

### 域名配置

如果您拥有域名并想要绑定，请配置Nginx（或其他Web服务器）的反向代理：

```nginx
server {
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

然后获取SSL证书并配置HTTPS。

## 许可证

[MIT](LICENSE)

## 致谢

感谢Solana社区提供的优秀API和开发工具。

## 运行模式

该项目提供了两种运行模式:

### 1. 演示模式

使用模拟数据运行，无需连接到Solana网络，适合快速体验和开发测试。

```bash
python fixed_demo_mode.py
```

### 2. 真实模式

连接到真实的Solana网络获取数据。这种模式需要稳定的网络连接和配置正确的RPC节点。

```bash
python real_mode.py
```

## 中国大陆用户指南

对于中国大陆用户，可能会遇到Solana官方节点连接问题。我们已将默认节点配置更改为Ankr提供的公共节点，该节点在中国大陆通常可以访问。

如果仍然遇到连接问题，可以尝试以下解决方案:

1. **使用代理服务器**: 修改`real_mode.py`文件中的`startup_event`函数，取消注释代理配置行并设置您的代理地址。

```python
# solana_connection = get_solana_connection(proxy="http://127.0.0.1:7890")
```

2. **使用其他节点**: 在`app/core/config.py`文件中修改节点URL配置。我们提供了几个备选节点:

```python
# 备用节点配置
# Triton公共节点: "https://api.mainnet-beta.solana.com"
# ChainUp节点: "https://solana.chainupcdn.com"
# Helius节点(需API Key): "https://mainnet.helius-rpc.com/?api-key=YOUR_API_KEY"
```

3. **运行测试工具**: 使用`debug_api.py`脚本测试不同节点的连接情况:

```bash
python debug_api.py
``` 