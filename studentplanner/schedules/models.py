import datetime
import math

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

# Create your models here.
from schedules.enums import Degree


class Faculty(models.Model):
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=16, unique=True)

    class Meta:
        verbose_name = "Wydział"
        verbose_name_plural = "Wydziały"

    def __str__(self):
        return '[{}] {}'.format(self.code, self.name)


class FieldOfStudy(models.Model):
    DEGREE_CHOICES = (
        ('BSC', "I stopień inżynierskie"),
        ('BCH', "I stopień licencjackie"),
        ('MST', "II stopień licencjackie"),
        ('MSC', "II stopień inżynierskie"),
    )

    name = models.CharField(max_length=128)
    faculty = models.ForeignKey('Faculty', on_delete=models.CASCADE, related_name='fields_of_study')
    degree = models.CharField(choices=DEGREE_CHOICES, default=DEGREE_CHOICES[0][0], max_length=3)

    class Meta:
        verbose_name = "Kierunek"
        verbose_name_plural = "Kierunki"

    def __str__(self):
        return '/'.join([self.faculty.code, self.name])

    def human_str(self):
        return ', '.join([self.name, self.get_degree_display()])


class Course(models.Model):
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=16, unique=True)
    field_of_study = models.ForeignKey('FieldOfStudy', on_delete=models.CASCADE, related_name='courses')
    semester = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(7)])

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kursy"

    def clean(self):
        if self.semester not in Degree[self.field_of_study.degree].value:
            raise ValidationError("Semester not in expected range for selected degree")

    def name_semester_str(self):
        return '{}, semestr {}'.format(self.name, self.semester)

    def __str__(self):
        return '/'.join([str(self.field_of_study), '[{}]{}'.format(self.code, self.name)])


class Lecturer(models.Model):
    TITLE_CHOICES = (
        (0, 'lic.'),
        (1, 'inż.'),
        (2, 'mgr'),
        (3, 'mgr inż.'),
        (4, 'dr'),
        (5, 'dr inż.'),
        (6, 'dr hab.'),
        (7, 'dr hab. inż.'),
        (8, 'prof. dr hab.'),
        (10, 'prof dr hab. inż'),

    )
    title = models.IntegerField(choices=TITLE_CHOICES)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "Prowadzący"
        verbose_name_plural = "Prowadzący"

    def __str__(self):
        return " ".join([self.get_title_display(), self.first_name, self.last_name])


