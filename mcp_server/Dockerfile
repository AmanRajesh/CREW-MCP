FROM python:3.10-slim

WORKDIR /app
COPY mcp_server/ /app/mcp_server/
COPY database/ /app/database/
COPY manual.txt /app/manual.txt
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
CMD ["python", "mcp_server/server.py"]
