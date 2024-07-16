FROM quay.io/fedora/python-311

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --verbose

COPY . .

EXPOSE 10086

CMD ["python", "start.py"]
