FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV SKILLETFILE=Skilletfile.yaml
EXPOSE 8080
CMD ["uvicorn", "skillet_runtime:app", "--host", "0.0.0.0", "--port", "8080"]
