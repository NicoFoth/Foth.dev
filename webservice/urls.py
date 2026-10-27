from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('', include('stars.urls')),
    path('projects/', include('projects.urls')),
    path('puzzle/', include('puzzle.urls')),
    path('cs/', include('csgo.urls')),
    path('poker/', include('poker.urls')),
]

handler404 = 'pages.views.not_found'
