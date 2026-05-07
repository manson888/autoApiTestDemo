
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .

# 增加 --upgrade 确保依赖解析最新
RUN pip install --no-cache-dir --upgrade -r requirements.txt


COPY . .

CMD ["python", "run.py"]
