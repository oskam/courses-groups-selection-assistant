from django import forms
from students.models import Student
from schedules.models import FieldOfStudy


class FacultyStudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ('faculty',)

        faculty = forms.ModelChoiceField(queryset=...,
                                         required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs['initial'].get('user', None)
        choices = kwargs['initial'].get('faculties', [])
        self.fields['faculty'].queryset = choices
        if hasattr(user, 'student') and user.student.faculty in choices:
                self.fields['faculty'].initial = user.student.faculty
                self.fields['faculty'].empty_label = None
        else:
            self.fields['faculty'].empty_label = 'Wybierz wydział...'


class DegreeStudentForm(forms.Form):
    degree = forms.ChoiceField(label='Stopień',
                               choices=FieldOfStudy.DEGREE_CHOICES)


class FieldOfStudyStudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ('field_of_study',)

        field_of_study = forms.ModelChoiceField(queryset=...,
                                                required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs['initial'].get('user', None)
        choices = kwargs['initial'].get('fields_of_study', [])
        self.fields['field_of_study'].queryset = choices
        self.fields['field_of_study'].empty_label = None
        if hasattr(user, 'student') and user.student.field_of_study in choices:
            self.fields['field_of_study'].initial = user.student.field_of_study
