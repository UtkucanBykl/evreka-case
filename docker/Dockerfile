# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables for Python buffering
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /code

# Copy the Python dependencies file to the container and install dependencies
COPY ../requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container
COPY .. /code
RUN ["chmod", "+x", "/code/docker/entrypoint.sh"]

# Expose the port the app runs on
EXPOSE 8000
# Start the Django application
ENTRYPOINT ["sh", "/code/docker/entrypoint.sh"]