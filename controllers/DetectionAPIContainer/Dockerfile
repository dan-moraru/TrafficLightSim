FROM python:3.7.4
WORKDIR /DetectionAPIContainer
EXPOSE 5227

COPY controllers/DetectionAPIContainer/requirements.txt .
RUN pip3 install -r requirements.txt

COPY controllers/DetectionAPIContainer/DetectionApi.py .

CMD ["python3", "./DetectionApi.py"]