FROM python:3.9-slim
COPY ./ /app
WORKDIR /app
RUN apt-get update
RUN apt-get install -y build-essential libpq-dev postgresql-client cron nano gettext librsync-dev libsecp256k1-0
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
#RUN chmod +x backup_cron.sh
#RUN (crontab -l; echo '0 15 * * * /app/backup_cron.sh >> /var/log/backup_cron.log 2>&1') | crontab -
CMD service cron start && python3 app.py
EXPOSE 5000
