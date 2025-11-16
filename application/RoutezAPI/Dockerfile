# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirementsApp.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirementsApp.txt

# Copy the rest of the application's code
COPY . .

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
