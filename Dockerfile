# Use the official Python lightweight image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy ONLY requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# The default command to run when the container starts
# CMD ["python", "app.py"]

# For production
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "app:app"]