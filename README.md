# 直播间智能分配系统 - API 服务

飞书多维表格代理后端，部署到 Railway 使用。

## 部署步骤

1. 把这组文件上传到 GitHub 仓库根目录（直接传，不要套文件夹）
2. Railway → New Project → Deploy from GitHub repo → 选择仓库
3. Service → Variables → 添加：
   - `FEISHU_APP_ID` = 你的飞书 App ID
   - `FEISHU_APP_SECRET` = 你的飞书 App Secret
4. Railway 自动部署，复制生成的域名
5. 浏览器访问 `https://你的域名/api/health` 验证

## 文件说明

| 文件 | 用途 |
|------|------|
| `main.py` | FastAPI 主服务 |
| `requirements.txt` | Python 依赖 |
| `Procfile` | Railway 启动命令 |
| `runtime.txt` | Python 版本 |
| `railway.json` | Railway 配置 |
| `.env.example` | 环境变量模板 |
