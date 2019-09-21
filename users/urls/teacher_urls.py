from django.urls import path

from users import ajax_views

from users.views import teacher_views as views


urlpatterns = [
    path('list/', views.TeacherList.as_view(), name='list'),
    path('add/', views.TeacherAdd.as_view(), name='add'),
    path('read-from-file/', views.add_teachers_from_file, name='read_from_file'),
    path('<slug:slug>/', views.TeacherDetails.as_view(), name='details'),
    path('edit/<slug:slug>/', views.TeacherEdit.as_view(), name='edit'),
    path('delete/<slug:slug>/', views.TeacherDelete.as_view(), name='delete'),
    path('<slug:slug>/assign_grades/', views.AssignGradesToTeacher.as_view(), name='assign_grades'),

    path('<slug:slug>/merit-to-learner/', views.discipline_action_to_learner, name='merit_to_learner'),
    path('<slug:slug>/demerit-to-learner/', views.discipline_action_to_learner, name='demerit_to_learner'),

    path('<slug:slug>/merit/select-grade/', views.add_discipline_action_to_grade, name='select_merit_grade'),
    path('<slug:slug>/demerit/select-grade/', views.add_discipline_action_to_grade, name='select_demerit_grade'),

    path('<slug:slug>/merit/list/', views.DisciplineActionList.as_view(), name='merit_list'),
    path('<slug:slug>/demerit/list/', views.DisciplineActionList.as_view(), name='demerit_list'),

    path('<slug:teacher_slug>/merit/<int:pk>/update/',
         views.DisciplineActionUpdate.as_view(), name='update_merit_action'),
    path('<slug:teacher_slug>/demerit/<int:pk>/update',
         views.DisciplineActionUpdate.as_view(), name='update_demerit_action'),

    path('<slug:teacher_slug>/merit/<int:pk>/delete/',
         views.DisciplineActionDelete.as_view(), name='delete_merit_action'),
    path('<slug:teacher_slug>/demerit/<int:pk>/delete/',
         views.DisciplineActionDelete.as_view(), name='delete_demerit_action'),

    path('ajax/load-learners/', ajax_views.load_learners, name='ajax_load_learners'),
    path('ajax/load-discipline-actions/',
         ajax_views.load_discipline_actions_for_grade,
         name='load_discipline_actions'),
]