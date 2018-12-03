# dnsproxy
DNS to DNS-over-TLS proxy
## What does this do?
dnsproxy is a Python program that can run as a local forwarder using DNS-over-TLS to forward queries.The program listen on 53/tcp and 53/udp for incoming queries from localhost or LAN servers and 
immediately forward those queries over TLS to a public DNS server. 
By default the resolver  is Google's DNS server (8.8.8.8)

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
Now you should be able to make dns queries to localhost on port 53, either over tcp or udp
##Options
 The following options could be passed to the program as Environment Variables
+ **SERVER_ADDRESS** local ip address where the program listen for queries. By default is any.  
`example: docker run --rm  -p 53:53/tcp -p 53:53/udp -e "SERVER_HOST=127.0.0.1" dnsproxy`
+ **SERVER_PORT** local ip port where the program listen for queries. By default is 53.  
`example: docker run --rm  -p 53:53/tcp -p 53:53/udp -e "SERVER_PORT=1053" dnsproxy`
+ **RESOLVER_HOST** remote ip address of the public dns resolver server to forward the queries to. By default is 8.8.8.8.  
`example: docker run --rm  -p 53:53/tcp -p 53:53/udp -e "RESOLVER_HOST=1.1.1.1" dnsproxy`
+ **RESOLVER_PORT** remote port of the public dns resolver server to forward the queries to. By default is 853.  
`example: docker run --rm  -p 53:53/tcp -p 53:53/udp -e "RESOLVER_PORT=854" dnsproxy`

## Testing
In order to test the application open two terminals.
Run nslookup in the first terminal to query the local port 53/tcp
````
nslookup -vc www.example.com 127.0.0.1
````
Run a second nslookup in the second terminal to query the local port 53/udp
````
nslookup -novc www.example.com 127.0.0.1
````
