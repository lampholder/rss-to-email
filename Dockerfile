FROM python:3
COPY requirements.txt /opt/app/requirements.txt
RUN pip install -r /opt/app/requirements.txt

COPY rss_to_email.py /opt/app

WORKDIR /opt/app
CMD ["python", "./rss_to_email.py"]
