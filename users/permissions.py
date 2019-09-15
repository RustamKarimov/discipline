from rolepermissions.permissions import register_object_checker
from school_discipline.roles import TeacherRole, LearnerRole


@register_object_checker()
def view_teacher(role, user, teacher):
    if role == TeacherRole and user == teacher.user:
        return True

    return False


@register_object_checker()
def view_learner(role, user, learner):
    if role == LearnerRole and user == learner.user:
        return True

    # # todo: if user is teacher and learner in his grade return true
    # grade = learner.grades.filter(active=True).first()
    # if role == TeacherRole and grade in user.teacher.form_class.all():
    #     return True

    return False