from django.urls import path

from . import views


urlpatterns = [
    path('merit/list', views.MeritList.as_view(), name='merit_list'),
    path('demerit/list', views.DemeritList.as_view(), name='demerit_list'),

    path('merit/add', views.MeritAdd.as_view(), name='merit_add'),
    path('demerit/add', views.DemeritAdd.as_view(), name='demerit_add'),

    path('<slug:slug>/', views.DisciplineDetail.as_view(), name='details'),
    path('edit/<slug:slug>/', views.DisciplineEdit.as_view(), name='edit'),
    path('delete/<slug:slug>/', views.DisciplineDelete.as_view(), name='delete'),
]