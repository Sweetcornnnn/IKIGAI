from django import forms
from .models import Habit


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'description', 'icon']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your habit...'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter habit name...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Habit Name'
        self.fields['description'].label = 'Description (optional)'
        self.fields['icon'].label = 'Icon'