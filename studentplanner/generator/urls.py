from django.conf.urls import url
from generator.views import GeneratorFormWizardView, TimeTableView

urlpatterns = [
    url(r"^$", GeneratorFormWizardView.as_view(), name="form_view"),
    url(r"^timetable/(?P<time_table_id>[0-9]+)/$", TimeTableView.as_view(), name="timetable_view"),
]
