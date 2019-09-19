from django.urls import path

from users.views import learner_views as views
from users import ajax_views


urlpatterns = [
    path('list/', views.LearnerList.as_view(), name='list'),
    path('add/', views.LearnerAdd.as_view(), name='add'),
    path('read-from-file/', views.add_learners_from_file, name='read_from_file'),
    path('assign-grades/', views.assign_grades_to_learners, name='assign_grades'),
    path('<slug:slug>/', views.LearnerDetails.as_view(), name='details'),
    path('edit/<slug:slug>/', views.LearnerEdit.as_view(), name='edit'),
    path('delete/<slug:slug>/', views.LearnerDelete.as_view(), name='delete'),

    path('ajax/load_learners_per_grade/', ajax_views.load_learners_per_grade, name='load_learners_per_grade'),
    path('ajax/assign-grades-to-learners/', ajax_views.grade_formset_for_learners, name='grade_formset_for_learners'),
]