from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    """
    Form for creating and editing tasks
    """

    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    day = forms.ChoiceField(choices=DAY_CHOICES, label='Day', required=False)

    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'priority', 'due_date', 'day']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'What do you want to accomplish?'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add details about this task...'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Task Name'
        self.fields['description'].label = 'Description'
        self.fields['category'].label = 'Category'
        self.fields['priority'].label = 'Priority'
        self.fields['due_date'].label = 'Due Date'
        self.fields['day'].label = 'Day'
        self.fields['day'].required = False