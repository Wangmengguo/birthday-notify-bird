# 子目录部署指南

如何将 Birthday Notify Bird 部署到域名的子目录下（如 `explain1thing.top/birthday`）。

## 方案选择

### 方案 A：主 Nginx + Docker 应用（推荐）

适合：域名已有其他服务，需要在子路径下添加应用。

```nginx
# 在你的主 Nginx 配置中添加（如 /etc/nginx/sites-available/default）

server {
    listen 80;
    server_name explain1thing.top;
    
    # 其他服务的配置...
    
    # Birthday Notify Bird - 子路径部署
    location /birthday {
        proxy_pass http://localhost:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

**部署步骤：**

```bash
# 1. 配置环境变量
cd ~/projects/Birthday-notify-bird
cp env.example .env
nano .env
```

在 `.env` 中添加：
```bash
ROOT_PATH=/birthday
```

```bash
# 2. 启动应用（不使用 Nginx compose）
docker compose up -d

# 3. 重载主 Nginx
sudo nginx -t
sudo systemctl reload nginx

# 4. 访问测试
curl http://explain1thing.top/birthday/health
```

### 方案 B：独立 Docker Nginx（不推荐用于子路径）

如果使用 docker-compose-nginx.yml，需要：

1. 修改 `nginx/nginx.conf`：
```nginx
location /birthday {
    proxy_pass http://birthday_app;
    # ... 其他配置
}
```

2. 修改 `.env`：
```bash
ROOT_PATH=/birthday
```

3. 启动：
```bash
docker compose -f docker-compose.nginx.yml up -d
```

**注意**：此方案 Nginx 监听 80 端口，会与主 Nginx 冲突。

## 配置说明

### 必须设置的环境变量

```bash
# .env 文件
ROOT_PATH=/birthday  # 子路径前缀
```

### 验证配置

```bash
# 检查应用启动日志
docker compose logs -f app

# 测试健康检查
curl http://your-domain/birthday/health

# 应返回：
# {"status":"ok","email_configured":true,...}
```

## 常见问题

**Q: 访问子路径返回 404**
- 检查主 Nginx location 配置是否正确
- 检查应用 ROOT_PATH 环境变量
- 检查应用容器是否运行：`docker compose ps`

**Q: 样式/静态文件加载失败**
- FastAPI 的 root_path 会自动处理，无需额外配置
- 检查浏览器开发者工具中的请求路径

**Q: 从子路径切换回根路径**
- 删除或注释 `.env` 中的 `ROOT_PATH`
- 重启容器：`docker compose restart`

## grug 总结

```bash
# 1. 主 Nginx 加 location /birthday
# 2. .env 加 ROOT_PATH=/birthday
# 3. docker compose up -d
# 4. 访问 domain.com/birthday
```

完。

