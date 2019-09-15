from django.urls import path

from users.views import learner_views as views


urlpatterns = [
    path('list/', views.LearnerList.as_view(), name='list'),
    path('add/', views.LearnerAdd.as_view(), name='add'),
    path('<slug:slug>/', views.LearnerDetails.as_view(), name='details'),
    path('edit/<slug:slug>/', views.LearnerEdit.as_view(), name='edit'),
    path('delete/<slug:slug>/', views.LearnerDelete.as_view(), name='delete'),
]