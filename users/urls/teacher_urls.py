from django.urls import path

from users import views

from .. import views


urlpatterns = [
    path('list/', views.TeacherList.as_view(), name='list'),
]