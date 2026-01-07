# 🐦 Birthday Notify Bird

生日提醒。提前7天、1天、当天发邮件。

## 跑起来

```bash
# 装依赖
pip install -r requirements.txt

# 配置
cp env.example .env
# 编辑 .env，填 SMTP

# 启动
uvicorn app.main:app --reload --port 8888
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `TO_EMAIL` | 收件邮箱 |
| `FROM_EMAIL` | 发件邮箱 |
| `SMTP_HOST` | SMTP 服务器 |
| `SMTP_PORT` | 端口 |
| `SMTP_USERNAME` | 用户名 |
| `SMTP_PASSWORD` | 密码/授权码 |
| `SMTP_MODE` | `starttls` / `ssl` |
| `TIMEZONE` | 时区，默认 `Asia/Shanghai` |
| `DAILY_RUN_AT` | 每日检查时间，默认 `09:00` |

## Docker

```bash
# 基础
docker compose up -d

# 带 Nginx IP 白名单
docker compose -f docker-compose.nginx.yml up -d
```

### 子目录部署

部署到 `domain.com/birthday`？查看 [子目录部署指南](SUBDIRECTORY_DEPLOYMENT.md)

## 测试邮件

```bash
curl http://localhost:8888/api/test-email
```

## 手动触发

访问 `/logs`，点"手动触发检查"。
