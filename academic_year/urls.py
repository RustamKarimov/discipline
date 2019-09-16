from django.urls import path

from . import views


urlpatterns = [
    path('list/', views.AcademicYearList.as_view(), name='list'),
    path('add/', views.add_academic_year, name='add'),
    path('<slug:slug>/', views.AcademicYearDetails.as_view(), name='details'),
    path('update/<slug:slug>/', views.AcademicYearEdit.as_view(), name='edit'),
    path('delete/<slug:slug>/', views.AcademicYearDelete.as_view(), name='delete'),
]