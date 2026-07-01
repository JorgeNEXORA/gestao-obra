#!/usr/bin/env bash
# Instalação da app "Gestão de Obra" no servidor, ao lado da agenda.
# Corre a partir da pasta do repositório já clonado.
set -e

cd "$(dirname "$0")"
echo "== PROARKH — Gestão de Obra · instalação =="

# Dependências de sistema
apt-get update -y
apt-get install -y python3-venv python3-pip

# Ambiente Python isolado
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# Abrir a porta na firewall local, se estiver ativa
if command -v ufw >/dev/null 2>&1 && ufw status | grep -q "Status: active"; then
  ufw allow 8765/tcp || true
fi

# Arrancar / reiniciar com PM2 (não toca na agenda)
pm2 delete orcamentos >/dev/null 2>&1 || true
pm2 start server.py --name orcamentos --interpreter "$(pwd)/.venv/bin/python3"
pm2 save

IP=$(hostname -I | awk '{print $1}')
echo ""
echo "== Instalado! A app está em:  http://$IP:8765 =="
pm2 status
