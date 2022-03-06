FROM python:3.8

WORKDIR /shopping-list
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]