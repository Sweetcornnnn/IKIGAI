import os
from django.conf import settings
from django.urls import path, re_path
from django.views.static import serve as static_serve

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Static file serving in development
static_routes = []
if settings.DEBUG:
    static_routes = [
        re_path(r'^static/(?P<path>.*)$', static_serve, {
            'document_root': settings.BASE_DIR / 'static',
            'show_indexes': True,
        }),
    ]