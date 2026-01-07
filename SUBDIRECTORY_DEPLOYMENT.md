# 子目录部署指南

部署到域名子目录（如 `explain1thing.top/birthday`）。

## Nginx 配置

在主 Nginx 的 HTTPS server 块中添加：

```nginx
# Birthday Notify Bird
location = /birthday {
    return 301 /birthday/;
}

location ^~ /birthday/ {
    proxy_pass http://127.0.0.1:8888/;  # 末尾斜杠必须！剥离前缀
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**关键点：**
- `location = /birthday` - 精确匹配，重定向加斜杠
- `location ^~ /birthday/` - 前缀匹配，优先级高于正则
- `proxy_pass` 末尾加 `/` - 把 `/birthday/health` 代理为 `/health`

## 部署步骤

```bash
# 1. 进入项目目录
cd ~/projects/Birthday-notify-bird

# 2. 配置环境变量
nano .env
# 添加：ROOT_PATH=/birthday

# 3. 启动/重启应用
docker compose up -d
# 或 docker compose restart

# 4. 编辑 Nginx 配置
nano /etc/nginx/sites-available/default
# 在 server { listen 443 ... } 块内添加上面的 location

# 5. 重载 Nginx
nginx -t && systemctl reload nginx
```

## 测试

```bash
# 测试应用本身
curl http://127.0.0.1:8888/health

# 测试 HTTPS（如果有 HTTP→HTTPS 重定向）
curl https://your-domain/birthday/health

# 或浏览器直接访问
https://your-domain/birthday
```

## 常见问题

**301 重定向到 HTTPS**
- 正常！Nginx 配置了 HTTP→HTTPS
- 用 `curl https://...` 或浏览器测试

**404 Not Found**
- 检查 `.env` 中 `ROOT_PATH=/birthday`
- 检查 `docker compose restart` 是否执行

**502 Bad Gateway**
- 应用没跑：`docker compose ps`
- 查看日志：`docker compose logs -f`

**路径不对 / 静态文件 404**
- 检查 `proxy_pass` 末尾是否有 `/`
- 有斜杠：`/birthday/x` → `/x` ✅
- 无斜杠：`/birthday/x` → `/birthday/x` ❌

## grug 总结

```bash
# Nginx 配置
location = /birthday { return 301 /birthday/; }
location ^~ /birthday/ { proxy_pass http://127.0.0.1:8888/; }

# 应用配置
ROOT_PATH=/birthday

# 测试
curl https://domain.com/birthday/health
```
