from django.urls import path

from . import views


urlpatterns = [
    path('list/', views.GradeList.as_view(), name='list'),
    path('add/', views.GradeAdd.as_view(), name='add'),
    path('<slug:slug>/', views.GradeDetails.as_view(), name='details'),
    path('edit/<slug:slug>/', views.GradeEdit.as_view(), name='edit'),
    path('delete/<slug:slug>/', views.GradeDelete.as_view(), name='delete'),

    path('<slug:slug>/assign_teachers/', views.AssignTeachersToGrade.as_view(), name='assign_teachers'),

]