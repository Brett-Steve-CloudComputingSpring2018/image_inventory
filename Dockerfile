FROM python:2.7

WORKDIR /app

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y vim
RUN pip install anchorecli
    
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
    
COPY src /app
RUN chmod +x /app/*.py

ENV PYTHONPATH=/usr/local/lib/python2.7/site-packages/ 

#ENTRYPOINT ["/app/imageinv.py"]