from schedules.models import Lecturer
from django.core import serializers
from django.http import JsonResponse

# Create your views here.
def list(request):
    queryset = Lecturer.objects.all()
    queryset = serializers.serialize('json', queryset)
    return JsonResponse(queryset, safe=False)