FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/

RUN chmod +x /app/entrypoint.sh
# Ensure Windows CRLF doesn't break shell parsing / argument matching.
RUN sed -i 's/\r$//' /app/entrypoint.sh || true

EXPOSE 8000

# Use `sh` to avoid shebang issues caused by CRLF line endings on Windows.
CMD ["sh", "/app/entrypoint.sh"]

