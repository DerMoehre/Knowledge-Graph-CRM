FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
# Frontend's own separate dependencies
COPY pyproject.toml uv.lock ./
RUN uv pip install --system --no-cache -r pyproject.toml

COPY . .
CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]