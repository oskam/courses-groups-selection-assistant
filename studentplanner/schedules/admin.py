from django.contrib import admin
from .models import Faculty, FieldOfStudy, Group, Course, Lecturer, TimeTable

# Register your models here.
admin.site.register(Faculty)
admin.site.register(FieldOfStudy)
admin.site.register(Group)
admin.site.register(Lecturer)
admin.site.register(Course)
admin.site.register(TimeTable)