from django.contrib.auth import get_user_model
from django.db import models
from django.core.urlresolvers import reverse
# Create your models here.


class Student(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    faculty = models.ForeignKey('schedules.Faculty', blank=False, on_delete=models.CASCADE, verbose_name="Wydział")
    field_of_study = models.ForeignKey('schedules.FieldOfStudy', blank=False, on_delete=models.CASCADE, verbose_name="Kierunek")

    def get_absolute_url(self):
        return reverse("students:student_update")

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Studenci"

    def __str__(self):
        return str(self.user)


class StudentTimeTable(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='student_time_tables')
    name = models.CharField(max_length=128, null=True, blank=True, default=None)
    time_table = models.ForeignKey('schedules.TimeTable', on_delete=models.PROTECT, related_name='time_table_student')

    class Meta:
        verbose_name = "Plan zajęć Studenta"
        verbose_name_plural = "Plany zajęć Studenta"

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.time_table)
