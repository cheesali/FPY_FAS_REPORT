import os
from django.conf import settings
from django.core.asgi import get_asgi_application as asgi
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line
from django.conf import settings
from django.conf.urls.static import static

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
wsgi = lambda *args, **kwargs: get_wsgi_application()(*args, **kwargs)

from django.urls import include, path
from django.contrib import admin
from django.utils.functional import SimpleLazyObject
from utils.django_url import UrlManager
app_urls_api = UrlManager(views_root='LOGIC')
app_urls_pages = UrlManager(views_root='PAGES')


urlpatterns = SimpleLazyObject(
    lambda:[
            path('admin/', admin.site.urls),
            path('', include(app_urls_pages.url_patterns)),
            path('api/', include(app_urls_api.url_patterns)),
            path("__reload__/", include("django_browser_reload.urls")),
        ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )

if __name__ == "__main__":
    execute_from_command_line()
    
