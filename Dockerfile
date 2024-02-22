FROM python:3.11.8

WORKDIR /code

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY .env ./
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh

COPY . .

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]

CMD ["gunicorn", "app:app"]
