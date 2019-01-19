Pure Python HTTP Proxy Server which uses only standard library.
Receive http requests from client and forward it to servers which are associated to url patterns.
Supports both Python3 and 2.

=======
Proxy Rule Syntax
[
  (SERVER_1_IP, SERVER_1_PORT, ['URL_PATTERN_1-1', 'URL_PATTERN_1-2', ...]),
  (SERVER_2_IP, SERVER_2_PORT, ['URL_PATTERN_2-1', 'URL_PATTERN_2-2', ...]),
  ...
  (SERVER_N_IP, SERVER_N_PORT, ['URL_PATTERN_N-1', 'URL_PATTERN_N-2', ...]),
]

Proxy Rule Sample
[
  ('127.0.0.1', 8000, ['/api', '/admin', 'static/admin']), 
  ('127.0.0.1', 8080, ['.*']),
]
=======

Proxy server checks url pattern like "1-1, 1-2, ..., 2-1, 2-2, ..., N-1, N-2, ...".
If no pattern matchs the request path, Proxy server will return 504 error response to the client.
Pattern '.*' can be used as Regex wild card as you know.


HOW TO USE
(1) As main Proxy Server program.
Update these params on "proxy.py"
 - LISTEN_IP
 - LISTEN_PORT
 - PROXY_RULE
And then, run it.
"python proxy.py"

I'm using this program as proxy server for frontend(Node) and backend(Django) on dev.
But, using NGINX in production.


(2) Make Proxy Server instance
Also, you can use proxy server on your program.
To do that, import this module "proxy.py" and call get_HTTPServer_instance on your module.
Please check "call_proxy_sample.py" for details.


Author: yuichi.ito
Email: yuichi@yuichi.com