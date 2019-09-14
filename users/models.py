from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class TeacherManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_teacher=True)


class LearnerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_learner=True)


class User(AbstractUser):
    image = models.ImageField(upload_to='users', default='users/no_image.png')
    user_id = models.CharField(max_length=10, unique=True)
    slug = models.SlugField()
    is_teacher = models.BooleanField(default=False)
    is_learner = models.BooleanField(default=False)
    objects = models.Manager()
    teachers = TeacherManager()
    learners = LearnerManager()

    class Meta:
        ordering = ('last_name', 'first_name')

    def __str__(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        slug_str = f"{self.get_full_name()} {self.user_id}"
        self.slug = slugify(slug_str)

        self.last_name = self.last_name.uppercase()

        self.username = self.user_id
        return super().save(*args, **kwargs)


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher')
    # form_class = models.ManyToManyField(Grade, related_name='teachers', blank=True)

    class Meta:
        ordering = ('user__last_name', 'user__first_name')

    def __str__(self):
        return self.user.get_full_name()


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner')
    # grades = models.ManyToManyField(Grade, related_name='learners', blank=True)
    is_alumni = models.BooleanField(default=False)
    is_transferred = models.BooleanField(default=False)
    is_expelled = models.BooleanField(default=False)
    leave_year = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ('user',)

    def __str__(self):
        return self.user.get_full_name()