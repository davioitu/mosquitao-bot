FROM python:3.10

WORKDIR /usr/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "main.py" ]