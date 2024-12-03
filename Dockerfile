# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the working directory
COPY . /app/

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/entrypoint.sh

# Set executable permissions for the entrypoint script
RUN chmod +x /app/entrypoint.sh   # Ajoute cette ligne

# Expose the port that Django will run on
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
