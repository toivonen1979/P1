FROM centos:latest
RUN yum install -y bind-utils
COPY dns_proxy_socket.py /root/
COPY ca-bundle.crt /root/
EXPOSE 53
WORKDIR /root
CMD python dns_proxy_socket.py
