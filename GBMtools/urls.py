from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings, urls
from SearchTraits import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('tasklist/', include('TaskList.urls')),
    path('search/', include('SearchTraits.urls')),
    path('blog/', include('nblog3.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += static(
#     settings.MEDIA_URL,
#     document_root=settings.MEDIA_ROOT
# )

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

urls.handler404 = views.index