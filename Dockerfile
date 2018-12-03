FROM python:3
COPY dns_proxy_threaded.py ca-bundle.crt /root/
EXPOSE 53
WORKDIR /root
CMD python dns_proxy_threaded.py
