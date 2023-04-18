# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN apt update
RUN apt install -y wget

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install -y ./google-chrome-stable_current_amd64.deb

# Install any needed packages specified in requirements.txt
# RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN pip install Flask requests pdfreader gunicorn flask_httpauth selenium webdriver-manager

# Create a user to run our application
RUN useradd -ms /bin/bash appuser

# Change ownership of the /app directory to the new user
RUN chown -R appuser:appuser /app

# Switch to the newly created user
USER appuser

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME pdf_downloader

# Run the application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]

