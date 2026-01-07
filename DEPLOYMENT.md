# 🚀 Birthday Notify Bird - 云端服务器部署指南

本文档将手把手教你如何将 Birthday Notify Bird 部署到云端服务器（如阿里云、腾讯云、AWS、DigitalOcean 等）。

---

## 📋 目录

1. [准备工作](#准备工作)
2. [服务器环境配置](#服务器环境配置)
3. [上传项目文件](#上传项目文件)
4. [配置环境变量](#配置环境变量)
5. [部署方式选择](#部署方式选择)
6. [域名和 SSL 配置](#域名和-ssl-配置)
7. [维护和管理](#维护和管理)
8. [故障排查](#故障排查)

---

## 准备工作

### 1. 服务器要求

- **操作系统**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+（推荐 Ubuntu 22.04）
- **配置**: 最低 1 核 1GB（推荐 1 核 2GB）
- **带宽**: 1Mbps 即可
- **存储**: 10GB 即可

### 2. 需要准备的信息

- [ ] 服务器 IP 地址
- [ ] 服务器 SSH 登录密码或密钥
- [ ] 邮件服务配置（SMTP）
- [ ] （可选）域名

### 3. 本地工具

- SSH 客户端（Windows: PuTTY/Xshell，Mac/Linux: 终端）
- SCP/SFTP 工具（Windows: WinSCP/FileZilla，Mac: 终端或 Cyberduck）

---

## 服务器环境配置

### 步骤 1: 连接到服务器

**Mac/Linux:**
```bash
ssh root@your-server-ip
# 或使用密钥
ssh -i /path/to/key.pem root@your-server-ip
```

**Windows (PowerShell):**
```powershell
ssh root@your-server-ip
```

### 步骤 2: 更新系统

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 步骤 3: 安装 Docker

**Ubuntu/Debian:**
```bash
# 卸载旧版本
sudo apt remove docker docker-engine docker.io containerd runc

# 安装依赖
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# 添加 Docker 官方 GPG 密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

**CentOS/RHEL:**
```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

### 步骤 4: 配置 Docker（可选但推荐）

```bash
# 允许非 root 用户使用 Docker
sudo usermod -aG docker $USER

# 重新登录以使权限生效
exit
# 然后重新 SSH 连接
```

---

## 上传项目文件

### 方法 1: 使用 Git（推荐）

如果你的项目在 GitHub/GitLab 上：

```bash
# 在服务器上创建项目目录
cd ~
mkdir -p projects
cd projects

# 克隆项目（替换为你的仓库地址）
git clone https://github.com/your-username/Birthday-notify-bird.git
cd birthday-notify-bird
```

### 方法 2: 使用 SCP 上传

**Mac/Linux:**
```bash
# 在本地项目目录执行
cd /path/to/Birthday-notify-bird

# 压缩项目（排除不必要的文件）
tar -czf birthday-bird.tar.gz \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='data/birthday.db' \
  --exclude='.env' \
  app/ nginx/ requirements.txt Dockerfile docker-compose*.yml env.example README.md

# 上传到服务器
scp birthday-bird.tar.gz root@your-server-ip:~/

# 在服务器上解压
ssh root@your-server-ip
mkdir -p ~/projects/Birthday-notify-bird
cd ~/projects/Birthday-notify-bird
tar -xzf ~/birthday-bird.tar.gz
rm ~/birthday-bird.tar.gz
```

**Windows (使用 WinSCP):**
1. 打开 WinSCP，连接到服务器
2. 创建目录 `/root/projects/Birthday-notify-bird`
3. 上传项目文件（排除 `.git`, `.venv`, `__pycache__`, `data/` 等）

### 方法 3: 直接在服务器上创建文件

如果项目文件不多，可以直接在服务器上创建：

```bash
cd ~
mkdir -p projects/Birthday-notify-bird
cd projects/Birthday-notify-bird

# 然后手动创建或复制文件内容
```

---

## 配置环境变量

### 步骤 1: 创建环境配置文件

```bash
cd ~/projects/Birthday-notify-bird

# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件
nano .env  # 或使用 vim .env
```

### 步骤 2: 填写配置信息

```bash
# ========== 必填项 ==========

# 接收生日提醒的邮箱（你的邮箱）
TO_EMAIL=your-email@example.com

# 发件邮箱
FROM_EMAIL=noreply@example.com

# SMTP 服务器配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_MODE=starttls

# ========== 可选项 ==========

# 时区（默认：Asia/Shanghai）
TIMEZONE=Asia/Shanghai

# 每日检查时间（默认：09:00）
DAILY_RUN_AT=09:00

# 基础 URL（如果需要在邮件中包含链接）
BASE_URL=http://your-domain.com
```

### 步骤 3: Gmail 配置说明

如果使用 Gmail 发送邮件：

1. **开启两步验证**
   - 访问 https://myaccount.google.com/security
   - 找到"两步验证"并开启

2. **生成应用专用密码**
   - 访问 https://myaccount.google.com/apppasswords
   - 选择"应用"→"其他"，输入"Birthday Notify Bird"
   - 生成密码，复制 16 位密码（格式：xxxx xxxx xxxx xxxx）

3. **填入配置**
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # 应用专用密码
   SMTP_MODE=starttls
   ```

### 步骤 4: 保存并退出

```bash
# nano 编辑器
Ctrl + X → Y → Enter

# vim 编辑器
:wq
```

---

## 部署方式选择

### 方式 1: 基础部署（适合个人使用）

**适用场景**: 只有你自己访问，不需要 IP 限制

```bash
cd ~/projects/Birthday-notify-bird

# 构建并启动服务
docker compose up -d

# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f
```

**访问地址**: `http://your-server-ip:8888`

**防火墙配置**:
```bash
# Ubuntu/Debian (使用 ufw)
sudo ufw allow 8888/tcp
sudo ufw reload

# CentOS/RHEL (使用 firewalld)
sudo firewall-cmd --permanent --add-port=8888/tcp
sudo firewall-cmd --reload
```

### 方式 2: Nginx + IP 白名单部署（推荐）

**适用场景**: 需要限制只有特定 IP 才能访问

#### 步骤 1: 获取你的本地 IP

访问 https://ip.sb 或执行：
```bash
curl -4 ip.sb
```

记下你的 IP 地址，例如：`123.45.67.89`

#### 步骤 2: 配置 Nginx IP 白名单

```bash
cd ~/projects/Birthday-notify-bird

# 编辑 Nginx 配置
nano nginx/nginx.conf
```

找到以下部分并修改：

```nginx
server {
    listen 80;
    server_name _;

    # IP 白名单
    allow 123.45.67.89;     # 替换为你的 IP
    # allow 192.168.1.0/24; # 也可以允许整个网段
    deny all;               # 拒绝其他所有 IP
```

保存后退出（Ctrl+X → Y → Enter）

#### 步骤 3: 启动服务

```bash
# 使用 Nginx 配置启动
docker compose -f docker-compose.nginx.yml up -d

# 查看状态
docker compose -f docker-compose.nginx.yml ps

# 查看日志
docker compose -f docker-compose.nginx.yml logs -f
```

**访问地址**: `http://your-server-ip` (端口 80，不需要 8888)

**防火墙配置**:
```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw reload

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload
```

---

## 域名和 SSL 配置

### 前提条件

- 已购买域名（如 `example.com`）
- 域名已添加 A 记录指向服务器 IP

### 步骤 1: 安装 Certbot

```bash
# Ubuntu/Debian
sudo apt install -y certbot

# CentOS/RHEL
sudo yum install -y certbot
```

### 步骤 2: 停止当前服务

```bash
cd ~/projects/Birthday-notify-bird
docker compose -f docker-compose.nginx.yml down
```

### 步骤 3: 获取 SSL 证书

```bash
# 替换 your-domain.com 为你的域名
sudo certbot certonly --standalone -d your-domain.com
```

按提示输入邮箱，同意协议。证书将保存在：
- 证书: `/etc/letsencrypt/live/your-domain.com/fullchain.pem`
- 私钥: `/etc/letsencrypt/live/your-domain.com/privkey.pem`

### 步骤 4: 修改 Nginx 配置支持 HTTPS

```bash
cd ~/projects/Birthday-notify-bird
nano nginx/nginx.conf
```

修改为：

```nginx
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl;
    server_name your-domain.com;

    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # IP 白名单
    allow 123.45.67.89;  # 你的 IP
    deny all;

    location / {
        proxy_pass http://app:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 步骤 5: 修改 docker-compose.nginx.yml 挂载证书

```bash
nano docker-compose.nginx.yml
```

在 `nginx` 服务的 `volumes` 部分添加：

```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: birthday-bird-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"  # 添加 HTTPS 端口
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro  # 添加这行
    depends_on:
      - app
```

### 步骤 6: 启动服务

```bash
docker compose -f docker-compose.nginx.yml up -d
```

**防火墙配置**:
```bash
# Ubuntu/Debian
sudo ufw allow 443/tcp
sudo ufw reload

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

**访问地址**: `https://your-domain.com`

### 步骤 7: 设置证书自动续期

```bash
# 测试自动续期
sudo certbot renew --dry-run

# 添加定时任务
sudo crontab -e

# 添加以下行（每天凌晨 2 点检查续期）
0 2 * * * certbot renew --quiet --deploy-hook "cd ~/projects/Birthday-notify-bird && docker compose -f docker-compose.nginx.yml restart nginx"
```

---

## 维护和管理

### 常用命令

```bash
cd ~/projects/Birthday-notify-bird

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
docker compose logs -f app    # 只看应用日志
docker compose logs -f nginx  # 只看 Nginx 日志

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 更新代码后重新部署
git pull  # 如果使用 Git
docker compose down
docker compose up -d --build

# 查看数据库
docker compose exec app ls -lh /app/data/

# 备份数据库
docker compose exec app cat /app/data/birthday.db > backup_$(date +%Y%m%d).db

# 恢复数据库
cat backup_20240101.db | docker compose exec -T app sh -c 'cat > /app/data/birthday.db'
docker compose restart
```

### 更新应用

```bash
cd ~/projects/Birthday-notify-bird

# 1. 备份数据库
docker compose exec app cat /app/data/birthday.db > backup_$(date +%Y%m%d).db

# 2. 拉取最新代码（如果使用 Git）
git pull

# 3. 重新构建并启动
docker compose down
docker compose up -d --build

# 4. 查看日志确认启动成功
docker compose logs -f
```

### 监控和告警

#### 1. 设置健康检查脚本

```bash
nano ~/check_birthday_bird.sh
```

```bash
#!/bin/bash
HEALTH_URL="http://localhost:8888/health"
WEBHOOK_URL="https://your-webhook-url"  # 可选：钉钉/企业微信等

response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $response -ne 200 ]; then
    echo "Birthday Notify Bird is down! HTTP Status: $response"
    # 发送告警（可选）
    # curl -X POST $WEBHOOK_URL -d "{\"text\":\"Birthday Bird 服务异常\"}"
    
    # 尝试重启
    cd ~/projects/Birthday-notify-bird
    docker compose restart
fi
```

```bash
chmod +x ~/check_birthday_bird.sh

# 添加到 crontab（每 5 分钟检查一次）
crontab -e
# 添加：
*/5 * * * * ~/check_birthday_bird.sh
```

#### 2. 查看资源使用

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h
du -sh ~/projects/Birthday-notify-bird/data/
```

---

## 故障排查

### 问题 1: 无法访问服务

**检查步骤**:

```bash
# 1. 检查服务是否运行
docker compose ps

# 2. 检查端口监听
sudo netstat -tlnp | grep 8888  # 基础部署
sudo netstat -tlnp | grep 80    # Nginx 部署

# 3. 检查防火墙
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-all  # CentOS

# 4. 检查日志
docker compose logs -f
```

**解决方法**:
```bash
# 开放端口
sudo ufw allow 8888/tcp  # 或 80/tcp
sudo ufw reload

# 重启服务
docker compose restart
```

### 问题 2: IP 白名单访问被拒绝

**症状**: 访问时看到 "403 Forbidden"

**检查**:
```bash
# 1. 确认你的真实 IP
curl -4 ip.sb

# 2. 检查 Nginx 配置
cat nginx/nginx.conf | grep -A 5 "allow"
```

**解决**:
```bash
# 更新 nginx.conf 中的 IP
nano nginx/nginx.conf

# 重启 Nginx
docker compose -f docker-compose.nginx.yml restart nginx
```

### 问题 3: 邮件发送失败

**检查**:
```bash
# 1. 查看环境变量配置
cat .env

# 2. 测试邮件发送
curl http://localhost:8888/api/test-email

# 3. 查看应用日志
docker compose logs -f app | grep -i email
```

**常见原因**:
- Gmail 未使用应用专用密码
- SMTP 端口被防火墙阻止
- SMTP 认证信息错误

**解决方法**:
```bash
# 重新生成 Gmail 应用专用密码
# 访问: https://myaccount.google.com/apppasswords

# 更新 .env 文件
nano .env

# 重启服务
docker compose restart
```

### 问题 4: 容器启动失败

**检查**:
```bash
# 查看容器状态
docker compose ps

# 查看详细日志
docker compose logs

# 检查镜像
docker images | grep birthday
```

**解决**:
```bash
# 清理并重建
docker compose down
docker compose up -d --build --force-recreate

# 如果还是失败，查看具体错误
docker compose logs -f
```

### 问题 5: 数据库损坏

**症状**: 应用无法启动，日志显示数据库错误

**解决**:
```bash
cd ~/projects/Birthday-notify-bird

# 1. 停止服务
docker compose down

# 2. 备份当前数据库
docker volume create backup_volume
docker run --rm -v birthday_notify_bird_data:/source -v backup_volume:/backup alpine \
    sh -c "cp /source/birthday.db /backup/birthday.db.backup"

# 3. 删除损坏的数据库（会重新初始化）
docker volume rm birthday_notify_bird_data

# 4. 重新启动
docker compose up -d

# 5. 如果需要恢复数据，联系技术支持
```

### 问题 6: 磁盘空间不足

**检查**:
```bash
# 查看磁盘使用
df -h

# 查看 Docker 磁盘使用
docker system df
```

**清理**:
```bash
# 清理未使用的 Docker 资源
docker system prune -a

# 清理日志
sudo sh -c "truncate -s 0 /var/lib/docker/containers/*/*-json.log"
```

---

## 安全建议

### 1. 定期更新系统

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 3. 修改 SSH 端口（可选）

```bash
sudo nano /etc/ssh/sshd_config
# 修改 Port 22 为其他端口，如 2222
sudo systemctl restart sshd

# 记得更新防火墙
sudo ufw allow 2222/tcp
```

### 4. 定期备份

```bash
# 创建备份脚本
nano ~/backup_birthday_bird.sh
```

```bash
#!/bin/bash
BACKUP_DIR=~/backups/birthday-bird
mkdir -p $BACKUP_DIR

# 备份数据库
docker compose -f ~/projects/Birthday-notify-bird/docker-compose.yml exec -T app \
    cat /app/data/birthday.db > $BACKUP_DIR/birthday_$(date +%Y%m%d_%H%M%S).db

# 只保留最近 7 天的备份
find $BACKUP_DIR -name "birthday_*.db" -mtime +7 -delete

echo "Backup completed: $(date)"
```

```bash
chmod +x ~/backup_birthday_bird.sh

# 添加到 crontab（每天凌晨 3 点备份）
crontab -e
# 添加：
0 3 * * * ~/backup_birthday_bird.sh >> ~/backup.log 2>&1
```

---

## 快速参考

### 一键部署命令（适合复制粘贴）

**基础部署**:
```bash
# 1. 进入项目目录
cd ~/projects/Birthday-notify-bird

# 2. 配置环境变量
cp env.example .env && nano .env

# 3. 启动服务
docker compose up -d

# 4. 查看日志
docker compose logs -f

# 5. 开放防火墙
sudo ufw allow 8888/tcp && sudo ufw reload
```

**Nginx + IP 白名单部署**:
```bash
# 1. 进入项目目录
cd ~/projects/Birthday-notify-bird

# 2. 配置环境变量
cp env.example .env && nano .env

# 3. 配置 IP 白名单
nano nginx/nginx.conf  # 修改 allow 行

# 4. 启动服务
docker compose -f docker-compose.nginx.yml up -d

# 5. 查看日志
docker compose -f docker-compose.nginx.yml logs -f

# 6. 开放防火墙
sudo ufw allow 80/tcp && sudo ufw reload
```

---

## 需要帮助？

- 查看日志: `docker compose logs -f`
- 健康检查: `curl http://localhost:8888/health`
- 测试邮件: `curl http://localhost:8888/api/test-email`
- 重启服务: `docker compose restart`

---

## 总结

恭喜！🎉 你已经成功将 Birthday Notify Bird 部署到云端服务器。

**下一步**:
1. 访问 Web 界面添加联系人
2. 测试邮件发送功能
3. 设置定期备份
4. （可选）配置域名和 SSL

**日常维护**:
- 每月检查一次日志
- 定期更新系统和 Docker
- 确保备份正常运行

祝你使用愉快！再也不会忘记重要的生日了 🎂

