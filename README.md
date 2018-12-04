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

## Options
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
## Known bugs and issues
+ When the rate of requests/sec breaks the threshold of a few requests per second 
there is a problem with the constructor of the TLS connection that raises a `ValueError: attempt to connect already-connected SSLSocket!`. 
This is a known issue in Python 3.7 https://github.com/dpkp/kafka-python/issues/1549
+ The buffer is fixed to 4096.  In the very unlikely case of a requests with tens of queries or big resource records, 
the message could be cut off.
+ The program doesn't respond to SIGTERM. In future versions a event management logic could be implemented to improve that.
+ The TCP Thread closes the client connection after sending the first response. This behaviour does not comply with the section 4.2.2 of rfc1035.
The server should wait until the connection has been idle for a period on the order of two minutes before reclaiming a 
connection. Future versions should implement the control logic to address this issue.
+ The general error handling has to be improved.
## Implementation
- This program uses the Python threading module to spawn two Thread  subclasses. One for UDP requests and one for TCP requests.
It has been considered a good approach to serve TCP and UDP clients in parallel.  

- Process-based parallelism has been discarded given that this program is not CPU bound.
- In each Thread subclass the run() method has been overwritten with the socket and data manipulation logic.
- The UDP proxy Thread uses a function to add a prefixed two byte length field which gives the message length 
when transpose the DNS payload from UDP to TCP. The opposite operation is done with the response when the message goes 
from TCP to UDP. See  section 4.2.2 of rfc1035.
- Both subclasses call the same static function to open a TLS socket to the resolver DNS.  
- For each request a new TLS socket is created, with the overhead associated with the handshake. 
This is clearly inefficient. 
Future versions should solve this problem reusing the TLS socket for more than one request.
- Currently the program only allow one DNS resolver server. Future versions should allow more than one and implement Round Robin mechanism.
- The configuration of the SSLContext is closer to the strict profile of DNS over TLS rfc8310, but is not fully compliant.  
 `TLS_1.2, TLS only as a transport (no fallback to UDP or TCP), SSL Cert required `  
 # Questions
 ## Security concerns
 A DNS query is involved in virtually any Internet activity.
 The content of the queries is sent in clear text. It's easy for a third person to 
 see the content of  the DNS lookups. That information can reveal which sites we visit , to which domain we send 
 emails and other metadata. Any solution to avoid revealing that information while on transit 
 has to be completed with a list of providers with sounds privacy policies that prevent them from 
 disclosing or using the information distilled from our queries. The encryption of the channel and the 
 authentication provided by the SSL Certs also protects us from DNS spoofing.
 ## Microservices
 A dns to dns-over-tls proxy could be a good candidate to accelerate the transition of a whole plaftorm 
 to DNS privacy and reap the security benefits without having to wait to adapt each and eveyone of the microservices
 running on the platform. 
 The nature of this service makes it a perfect fit to run on a microservices platform. Each container is completely ephemeral.
 The footprint is small. It's perfectly suitable for a scale-out approach based on containers.
 ## Improvements
 - Apart from the ones mentioned in previous sections one desirable improvement would be to 
 implement a cache mechanism to improve the perceived response time and reduce the requests send to outside. 
 A Redis cluster could be a good candidate to store the cache. It would require further analysis to see the 
 actual gains of this solution.
 - Another change to improve the performance and efficiency  would be to implement the logic 
 to use sha256 SPKI to verify the server certificates.
 - Implement instrumentation methods to improve the observability of the service.  
