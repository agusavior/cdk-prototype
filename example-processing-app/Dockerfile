FROM python:3.8

# Python dependencies.
COPY ./requirements.txt /app/requirements.txt
RUN python3 -m pip install -r requirements.txt -t .

# App source.
COPY . /app

# Run it.
WORKDIR /app
CMD ["python", "__init__.py"]
