# 🧪 验证指南

## 邮箱配置

| 邮箱 | SMTP_HOST | SMTP_PORT | SMTP_MODE | 密码 |
|------|-----------|-----------|-----------|------|
| Gmail | `smtp.gmail.com` | `587` | `starttls` | 应用专用密码 |
| QQ | `smtp.qq.com` | `587` | `starttls` | 授权码 |
| 163 | `smtp.163.com` | `465` | `ssl` | 授权码 |
| Outlook | `smtp-mail.outlook.com` | `587` | `starttls` | 应用密码 |

### Gmail

1. 开两步验证：https://myaccount.google.com/security
2. 生成应用专用密码：https://myaccount.google.com/apppasswords
3. 16位密码去掉空格填入 `SMTP_PASSWORD`

### QQ

1. 登录 mail.qq.com → 设置 → 账户
2. 开启 POP3/SMTP 服务
3. 发短信验证，拿授权码

### 163

1. 登录 mail.163.com → 设置 → POP3/SMTP/IMAP
2. 开启服务，拿授权码

## .env 模板

```bash
# Gmail
TO_EMAIL=xxx@gmail.com
FROM_EMAIL=xxx@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=xxx@gmail.com
SMTP_PASSWORD=16位应用密码
SMTP_MODE=starttls
TIMEZONE=Asia/Shanghai
DAILY_RUN_AT=09:00
```

## 验证

```bash
# 健康检查
curl http://localhost:8888/health

# 测试邮件
curl http://localhost:8888/api/test-email
```

启动输出应该有：
```
✅ Scheduler started: daily at 09:00 (Asia/Shanghai)
✅ Email configured: xxx@example.com
```

## 功能测试

1. 添加联系人，生日设今天/明天/7天后
2. `/logs` 页面点"手动触发检查"
3. 查收件箱

防重复：同一天同一人同一类型只发一次。

## 常见问题

**SMTP 认证失败** → 检查是不是用了普通密码而不是应用专用密码/授权码

**连接超时** → 检查 SMTP_HOST 和 SMTP_PORT

**QQ 授权码错误** → 重新生成授权码
