from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    """
    Form for creating and editing tasks
    """

    # Custom day selector for weekly view
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    day = forms.ChoiceField(choices=DAY_CHOICES, label='Day', required=True)

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'day']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add details about this task...'}),
            'title': forms.TextInput(attrs={'placeholder': 'What do you want to accomplish?'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Task Name'
        self.fields['description'].label = 'Description (optional)'
        self.fields['priority'].label = 'Priority'
        self.fields['day'].label = 'Which day?'