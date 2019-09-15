from django.urls import path

from users import views

from .. import views


urlpatterns = [
    path('list/', views.TeacherList.as_view(), name='list'),
    path('add/', views.TeacherAdd.as_view(), name='add'),
    path('<slug:slug>/', views.TeacherDetails.as_view(), name='details'),
    path('edit/<slug:slug>/', views.TeacherEdit.as_view(), name='edit'),
    path('delete/<slug:slug>/', views.TeacherDelete.as_view(), name='delete'),
]