FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py index.html ./

# A base de dados fica num volume para persistir entre atualizações
ENV GO_DB_PATH=/data/gestao_obra.db
VOLUME ["/data"]
EXPOSE 8765

CMD ["python", "server.py"]
