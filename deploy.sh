#!/bin/bash
# SIGINT Ops — EC2 Deploy Script
# Run as: bash deploy.sh
set -e

echo "==> Creating project directory..."
mkdir -p ~/sigint-ops/backend/data

echo "==> Copying backend files..."
# (Files already uploaded via scp at this point)

echo "==> Creating Python virtual environment..."
cd ~/sigint-ops/backend
python3 -m venv venv
source venv/bin/activate

echo "==> Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Installing systemd service..."
sudo cp ~/sigint-ops/sigint-ops.service /etc/systemd/system/sigint-ops.service
sudo systemctl daemon-reload
sudo systemctl enable sigint-ops
sudo systemctl start sigint-ops

echo "==> Setting up Nginx config..."
sudo cp ~/sigint-ops/nginx-ops.conf /etc/nginx/sites-available/ops.unocloud.us
sudo ln -sf /etc/nginx/sites-available/ops.unocloud.us /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

echo "==> Getting SSL cert..."
sudo certbot --nginx -d ops.unocloud.us --non-interactive --agree-tos -m your@email.com

echo ""
echo "✓ Backend running on port 5002"
echo "✓ Available at https://ops.unocloud.us"
echo ""
echo "Check logs with: sudo journalctl -u sigint-ops -f"
