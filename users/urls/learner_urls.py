from django.urls import path

from users.views import learner_views as views


urlpatterns = [
    path('list/', views.LearnerList.as_view(), name='list'),
    # path('add/', views.TeacherAdd.as_view(), name='add'),
    # path('<slug:slug>/', views.TeacherDetails.as_view(), name='details'),
    # path('edit/<slug:slug>/', views.TeacherEdit.as_view(), name='edit'),
    # path('delete/<slug:slug>/', views.TeacherDelete.as_view(), name='delete'),
]