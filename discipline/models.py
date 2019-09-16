# import datetime
#
# from django.db import models
# from django.core.validators import MaxValueValidator
# from django.shortcuts import reverse
# from django.utils.text import slugify
#
# from users.models import Learner, Teacher
#
#
# class MeritManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(is_merit=True)
#
#
# class DemeritManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(is_demerit=True)
#
#
# class Discipline(models.Model):
#     MAXIMUM_POINT = 10
#     MERIT = 'M'
#     DEMERIT = 'D'
#     DISCIPLINE_CHOICES = (
#         (MERIT, 'Merit'),
#         (DEMERIT, 'Demerit'),
#     )
#     discipline_type = models.CharField(max_length=1, choices=DISCIPLINE_CHOICES)
#     code = models.CharField(max_length=7, unique=True)
#     description = models.CharField(max_length=250)
#     point = models.PositiveIntegerField(validators=[MaxValueValidator(MAXIMUM_POINT)])
#     slug = models.SlugField()
#     objects = models.Manager()
#     merits = MeritManager()
#     demerits = DemeritManager()
#
#     class Meta:
#         ordering = ('point', 'code')
#
#     def __str__(self):
#         return self.code
#
#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.code)
#
#     def get_absolute_url(self):
#         return reverse('discipline:detail', args=[self.slug])
#
#     def get_update_url(self):
#         return reverse('discipline:update', args=[self.slug])
#
#     def get_delete_url(self):
#         return reverse('discipline:delete', args=[self.slug])
#
#     @property
#     def is_merit(self):
#         return self.discipline_type == self.MERIT
#
#     @property
#     def is_demerit(self):
#         return self.discipline_type == self.DEMERIT
#
#
# def get_discipline_action_time():
#     return datetime.datetime.now()
#
#
# class DisciplineAction(models.Model):
#     action = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='discipline_action')
#     learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name='discipline_action')
#     teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='discipline_action')
#     time = models.DateTimeField(default=get_discipline_action_time)
#
#     class Meta:
#         ordering = ('-time',)
