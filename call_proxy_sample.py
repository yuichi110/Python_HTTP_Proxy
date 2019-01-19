import proxy

proxy_rule = [
  ('127.0.0.1', 8000, ['/api', '/admin', 'static/admin']), 
  ('127.0.0.1', 8080, ['.*']),
]

httpd = proxy.get_HTTPServer_instance('127.0.0.1', 80, proxy_rule)
httpd.serve_forever()