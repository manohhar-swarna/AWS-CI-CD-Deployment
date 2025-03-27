# Use a base image with Python installed
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /rice/application

# Copy the requirements.txt file
COPY requirements.txt /rice/application

#copy app.py file
COPY app.py /rice/application

#copy templates  directory
COPY templates /rice/application/templates

#copy templates  directory
COPY current_endpoint_name.txt /rice/application

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Set the entry point or default command for the container
CMD ["python", "./app.py"]  # Adjust as per your project structure
