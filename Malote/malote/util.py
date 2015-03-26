import requests
from requests.adapters import HTTPAdapter
from functools import wraps

class NotCheckingHostnameHTTPAdapter(HTTPAdapter):
    def cert_verify(self, conn, *args, **kwargs):
        super().cert_verify(conn, *args, **kwargs)
        conn.assert_hostname = False

def require_cert(method):
    @wraps(method)
    def _handle(self, *args, **kwargs):
        if self.request.get_ssl_certificate() is None:
            self.set_status(403)
            self.write({"msg": "Client certificate required"})
            self.finish()
        else:
            method(self, *args, **kwargs)
    return _handle
