FROM python:3.7.4
WORKDIR /WeatherAPIContainer
EXPOSE 5226

COPY controllers/WeatherAPIContainer/requirements.txt .
RUN pip3 install -r requirements.txt

COPY controllers/WeatherAPIContainer/WeatherApi.py .

CMD ["python3", "./WeatherApi.py"]