from apps.main_app.views import IndexView
from django.urls import path

app_name = 'main_app'

urlpatterns = [
    path('', IndexView.as_view(template_name='main_app/index.html'), name='index'),

    # path('api/crawl/', views.crawl, name='crawl'),
]


# This is required for static files while in development mode. (DEBUG=TRUE)
# No, not relevant to scrapy or crawling :)
# if settings.DEBUG:
#     urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
