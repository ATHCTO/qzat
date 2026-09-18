from django import forms

from core.models.core import Goal


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'description', 'start_datetime', 'due_datetime', 'status', 'notes']
        widgets = {
            'start_datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'due_datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        due_datetime = cleaned_data.get('due_datetime')

        # التحقق من أن تاريخ الاستحقاق/النهاية بعد تاريخ البدء
        if start_datetime and due_datetime:
            if due_datetime <= start_datetime:
                self.add_error('due_datetime', 'يجب أن يكون تاريخ وقت الاستحقاق بعد تاريخ وقت البدء.')

        return cleaned_data