from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class TestPage(TemplateView):
    template_name = 'test.html'

class ThanksPage(TemplateView):
    template_name = 'thanks.html'

class HomePage(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'