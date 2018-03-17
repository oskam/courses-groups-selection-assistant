from django.contrib import messages
from django.contrib.auth import get_user
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView, ListView

from django.contrib.auth.mixins import LoginRequiredMixin
from formtools.wizard.views import SessionWizardView

from schedules.models import Faculty, FieldOfStudy, Group
from students.forms import FacultyStudentForm, FieldOfStudyStudentForm, DegreeStudentForm
from students.models import Student, StudentTimeTable
from studentplanner import parse_forms


class StudentEditWizardView(LoginRequiredMixin, SessionWizardView):
    template_name = "students/student_form.html"
    form_list = [
        FacultyStudentForm,
        DegreeStudentForm,
        FieldOfStudyStudentForm
    ]

    def get_form_initial(self, step):
        initial = {'user': get_user(self.request)}
        if step == '0':
            faculties = Faculty.objects.all()
            if not faculties:
                faculties = Faculty.objects.none()
            initial.update({'faculties': faculties})
        if step == '2':
            step0_data = self.get_cleaned_data_for_step('0')
            step1_data = self.get_cleaned_data_for_step('1')
            faculty = step0_data.get('faculty', None)
            degree = step1_data.get('degree', None)
            fields_of_study = FieldOfStudy.objects.filter(faculty=faculty,
                                                          degree=degree)
            if not fields_of_study:
                fields_of_study = FieldOfStudy.objects.none()
            initial.update({'fields_of_study': fields_of_study})
        return initial

    def done(self, form_list, **kwargs):
        user = get_user(self.request)

        values = parse_forms(form_list)
        faculty = values.get('faculty', None)
        field_of_study = values.get('field_of_study', None)
        if not faculty or not field_of_study:
            return redirect('students:student_edit')

        Student.objects.update_or_create(user=user,
                                         defaults=dict(
                                             faculty=faculty,
                                             field_of_study=field_of_study
                                         ))

        return redirect('students:student_view')


class StudentView(LoginRequiredMixin, TemplateView):
    template_name = "students/student_detail.html"


class StudentTimetablesListView(LoginRequiredMixin, ListView):
    template_name = "students/student_time_tables_list.html"
    model = StudentTimeTable

    def get_queryset(self):
        user = get_user(self.request)
        timetables = super().get_queryset()
        try:
            timetables = timetables.filter(student=user.student)
        except Student.DoesNotExist:
            timetables = timetables.none()
        return timetables


class StudentTimetableView(LoginRequiredMixin, TemplateView):
    template_name = "students/student_time_table.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_user(self.request)
        time_table_id = kwargs.get('time_table_id', None)
        try:
            student_timetable = StudentTimeTable.objects.get(id=time_table_id)
            if student_timetable.student != user.student:
                raise ValueError
            context['timings'] = Group.START_TIME_CHOICES
            context['time_table'] = student_timetable.time_table
            context['name'] = student_timetable.name
        except (ObjectDoesNotExist, ValueError):
            context['time_table'] = None
            messages.add_message(self.request, messages.WARNING, 'Plan z podanym id nie istnieje '
                                                                 'lub nie masz do niego uprawnień.')
        return context


class StudentTimetableDeleteView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        time_table_id = kwargs.get('time_table_id', None)
        student_timetable = StudentTimeTable.objects.get(id=time_table_id)
        if student_timetable.student == user.student:
            timetable = student_timetable.time_table
            name = student_timetable.name
            student_timetable.delete()
            timetable.delete()
            messages.add_message(request, messages.SUCCESS, 'Plan "{}" został usunięty.'.format(name))
        else:
            messages.add_message(request, messages.WARNING, 'Możesz usuwać tylko swoje plany.')
        return redirect('students:timetables_list')
