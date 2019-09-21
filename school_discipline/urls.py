import debug_toolbar

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import urls as auth_urls

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', views.Login.as_view(), name='login'),
    path('accounts/logout/', views.logout_user, name='logout'),
    path('accounts/', include(auth_urls)),
    path('academic_year/', include(('academic_year.urls', 'academic_year'), namespace='years')),
    path('discipline/', include(('discipline.urls', 'discipline'), namespace='disciplines')),
    path('grade/', include(('grades.urls', 'grades'), namespace='grades')),
    path('settings/', include(('settings.urls', 'settings'), namespace='settings')),
    path('teacher/', include(('users.urls.teacher_urls', 'users'), namespace='teachers')),
    path('learner/', include(('users.urls.learner_urls', 'users'), namespace='learners')),
    path('', views.dashboard, name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]