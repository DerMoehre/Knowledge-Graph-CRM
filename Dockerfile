FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /src

# Copy dependency files first to leverage Docker caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# --system tells uv to install into the global site-packages of the container
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy the application code
COPY app/ ./app

ENV PYTHONPATH=/src

EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]