FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY agentaudit ./agentaudit
COPY target_agent ./target_agent

RUN pip install --no-cache-dir . && pip install --no-cache-dir "uvicorn[standard]"

ENV PORT=8080 GOOGLE_GENAI_USE_VERTEXAI=FALSE
EXPOSE 8080
CMD ["sh", "-c", "uvicorn agentaudit.server:app --host 0.0.0.0 --port ${PORT}"]
