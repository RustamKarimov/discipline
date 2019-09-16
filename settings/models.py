from django.db import models


class Settings(models.Model):
    """
    Settings for admin. Will be created automatically with defaults during first visit of dashboard page
    """
    DEFAULT_DIVISION = 'Grade'
    DEFAULT_MAX_SECTION = 12
    UPDATE_GRADES = True
    ALLOW_ALUMNI = True
    ALLOW_TRANSFER = True
    ALLOW_EXPULSION = True

    division = models.CharField(default=DEFAULT_DIVISION,
                                max_length=25)
    update_grades = models.BooleanField(default=UPDATE_GRADES,
                                        verbose_name='Move learners to the next grade '
                                                     'at the start of the new academic year.')
    last_section = models.PositiveIntegerField(help_text='Learners will not be updated for the next academic '
                                                         'year after this division.',
                                               default=DEFAULT_MAX_SECTION)
    allow_alumni = models.BooleanField(default=ALLOW_ALUMNI,
                                       verbose_name='Move learners in the last section to alumni section at the'
                                                    ' end of academic year. ')
    allow_transfers = models.BooleanField(default=ALLOW_TRANSFER,
                                          verbose_name='Add learner to transferred section in case of de-registration')
    allow_expulsion = models.BooleanField(default=ALLOW_EXPULSION,
                                          verbose_name='Add learner to expelled section in case of expulsion.')