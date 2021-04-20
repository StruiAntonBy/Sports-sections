from django import forms

class UserForm(forms.Form):
    surname = forms.CharField(max_length=50)
    name = forms.CharField(max_length=50)
    middle_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    image = forms.ImageField()
    login = forms.CharField(max_length=20)
    phone_number = forms.CharField(max_length=9, min_length=9)
    password = forms.CharField(min_length=12)
    repeat_password = forms.CharField(min_length=12)

    def is_valid(self):
        valid = super(UserForm, self).is_valid()

        if not valid:
            return valid

        if self.cleaned_data['password'] != self.cleaned_data['repeat_password']:
            return False

        return True

class EditUserForm(forms.Form):
    surname = forms.CharField(max_length=50)
    name = forms.CharField(max_length=50)
    middle_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    login = forms.CharField(max_length=20)
    phone_number = forms.CharField(max_length=9, min_length=9)
    user_id = forms.IntegerField()

    def is_valid(self):
        valid = super(EditUserForm, self).is_valid()

        if not valid:
            return valid

        if not self.cleaned_data['phone_number'].isdigit():
            return False

        return True

class LessonForm(forms.Form):
    start_time = forms.TimeField()
    end_time = forms.TimeField()
    description = forms.CharField(max_length=200)

    def is_valid(self):
        valid = super(LessonForm, self).is_valid()

        if not valid:
            return valid

        if self.cleaned_data['start_time'] >= self.cleaned_data['end_time']:
            return False

        return True

class SectionForm(forms.Form):
    name = forms.CharField(max_length=50)
    description = forms.CharField()
    progress = forms.CharField()
    beginner = forms.CharField()