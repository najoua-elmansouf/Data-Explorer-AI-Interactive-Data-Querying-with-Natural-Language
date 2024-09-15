FROM python:3.9.4

WORKDIR /app

ADD app/ .

RUN pip install -r requirements.txt

EXPOSE 8501

CMD [ "streamlit", "run", "excelbot.py" ]