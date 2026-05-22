FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY requirements.txt pyproject.toml ./

# Install dependencies using uv
RUN uv pip install --no-cache -r requirements.txt --system

# Copy source code
COPY . .

# Expose port 8080
EXPOSE 8080

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
