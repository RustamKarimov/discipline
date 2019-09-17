from django.urls import path

from users import views

from users.views import teacher_views as views
from users import tasks


urlpatterns = [
    path('list/', views.TeacherList.as_view(), name='list'),
    path('add/', views.TeacherAdd.as_view(), name='add'),
    path('read-from-file/', views.add_teachers_from_file, name='read_from_file'),
    path('<slug:slug>/', views.TeacherDetails.as_view(), name='details'),
    path('edit/<slug:slug>/', views.TeacherEdit.as_view(), name='edit'),
    path('delete/<slug:slug>/', views.TeacherDelete.as_view(), name='delete'),
    path('<slug:slug>/assign_grades/', views.AssignGradesToTeacher.as_view(), name='assign_grades'),

]