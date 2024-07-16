FROM python:3.11.7

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY model/ model/
COPY removebg/ removebg/
COPY static/ static/
COPY .env .env
COPY *.py .

EXPOSE 80

CMD ["python", "start.py"]
