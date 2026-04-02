FROM python:3.10

RUN apt-get update && apt-get install -y \
    texlive-xetex 
#     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY fonts /app/fonts

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]