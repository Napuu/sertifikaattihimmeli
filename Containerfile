FROM certbot/dns-cloudflare:v2.8.0 as certbot
WORKDIR /app
RUN pip install kubernetes
COPY renew.py renew.py
ENTRYPOINT ["python", "/app/renew.py"]