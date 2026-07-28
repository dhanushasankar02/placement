from django import forms
from apps.interviews.models import Interview

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['interview_date', 'location_or_link', 'round_number', 'round_name', 'status', 'result', 'feedback']
        widgets = {
            'interview_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location_or_link': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Online link or physical location'}),
            'round_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'round_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Coding Test, Technical HR'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'result': forms.Select(attrs={'class': 'form-control'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
