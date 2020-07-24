FROM python:3.6

ENV FLASK_APP run.py

COPY run.py gunicorn-cfg.py requirements.txt requirements-mysql.txt config.py config.json .env ./
COPY app app

RUN pip install -r requirements-mysql.txt

EXPOSE 5005
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "run:app"]
