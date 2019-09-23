from rolepermissions.permissions import register_object_checker
from school_discipline.roles import TeacherRole, LearnerRole


@register_object_checker()
def view_grade(role, user, grade):
    if role == TeacherRole and user.teacher in grade.teachers.all():
        return True

    return False
