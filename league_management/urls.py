from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import  *

urlpatterns = [
    path('', home, name="home"),
    path("tables/", league_tables, name="league_tables"),
    path("fixtures/", fixtures_page, name="fixtures"),
    path("results/", results_page, name="results"),
    path("teams/", teams_list, name="teams"),
    path("news/", news_page, name="news"),
     path('news/<int:news_id>/', news_detail, name='news_detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)