'''
Python HTTP Proxy Server.
Proxy HTTP requests to upstram servers via URL patterns.
Authour: Yuichi Ito
Email: yuichi@yuichi.com


How to use
(1) As main Proxy Server program.
Update 
 - LISTEN_IP
 - LISTEN_PORT
 - PROXY_RULE
And then, run this program file.

(2) Make Proxy Server instance
Import this module and call get_HTTPServer_instance on another module.
Please check "call_proxy_sample.py" for details.
'''


# CONSTANT PARAMS ONLY FOR (1)
LISTEN_IP = '127.0.0.1'
LISTEN_PORT = 80
PROXY_RULE = [
  ('127.0.0.1', 8000, ['/api', '/admin', 'static/admin']), 
  ('127.0.0.1', 8080, ['.*']),
]


# PUBLIC FUNCTION FOR (2)
def get_HTTPServer_instance(ip, port, proxy_rule):
  # raise Exception if parameters have problem.
  return _get_HTTPServer_instance(ip, port, proxy_rule)



import re
import sys
if sys.version_info.major == 3:
  from http.server import BaseHTTPRequestHandler, HTTPServer
  from urllib.request import HTTPErrorProcessor, Request, build_opener
  from urllib.error import HTTPError, URLError
  RequestWithMethod = Request
elif sys.version_info.major == 2:
  from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
  from urllib2 import HTTPErrorProcessor, Request, build_opener
  from urllib2 import HTTPError, URLError
  class RequestWithMethod(Request):
    def __init__(self, method, *args, **kwargs):
      self._method = method
      Request.__init__(self, *args, **kwargs)
    def get_method(self):
      return self._method
else:
  sys.exit('Python HTTP Proxy: Not supported on your Python version. Exit.')

# Handler for avoiding url redirection(302) at urllib Request.
class _NoRedirectProcessor(HTTPErrorProcessor):
  def http_response(self, request, response):
    return response
  https_response = http_response
  
# Proxy Handler
class _ProxyHTTPRequestHandler(BaseHTTPRequestHandler):

  def __init__(self, proxy_rule, *args):
    proxy_matcher_list = []
    for (ip, port, urlpat_list) in PROXY_RULE:
      for urlpat in urlpat_list:
        t = (re.compile(urlpat), ip, port)
        proxy_matcher_list.append(t)
    self.proxy_matcher_list = proxy_matcher_list
    BaseHTTPRequestHandler.__init__(self, *args)

  def proxy(self, method):

    # Get proxy ip and port from path.
    proxy_ip = ''
    proxy_port = -1
    for (matcher, ip, port) in self.proxy_matcher_list:
      if matcher.match(self.path):
        proxy_ip = ip
        proxy_port = port
        break
    if proxy_port == -1:
      self.send_error(504, 'Error Proxying: URL "{}" doesn\'t match any proxy rule.'.format(self.path))
      self.end_headers()
      return

    # Get original request headers.
    header_dict = {}
    for key in self.headers:
      header_dict[key] = self.headers.get(key)

    # Get original request body.
    content_len = self.headers.get('Content-Length')
    if content_len is None:
      content_len = 0
    else:
      content_len = int(content_len)
      body = self.rfile.read(content_len)

    # Make request to server with original HTTP method.
    url = 'http://{}:{}{}'.format(proxy_ip, proxy_port, self.path)
    if content_len == 0:
      req = RequestWithMethod(method=method, url=url, headers=header_dict)
    else:
      req = RequestWithMethod(method=method, url=url, headers=header_dict, data=body)

    # Build opener which avoid URL redirection.
    opener = build_opener(_NoRedirectProcessor)

    # Access to the upstream server and get response.
    try:
      resp = opener.open(req)
    except HTTPError as e:
      if e.getcode():
        resp = e
      else:
        self.send_error(502, 'Error Proxying: {}'.format(e))
        self.end_headers()
        return
    except URLError as e:
      self.send_error(504, 'Error Proxying: {}'.format(e))
      self.end_headers()
      return
    except Exception as e:
      self.send_error(504, 'Error Proxying: {}'.format(e))
      self.end_headers()
      return      

    # Set response code.
    self.send_response(resp.getcode())

    # Set response header.
    if sys.version_info.major == 3:
      headers = resp.info().as_string().splitlines()
    else:
      headers = resp.info().headers
    for line in headers:
      line_parts = line.split(':', 1)
      if len(line_parts) == 2:
        self.send_header(line_parts[0].strip(), line_parts[1].strip())
    self.end_headers()

    # Set response body.
    self.wfile.write(resp.read())

    # Done.
    return

  def do_GET(self):
    self.proxy('GET')

  def do_POST(self):
    self.proxy('POST')

  def do_PUT(self):
    self.proxy('PUT')

  def do_DELETE(self):
    self.proxy('DELETE')

  def do_HEAD(self):
    self.proxy('HEAD')

  def do_OPTIONS(self):
    self.proxy('OPTIONS')


def _get_HTTPServer_instance(ip, port, proxy_rule):
  import socket
  def is_ip_ok(ip):
    try:
      socket.inet_aton(ip)
    except socket.error:
      return False
    return True

  def is_port_ok(port):
    port_ok = True
    if type(port) is not int:
      port_ok = False
    if port < 0:
      port_ok = False
    if port > 65535:
      port_ok = False
    return port_ok

  # IP check
  if not is_ip_ok(ip):
    raise Exception('Illegal IP address string "{}" is passed'.format(ip)) 

  # Port check
  if not is_port_ok(port):
    raise Exception('Illegal Port number "{}" is passed'.format(port))

  # Proxy rule check
  for (proxy_ip, proxy_port, urlpat_list) in proxy_rule:
    if not is_ip_ok(proxy_ip):
      raise Exception('Illegal IP address string "{}" is in proxy_rule'.format(ip))

    if not is_port_ok(proxy_port):
      raise Exception('Illegal Port number "{}" is in proxy_rule'.format(port))

    for urlpat in urlpat_list:
      is_ok = True
      try:
        # through Exception if urlpat contains illegal ascii chars
        re.compile(urlpat)
      except:
        is_ok = False
      if not is_ok:
        raise Exception('Illegal Regex pattern "{}" is in proxy_rule'.format(urlpat))

  # All params are OK. 
  # Create handler with proxy rule
  def handler(*args):
    return _ProxyHTTPRequestHandler(proxy_rule, *args)

  # Build HTTP Server
  httpd = HTTPServer((ip, port), handler)

  return httpd


if __name__ == '__main__':
  httpd = get_proxy_instance(LISTEN_IP, LISTEN_PORT, PROXY_RULE)
  print('Python http proxy is running at {}:{}'.format(LISTEN_IP, LISTEN_PORT))
  httpd.serve_forever()