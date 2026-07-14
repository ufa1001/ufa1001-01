# 直播间智能分配系统 V2 - iOS 版 + Railway 云部署

> 直连飞书多维表格的直播间资源管理系统。iOS 原生风格手机端界面，支持通过 Railway 一键云端部署后端 API。

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户手机 / 浏览器                           │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         iOS 风格前端应用 (妙搭平台部署)                │   │
│  │  底部 Tab 导航 | 大圆角卡片 | 系统字体 | 清爽留白      │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼ HTTPS                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         后端 API 代理服务 (Railway 云端部署)          │   │
│  │  FastAPI → 飞书开放平台 API → 多维表格               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 包含文件

```
live-room-api/
├── backend/
│   ├── main.py              # FastAPI 主服务（7张表 CRUD）
│   ├── requirements.txt     # Python 依赖
│   ├── Procfile             # Railway 启动命令
│   ├── runtime.txt          # Python 版本
│   ├── railway.json         # Railway 部署配置
│   ├── .env.example         # 环境变量模板
│   ├── startup.sh           # 本地启动脚本（备用）
│   └── Dockerfile           # Docker 部署（备用）
└── README.md                # 本文件
```

---

## 第一步：创建飞书自建应用

### 1.1 进入飞书开放平台
打开 [https://open.feishu.cn/app](https://open.feishu.cn/app) → 点击「创建企业自建应用」

### 1.2 填写应用信息
- **应用名称**：直播间管理系统 API
- **应用描述**：直播间智能分配系统后端数据服务

### 1.3 获取凭证
进入「凭证与基础信息」页面，复制：
- **App ID**（如 `cli_xxxxxxxxxxxxxxxx`）
- **App Secret**（点击显示后复制）

> ⚠️ **先保存好这两个值，下一步会用到**

### 1.4 添加多维表格权限
进入「权限管理」→ 搜索并勾选以下权限：

| 权限名称 | 权限码 |
|---------|--------|
| 查看多维表格 | `bitable:app:readonly` |
| 编辑多维表格 | `bitable:app` |

点击「批量开通」→ 确认授权

### 1.5 发布应用
进入「版本管理与发布」→ 点击「创建版本」→ 填写版本号（如 1.0.0）→ 点击「申请发布」→ **联系企业管理员审批通过**

> ⚠️ 应用必须处于「已发布」状态，API 才能正常调用。

### 1.6 给多维表格授权
打开你的多维表格 → 右上角「...」→「添加协作者」→ 搜索你刚创建的应用名称 → 权限选择 **「可编辑」** → 确认添加

---

## 第二步：Railway 一键部署后端

### 2.1 注册 Railway
打开 [https://railway.app](https://railway.app) → 用 GitHub 账号登录（免费额度足够本项目使用）

### 2.2 创建新项目
1. 点击「New Project」→「Empty Project」
2. 点击「Add a Service」→ 选择「GitHub Repo」（需先授权 Railway 访问你的 GitHub）
3. 或者选择「Deploy from GitHub repo」，上传本项目的 `backend` 文件夹为一个新的 GitHub 仓库

### 2.3 更简单的部署方式（推荐）

**方式一：从 GitHub 部署**
1. 把 `backend` 文件夹推送到一个 GitHub 仓库
2. 在 Railway 点击「New Project」→「Deploy from GitHub repo」
3. 选择你的仓库 → Railway 自动识别 Python 项目并安装依赖

**方式二：手动上传部署**
1. 在 Railway 创建 Empty Project
2. 添加 Service → 选择「Empty Service」
3. 进入 Service →「Settings」→ 上传代码（通过 Railway CLI 或 Git）

### 2.4 配置环境变量
在 Railway 项目面板中：
1. 点击你的 Service →「Variables」标签
2. 添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `FEISHU_APP_ID` | `cli_xxxxxxxxxxxxxxxx` | 从飞书开放平台复制的 App ID |
| `FEISHU_APP_SECRET` | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | 从飞书开放平台复制的 App Secret |
| `BASE_TOKEN` | `BLa2b1zJmaniVws3GhccrJfSnvc` | 多维表格 Token（已内置） |

3. Railway 会自动重新部署

### 2.5 获取公网地址
部署完成后，Railway 会自动分配一个域名：
- 点击 Service →「Settings」→「Domains」
- 复制类似 `https://live-room-api-production-xxxx.up.railway.app` 的地址
- 这就是你的后端 API 地址

### 2.6 验证部署
在浏览器访问：
```
https://你的-railway-地址/api/health
```

如果返回：
```json
{
  "status": "ok",
  "app_id_configured": true,
  "app_secret_configured": true
}
```

说明部署成功！

---

## 第三步：配置前端应用

1. 打开 iOS 风格前端应用
2. 首次进入会弹出「配置后端 API」引导
3. 填入你的 Railway 地址：`https://你的-railway-地址`
4. 点击「测试连接」→ 显示「连接成功」后保存
5. 应用自动加载多维表格实时数据

> 如果暂时不想配置 API，点击「跳过」即可使用本地演示数据（103 间房间、15 位运营）。

---

## API 接口文档

部署完成后访问：`https://你的-railway-地址/docs`

### 核心接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/tables` | 获取所有表 |
| GET | `/api/records/直播间明细` | 获取全部房间 |
| POST | `/api/records/直播间明细` | 创建房间 |
| PUT | `/api/records/直播间明细/{id}` | 更新房间 |
| DELETE | `/api/records/直播间明细/{id}` | 删除房间 |
| GET | `/api/records/运营分析汇总` | 运营数据 |
| GET | `/api/records/新主播分配记录` | 新人数据 |
| GET | `/api/records/运营巡检任务` | 巡检数据 |
| GET | `/api/records/项目进度总表` | 项目数据 |
| GET | `/api/records/主播-房间变更历史` | 变更历史 |
| GET | `/api/records/百万独占动态规则` | 独占规则 |

### 创建记录示例
```bash
curl -X POST https://你的-railway-地址/api/records/直播间明细 \
  -H "Content-Type: application/json" \
  -d '{"房间号": "A10-999", "位置": "临港", "状态": "空置", "设备": "单反"}'
```

---

## 数据表映射

| 表名 | table_id | 记录数 |
|------|----------|--------|
| 直播间明细 | tblsnwgk4YwNZ6yU | 103 |
| 运营分析汇总 | tblC9Og3HqSJeB17 | 15 |
| 运营巡检任务 | tblH49EgNnFrotqm | 3 |
| 项目进度总表 | tblm6NfVswtwYtfw | 14 |
| 新主播分配记录 | tbltH4UxFwRdJDKg | 2 |
| 主播-房间变更历史 | tblM0gAlALUpCH70 | 1 |
| 百万独占动态规则 | tbl7uSOxbKwix8zt | 21 |

---

## 常见问题

### Q1: Railway 部署后访问 /api/health 报错
- 检查 Railway 的 Variables 里是否正确设置了 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`
- 检查飞书应用是否已发布并通过审批
- 检查多维表格是否已添加该应用为协作者

### Q2: 提示 "飞书认证失败"
- 确认 App ID 和 App Secret 没有多空格或换行
- 确认应用处于「已发布」状态
- 在 Railway 面板点击「Redeploy」重新部署

### Q3: 前端测试连接失败
- 确认 Railway 服务状态为「Running」（绿色）
- 确认输入的 API 地址是 `https://` 开头
- 检查浏览器控制台是否有 CORS 错误（后端已配置允许所有来源）

### Q4: Railway 免费额度够用吗？
- Railway 免费版提供每月 $5 额度，本项目资源消耗极低，完全够用
- 如果流量增大，可考虑升级到 Hobby 计划（$5/月）

### Q5: 如何更新后端代码？
- 如果通过 GitHub 部署：推送新代码到仓库，Railway 自动重新部署
- 如果手动部署：在 Railway 面板点击「Redeploy」

---

## 技术栈

- **前端**：React + iOS 原生风格 UI + 妙搭平台部署
- **后端**：Python 3.11 + FastAPI + Uvicorn + HTTPX
- **数据源**：飞书多维表格（Bitable）via 飞书开放平台 API
- **云部署**：Railway（Serverless）

---

## 安全建议

1. **不要在前端暴露 App Secret**，所有飞书 API 调用必须通过后端代理
2. **定期轮换 App Secret**：可在飞书开放平台重新生成
3. **Railway 环境变量是安全的**：不会暴露在代码或日志中
4. **生产环境建议**：如果对外开放，可在 Railway 中加一层 Nginx 或 Cloudflare 做防护
