# ------------------------
#  Base image
# ------------------------
FROM python:3.11-slim

# ------------------------
#  Prevent .pyc files & buffering
# ------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ------------------------
#  Set working directory
# ------------------------
WORKDIR /app

# ------------------------
#  Copy dependency file & install requirements
# ------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------
#  Copy project files
# ------------------------
COPY . .

# ------------------------
#  Expose Django port
# ------------------------
EXPOSE 8000

# ------------------------
#  Default command (run server)
# ------------------------
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
