# Use the official Python 3.9 image from Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /code

# Copy the requirements.txt file first to leverage Docker cache
COPY ./requirements.txt /code/requirements.txt

# Install the required Python packages, upgrading pip and setuptools
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r /code/requirements.txt

# Copy the rest of the application code
COPY ./ /code/

# Expose port 8000 (optional, but good practice)
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
