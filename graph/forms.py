from django import forms
from django.forms import ChoiceField,MultipleChoiceField,IntegerField

class AnnotationsForm(forms.Form):
    def __init__(self, options=None, *args, **kwargs):
        super(AnnotationsForm, self).__init__(*args, **kwargs)
        self.fields['annotation'].choices = options

    annotation = ChoiceField(choices=(),required=True)
    header = IntegerField(required=False)
    
class GraphForm(forms.Form):
    def __init__(self, options=None, *args, **kwargs):
        super(GraphForm, self).__init__(*args, **kwargs)
        self.fields['x'].choices = options
        self.fields['y'].choices = options

    x = ChoiceField(choices=(),required=True)
    y = MultipleChoiceField(choices=(),required=True)