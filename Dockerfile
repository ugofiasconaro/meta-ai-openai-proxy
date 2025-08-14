# Use an official Python runtime as a parent image
FROM python:3.13-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
RUN chmod +x /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

ENV SELENIUM_HEADLESS="true"
ENV WEBDRIVER_URL="http://127.0.0.1:4444"
ENV DEBUG_ENABLED="false"
ENV METAAI_USERNAME="fiascojob"

# Run the send_message.py when the container launches
ENV SESSION_FILE_PATH="/app/data/session_data.json"
VOLUME /app/data

ENTRYPOINT ["/app/entrypoint.sh"]