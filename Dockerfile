FROM python:3.8.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements /code/requirements
RUN pip install --upgrade pip && pip install -r requirements/production.txt
COPY . /code/
