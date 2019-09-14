from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('academic_year/', include(('academic_year.urls', 'academic_year'), namespace='years')),
    path('discipline/', include(('discipline.urls', 'discipline'), namespace='discipline'))
    path('grades/', include(('grades.urls', 'grades'), namespace='grades')),
    path('settings/', include(('settings.urls', 'settings'), namespace='settings')),
    path('teacher/', include(('users.urls.teacher_urls', 'users'), namespace='teacher')),
    path('learner/', include(('users.urls.learner_urls', 'users'), namespace='learner')),
]
