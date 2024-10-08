from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from django.views.generic import TemplateView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('topics.urls')),
                  path('', include('feed.urls')),
                  path('', include('users.urls')),
                  path('', include('notifications.urls')),
                  path('passwordreset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
                  path('', TemplateView.as_view(template_name='index.html')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [re_path(r'^.*$', TemplateView.as_view(template_name='index.html'))]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
