# 🐦 Birthday Notify Bird

生日提醒小助手 - 再也不会忘记重要的人的生日。

## 功能特性

- 📋 网页管理联系人生日
- 📅 提前 **7 天** 邮件提醒
- ⏰ 提前 **1 天** 邮件提醒  
- 🎂 **当天** 邮件提醒
- 🔒 支持 Docker 部署 + Nginx IP 白名单

## 快速开始（本地开发）

### 1. 安装依赖

```bash
# 建议使用虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置模板
cp env.example .env

# 编辑 .env 文件，填入你的 SMTP 配置
```

### 3. 启动服务

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --port 8000

# 访问 http://localhost:8000
```

## 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `TO_EMAIL` | 接收提醒的邮箱 | `me@example.com` |
| `FROM_EMAIL` | 发件人邮箱 | `noreply@example.com` |
| `SMTP_HOST` | SMTP 服务器 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP 端口 | `587` |
| `SMTP_USERNAME` | SMTP 用户名 | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTP 密码/应用专用密码 | `xxxx-xxxx-xxxx` |
| `SMTP_MODE` | 加密模式 | `starttls` / `ssl` / `plain` |
| `TIMEZONE` | 时区 | `Asia/Shanghai` |
| `DAILY_RUN_AT` | 每日检查时间 | `09:00` |

### Gmail 配置说明

如果使用 Gmail：
1. 开启两步验证
2. 生成应用专用密码：Google 账号 → 安全 → 应用专用密码
3. 使用应用专用密码作为 `SMTP_PASSWORD`

## 项目结构

```
Birthday-notify-bird/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 入口
│   ├── settings.py      # 配置管理
│   ├── models.py        # 数据模型
│   ├── db.py            # 数据库连接
│   ├── emailer.py       # 邮件发送
│   ├── scheduler.py     # 定时任务
│   ├── routes/          # 路由模块
│   ├── templates/       # Jinja2 模板
│   └── static/          # 静态文件
├── nginx/               # Nginx 配置（可选）
├── data/                # SQLite 数据库（自动创建）
├── requirements.txt
├── env.example
├── Dockerfile
├── docker-compose.yml
└── docker-compose.nginx.yml  # 带 Nginx 的部署配置
```

## Docker 部署

### 基础部署（无 IP 限制）

```bash
# 1. 配置环境变量
cp env.example .env
# 编辑 .env 填入 SMTP 配置

# 2. 启动服务
docker compose up -d

# 访问 http://your-server:8000
```

### 带 Nginx IP 白名单的部署

```bash
# 1. 配置环境变量
cp env.example .env

# 2. 编辑 nginx/nginx.conf，添加你的 IP 到白名单
# allow 123.45.67.89;  # 你的 IP
# deny all;            # 取消注释这行

# 3. 启动服务
docker compose -f docker-compose.nginx.yml up -d

# 访问 http://your-server
```

## 手动触发提醒检查

访问 `/logs` 页面，点击"手动触发检查"按钮，可以立即执行一次生日检查。

这对于测试邮件发送非常有用：
1. 添加一个联系人，生日设为今天/明天/7天后
2. 手动触发检查
3. 查看发送记录和收件箱

## License

MIT

