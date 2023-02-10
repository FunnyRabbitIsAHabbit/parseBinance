FROM python:3.10-slim

WORKDIR /my_app
COPY . .

RUN pip install --no-cache-dir --upgrade -r /my_app/requirements.txt

ENTRYPOINT ["python", "-u", "main.py"]