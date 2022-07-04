FROM python:3.9-slim

# additional repositories for fonts
RUN sed -i'.bak' 's/$/ contrib/' /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y --no-install-recommends git ttf-mscorefonts-installer && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir bot
WORKDIR /bot

ENV PYTHONUNBUFFERED 1

# install required packages
COPY requirements.txt ./
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# copy files
COPY . .

# start the Bot
CMD ["python", "Zenyatta.py"]
