import logging

from django.contrib import messages
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.views.generic import FormView
from formtools.wizard.views import SessionWizardView

from generator.forms import (
    SemestersGeneratorForm,
    CoursesGeneratorForm,
    LecturersGeneratorForm,
    TimeGeneratorForm,
    TimeTableForm
)
from generator.generator import Generator
from schedules.enums import Degree
from schedules.models import FieldOfStudy, Course, Group, Lecturer, TimeTable


# Create your views here.
from students.models import Student, StudentTimeTable


class GeneratorFormWizardView(LoginRequiredMixin, SessionWizardView):
    template_name = "generator/generator_form.html"
    form_list = [
        SemestersGeneratorForm,
        CoursesGeneratorForm,
        LecturersGeneratorForm,
        TimeGeneratorForm
    ]

    def dispatch(self, request, *args, **kwargs):
        try:
            user = get_user(request)
            _ = user.student
        except (AttributeError, Student.DoesNotExist):
            messages.add_message(request, messages.WARNING, 'Przed generowaniem planu zajęć stwórz profil studenta.')
            return redirect('students:student_view')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current in ['0', '1']:
            context.update({'required': True})
        else:
            context.update({'required': False})
        return context

    def get_form_initial(self, step):
        user = get_user(self.request)
        field_of_study = FieldOfStudy.objects.get(id=user.student.field_of_study_id)
        initial = dict()
        if step == '0':
            degree = Degree[field_of_study.degree]
            initial.update({'degree': degree})
        elif step == '1':
            step_data = self.get_cleaned_data_for_step('0')
            semesters = step_data.get('semesters', [])
            courses = Course.objects.filter(field_of_study=field_of_study,
                                            semester__in=semesters).order_by('semester', 'name')
            initial.update({'courses': courses})
        elif step == '2':
            step_data = self.get_cleaned_data_for_step('1')
            courses_ids = step_data.get('courses', [])
            groups = Group.objects.filter(course_id__in=courses_ids)
            lecturers = Lecturer.objects.filter(
                group__in=groups).distinct().order_by('last_name', 'first_name', 'title')
            initial.update({'lecturers': lecturers})
        return initial

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()

        student = get_user(self.request).student
        courses = Course.objects.filter(pk__in=data.get('courses', []))
        loved_lecturers = Lecturer.objects.filter(pk__in=data.get('loved_lecturers', []))
        hated_lecturers = Lecturer.objects.filter(pk__in=data.get('hated_lecturers', []))
        hated_periods = data.get('hated_periods', {})

        try:
            generator = Generator(student,
                                  courses=courses,
                                  loved_lecturers=loved_lecturers,
                                  hated_lecturers=hated_lecturers,
                                  hated_periods=hated_periods)

            time_table = generator.generate()
            return redirect('generator:timetable_view', time_table_id=time_table.id)
        except AttributeError:
            messages.add_message(self.request, messages.WARNING, 'Nie udało się znaleźć poprawnego planu dla '
                                                                 'wszystkich podanych kursów, zmniejsz ich ilość '
                                                                 'lub spróbuj ponownie.')
            return redirect('generator:form_view')
        except Exception as e:
            logging.exception("generator error: ")
            print(str(e))
            messages.add_message(self.request, messages.ERROR, 'Wystąpił nieznany błąd! Spróbuj ponownie '
                                                               'lub skontaktuj się z administratorem serwisu.')
            return redirect('generator:form_view')


class TimeTableView(LoginRequiredMixin, FormView):
    template_name = 'generator/generator_result.html'
    form_class = TimeTableForm

    def get(self, request, *args, **kwargs):
        time_table_id = kwargs.get('time_table_id', None)
        timings = Group.START_TIME_CHOICES
        try:
            time_table = TimeTable.objects.get(id=time_table_id)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.WARNING, 'Plan z podanym id nie istnieje.')
            time_table = None
        form = TimeTableForm(initial=dict(name=str(time_table), time_table=time_table))
        return self.render_to_response(self.get_context_data(form=form, timings=timings, time_table=time_table))

    def post(self, request, *args, **kwargs):
        time_table_id = kwargs.get('time_table_id', None)
        context = self.get_context_data()
        form = context['form']
        if form.is_valid():
            name = form.cleaned_data['name']
            print(name)
            user = get_user(request)
            try:
                time_table = TimeTable.objects.get(id=time_table_id)
                student_timetable = StudentTimeTable(student=user.student,
                                                     name=name,
                                                     time_table=time_table)
                student_timetable.save()
            except (AttributeError, Student.DoesNotExist):
                messages.add_message(request, messages.WARNING, 'Przed generowaniem planu zajęć stwórz profil studenta.')
                return redirect('students:student_view')
            except ObjectDoesNotExist:
                messages.add_message(request, messages.WARNING, 'Plan z podanym id nie istnieje.')
                return redirect('generator:timetable_view', time_table_id=time_table_id)

            return redirect('students:timetables_list')
        else:
            return self.render_to_response(context)
