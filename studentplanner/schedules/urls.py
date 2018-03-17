from django.conf.urls import url
from . import views

app_name = 'schedules'

urlpatterns = [
    url(r"^$", views.list, name="json_list"),
]