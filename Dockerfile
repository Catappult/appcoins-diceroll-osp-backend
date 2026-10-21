# Use the official Python 3.11 image from the DockerHub
FROM python:3.11

# Refresh the OS CA bundle so the image gets the patched Debian ca-certificates
# (eMudhra CA distrust, SYS-3193).
RUN apt-get update && \
    apt-get install -y --no-install-recommends --only-upgrade ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file into the container
COPY ./requirements.txt /app/requirements.txt

# Install the requirements
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the current directory contents into the container
COPY ./main.py /app/main.py

# Set the command to run when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]