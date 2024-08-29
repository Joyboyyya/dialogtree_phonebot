# Use Python 3.10.7 as a base image
FROM python:3.10.7-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make the environment activation script executable
RUN chmod +x rest_env/Scripts/activate

# Activate the environment and run the application
CMD ["bash", "-c", "source rest_env/Scripts/activate && python -m dialogtree_phonebot.gateway.app"]
