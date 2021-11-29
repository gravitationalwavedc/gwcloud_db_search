FROM python:3.8
ENV PYTHONUNBUFFERED 1

# Copy the source code in to the container
COPY src /src
COPY ./runserver.sh /runserver.sh
RUN chmod +x /runserver.sh

# Install dependencies
RUN apt-get update && apt-get install -y python3-virtualenv build-essential python3-dev default-libmysqlclient-dev

# Create python virtualenv
RUN virtualenv -p python3 /src/venv

# Activate and install the django requirements (mysqlclient requires python3-dev and build-essential)
RUN . /src/venv/bin/activate && pip install -r /src/requirements.txt && pip install mysqlclient && pip install gunicorn

# Clean up unneeded packages
RUN apt-get remove --purge -y build-essential python3-dev
RUN apt-get autoremove --purge -y

# Expose the port
EXPOSE 8000

# Set the working directory and start script
WORKDIR /src
CMD [ "/runserver.sh" ]
