# dnsproxy
DNS to DNS-over-TLS proxy
# Requirements
- Docker
# Running the application
Build Docker image
```
$ docker build . -t dnsproxy
```
Run a container using the new image
```
$  docker run --rm -d  -p 53:53/tcp -p 53:53/udp -t dnsproxy
```
Now you should be able to make dns queries to localhost on port 53, either tcp or udp
