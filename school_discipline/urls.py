from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('academic_year/', include(('academic_year.urls', 'academic_year'), namespace='years')),
    path('discipline/', include(('discipline.urls', 'discipline'), namespace='disciplines')),
    path('grade/', include(('grades.urls', 'grades'), namespace='grades')),
    path('settings/', include(('settings.urls', 'settings'), namespace='settings')),
    path('teacher/', include(('users.urls.teacher_urls', 'users'), namespace='teachers')),
    path('learner/', include(('users.urls.learner_urls', 'users'), namespace='learners')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)