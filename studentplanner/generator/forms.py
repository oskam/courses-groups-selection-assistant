import datetime
from django import forms
from schedules.models import Group


class SemestersGeneratorForm(forms.Form):
    semesters = forms.MultipleChoiceField(
        label='Wybierz semestry.',
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        degree = kwargs['initial'].get('degree', None)
        self.fields['semesters'].choices = degree.semester_choices()

    def clean_semesters(self):
        return list(map(lambda x: int(x), self.cleaned_data['semesters']))


class CoursesGeneratorForm(forms.Form):
    courses = forms.MultipleChoiceField(
        label='Wybierz kursy, które chcesz zrealizować.',
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        courses = kwargs['initial'].get('courses', [])
        choices = ((c.id, c.name_semester_str()) for c in courses)
        self.fields['courses'].choices = choices

    def clean_courses(self):
        return list(map(lambda x: int(x), self.cleaned_data['courses']))


class LecturersGeneratorForm(forms.Form):
    loved_lecturers = forms.MultipleChoiceField(
        label='Wybierz prowadzących, z którymi chciałbyś mieć zajęcia.',
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    hated_lecturers = forms.MultipleChoiceField(
        label='Wybierz prowadzących, których wolałbyś uniknąć.',
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lecturers = kwargs['initial'].get('lecturers', [])
        choices_loved = ((l.id, str(l)) for l in lecturers)
        choices_hated = ((l.id, str(l)) for l in lecturers)
        self.fields['loved_lecturers'].choices = choices_loved
        self.fields['hated_lecturers'].choices = choices_hated

    def clean(self):
        loved_lecturers = list(map(lambda x: int(x), self.cleaned_data['loved_lecturers']))
        hated_lecturers = list(map(lambda x: int(x), self.cleaned_data['hated_lecturers']))
        return dict(loved_lecturers=loved_lecturers, hated_lecturers=hated_lecturers)


def periods_generator():
    yield ('{}_{}'.format(Group.START_TIME_CHOICES[0][0], Group.END_TIME_CHOICES[-1][0]), 'cały dzień')
    for (start, end) in zip(Group.START_TIME_CHOICES, Group.END_TIME_CHOICES):
        yield ('{}_{}'.format(start[0], end[0]), '{} - {}'.format(start[1], end[1]))


def parse_periods(values):
    for value in values:
        start, end = value.split(sep='_', maxsplit=1)
        start_time = datetime.datetime.strptime(start, '%H:%M:%S').time()
        end_time = datetime.datetime.strptime(end, '%H:%M:%S').time()
        if not (start_time == Group.START_TIME_CHOICES[0][0] and end_time == Group.END_TIME_CHOICES[-1][0]):
            yield (start_time, end_time)


class TimeGeneratorForm(forms.Form):
    days = Group.DAY_CHOICES[1:6]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.update({
            name: forms.MultipleChoiceField(label=str(label).title(),
                                            widget=forms.CheckboxSelectMultiple,
                                            choices=list(periods_generator()),
                                            required=False)
            for (name, label) in self.days
        })

    def clean(self):
        return dict(hated_periods={
            key: list(parse_periods(value)) for key, value in self.cleaned_data.items()
        })


class TimeTableForm(forms.Form):
    name = forms.CharField(label='Nazwa (wybierz pole poniżej, aby zmienić nazwę na własną)', required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_table = kwargs['initial'].get('time_table', None)
