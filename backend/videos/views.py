from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
    StreamingHttpResponse,
    HttpResponseForbidden,
    HttpResponseNotFound,
    JsonResponse,
)
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import requests
import os
from typing import Optional

from .jellyfin_client import verify_signature, JellyfinClient
from graphql_jwt.settings import jwt_settings
from graphql_jwt.utils import get_user_by_payload


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



@csrf_exempt
class AdminUploadAPI(View):
    """
    Accepts multipart/form-data with fields: file (binary), title, description (optional), genre (optional).
    Auth: Authorization: JWT <token> (must be an authenticated staff user).
    Copies file into Jellyfin library and triggers library refresh.
    """
    def _authenticate(self, request: HttpRequest) -> Optional[object]:
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('JWT '):
            return None
        token = auth[4:]
        try:
            payload = jwt_settings.JWT_DECODE_HANDLER(token)
            user = get_user_by_payload(payload)
            return user
        except Exception:
            return None

    def post(self, request: HttpRequest):
        user = self._authenticate(request)
        if not user or not user.is_authenticated or not user.is_staff:
            return JsonResponse({"error": "Admin authentication required"}, status=401)

        upload = request.FILES.get('file')
        title = request.POST.get('title') or ''
        description = request.POST.get('description') or ''
        genre = request.POST.get('genre') or ''
        if not upload or not title:
            return JsonResponse({"error": "Missing file or title"}, status=400)

        library_path = settings.JELLYFIN_LIBRARY_PATH
        os.makedirs(library_path, exist_ok=True)
        dest_filename = upload.name
        dest_path = os.path.join(library_path, dest_filename)
        with open(dest_path, 'wb') as f:
            for chunk in upload.chunks():
                f.write(chunk)

        client = JellyfinClient(settings.JELLYFIN_URL, settings.JELLYFIN_API_KEY, settings.JELLYFIN_USER_ID)
        client.refresh_library()

        return JsonResponse({
            "ok": True,
            "stored_path": dest_path,
            "title": title,
            "description": description,
            "genre": genre,
        })

