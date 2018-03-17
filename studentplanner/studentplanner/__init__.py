def parse_forms(form_list):
    values = dict()
    for form in form_list:
        values.update(form.cleaned_data)
    return values