class Group(models.Model):
    LECTURE = 'W'
    EXERCISES = 'C'
    LAB = 'L'
    PROJECT = 'P'
    SEMINARY = 'S'
    TYPE_CHOICES = (
        (LECTURE, 'wykład'),
        (EXERCISES, 'ćwiczenia'),
        (LAB, 'laboratorium'),
        (PROJECT, 'projekt'),
        (SEMINARY, 'seminarium'),
    )

    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    DAY_CHOICES = (
        (None, 'wybierz dzień zajęć'),
        (MONDAY, 'poniedziałek'),
        (TUESDAY, 'wtorek'),
        (WEDNESDAY, 'środa'),
        (THURSDAY, 'czwartek'),
        (FRIDAY, 'piątek'),
        (SATURDAY, 'sobota'),
        (SUNDAY, 'niedziela'),
    )
    START_TIME_CHOICES = (
        (datetime.time(7, 30, 00), '7:30'),
        (datetime.time(8, 15, 00), '8:15'),
        (datetime.time(9, 15, 00), '9:15'),
        (datetime.time(10, 15, 00), '10:15'),
        (datetime.time(11, 15, 00), '11:15'),
        (datetime.time(12, 15, 00), '12:15'),
        (datetime.time(13, 15, 00), '13:15'),
        (datetime.time(14, 15, 00), '14:15'),
        (datetime.time(15, 15, 00), '15:15'),
        (datetime.time(16, 10, 00), '16:10'),
        (datetime.time(17, 5, 00), '17:05'),
        (datetime.time(18, 00, 00), '18:00'),
        (datetime.time(18, 55, 00), '18:55'),
        (datetime.time(19, 50, 00), '19:50'),
    )
    END_TIME_CHOICES = (
        (datetime.time(8, 15, 00), '8:15'),
        (datetime.time(9, 00, 00), '9:00'),
        (datetime.time(10, 00, 00), '10:00'),
        (datetime.time(11, 00, 00), '11:00'),
        (datetime.time(12, 00, 00), '12:00'),
        (datetime.time(13, 00, 00), '13:00'),
        (datetime.time(14, 00, 00), '14:00'),
        (datetime.time(15, 00, 00), '15:00'),
        (datetime.time(16, 00, 00), '16:00'),
        (datetime.time(16, 55, 00), '16:55'),
        (datetime.time(17, 50, 00), '17:50'),
        (datetime.time(18, 45, 00), '18:45'),
        (datetime.time(19, 40, 00), '19:40'),
        (datetime.time(20, 35, 00), '20:35'),
    )

    NORMAL = "PN"
    EVEN = "P"
    ODD = "N"
    WEEK_TYPE_CHOICES = (
        (NORMAL, 'normalny'),
        (EVEN, 'parzysty'),
        (ODD, 'nieparzysty'),
    )

    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='groups')
    code = models.CharField(max_length=16)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    lecturer = models.ForeignKey('Lecturer', on_delete=models.CASCADE, null=True, blank=True, default=None)
    start_time = models.TimeField(choices=START_TIME_CHOICES)
    end_time = models.TimeField(choices=END_TIME_CHOICES)
    day = models.IntegerField(choices=DAY_CHOICES)
    week_type = models.CharField(max_length=2, choices=WEEK_TYPE_CHOICES, default=NORMAL)
    place = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Grupa"
        verbose_name_plural = "Grupy"
        unique_together = ("code", "start_time", "end_time", "day", "week_type")

    @property
    def template_start(self):
        today = datetime.datetime.today().date()
        start = datetime.datetime.combine(today, self.start_time)
        first = datetime.datetime.combine(today, Group.START_TIME_CHOICES[0][0])
        delta = start - first
        return int(math.ceil((delta.total_seconds() / 60)))

    @property
    def template_width(self):
        today = datetime.datetime.today().date()
        start = datetime.datetime.combine(today, self.start_time)
        end = datetime.datetime.combine(today, self.end_time)
        delta = end - start
        return int(math.ceil((delta.total_seconds() / 60)))

    @property
    def times(self):
        return "{}-{}".format(self.get_start_time_display(), self.get_end_time_display())

    def template_string(self):
        return ', '.join([
            self.course.name,
            self.get_type_display()
        ])

    def __str__(self):
        return '/'.join([
            str(self.course),
            '; '.join([
                '[{}]{}'.format(self.code, self.type),
                str(self.lecturer) if self.lecturer else "prowadzący nieznany",
                "{} {}-{} ({})".format(self.get_day_display(), self.start_time, self.end_time, self.week_type),
            ])
         ])

    def __repr__(self):
        return "<Group {} {}>".format(self.code, self.type)


class TimeTable(models.Model):
    field_of_study = models.ForeignKey('FieldOfStudy', on_delete=models.CASCADE, related_name='time_tables')
    groups = models.ManyToManyField('Group', related_name='time_tables')
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Plan zajęć"
        verbose_name_plural = "Plany zajęć"

    @property
    def local_date_created(self):
        return timezone.localtime(self.date_created)

    def template_groups_dict(self):
        return {
            day: {
                'name': name,
                'groups': self.groups.filter(day=day).order_by('start_time')
            }
            for (day, name) in Group.DAY_CHOICES[1:6]
        }

    def __str__(self):
        return "Plan {}/{}/{}".format(self.id, self.field_of_study.name, self.local_date_created.strftime('%X, %d.%m.%Y'))
