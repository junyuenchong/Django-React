from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from apps.items.urls import urlpatterns as items_urlpatterns

def healthz(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(items_urlpatterns)),
    path("healthz", healthz),
]

