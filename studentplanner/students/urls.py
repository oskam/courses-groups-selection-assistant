from django.conf.urls import url
from students.views import (
    StudentView,
    StudentEditWizardView,
    StudentTimetablesListView,
    StudentTimetableView,
    StudentTimetableDeleteView
)

urlpatterns = [
    url(r"^$", StudentView.as_view(), name="student_view"),
    url(r"^edit/$", StudentEditWizardView.as_view(), name="student_edit"),
    url(r"^timetables/$", StudentTimetablesListView.as_view(), name="timetables_list"),
    url(r"^timetables/(?P<time_table_id>[0-9]+)/$", StudentTimetableView.as_view(), name="timetable"),
    url(r"^timetables/(?P<time_table_id>[0-9]+)/delete/$", StudentTimetableDeleteView.as_view(), name="timetable_delete"),
]
