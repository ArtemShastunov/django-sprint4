from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from blog import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include(
        ('django.contrib.auth.urls', 'auth'),
        namespace='auth'
    )),
    path('auth/registration/', blog_views.signup, name='registration'),
    path('', include('blog.urls', namespace='blog')),
    path('', include('pages.urls', namespace='pages')),
]

handler500 = 'pages.views.page_500'
handler404 = 'pages.views.page_404'
handler403 = 'pages.views.page_403'

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
