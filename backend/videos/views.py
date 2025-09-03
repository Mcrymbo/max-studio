from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views import View
import requests

from .jellyfin_client import verify_signature


@method_decorator(login_required, name='dispatch')
class ProxyHLSView(View):
    def get(self, request: HttpRequest, item_id: str, filename: str):
        expires = request.GET.get('expires')
        sig = request.GET.get('sig')
        path = request.path.split('?')[0]
        if not (expires and sig and verify_signature(path, int(expires), sig)):
            return HttpResponseForbidden('Invalid signature')

        # Proxy request to Jellyfin
        upstream = f"{settings.JELLYFIN_URL}/Videos/{item_id}/{filename}"
        params = {
            'api_key': settings.JELLYFIN_API_KEY,
        }
        upstream_url = upstream + '?' + urlencode(params)
        r = requests.get(upstream_url, stream=True)
        if r.status_code == 404:
            return HttpResponseNotFound()
        headers = {k: v for k, v in r.headers.items() if k.lower() in ['content-type', 'content-length']}
        resp = StreamingHttpResponse(r.iter_content(chunk_size=8192), status=r.status_code)
        for k, v in headers.items():
            resp[k] = v
        return resp


