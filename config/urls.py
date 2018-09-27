from django.conf import settings
from django.conf.urls import include, static, url
from django.contrib import admin

urlpatterns = [
    url(settings.ADMIN_URL, admin.site.urls),
    url(r'^api/', include('credit_project.api.urls', namespace='api')),
]

if settings.DEBUG:
    urlpatterns += static.static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [url("__debug__/", include(debug_toolbar.urls))] + urlpatterns
