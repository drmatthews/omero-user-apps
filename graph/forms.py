from django import forms
from django.forms import ChoiceField,MultipleChoiceField,IntegerField

class PreviewForm(forms.Form):
    def __init__(self, options=None, *args, **kwargs):
        super(PreviewForm, self).__init__(*args, **kwargs)
        self.fields['preview_annotation'].choices = options

    preview_annotation = ChoiceField(choices=(),required=True)
    preview_sheet = IntegerField(required=False,min_value=0)
    
class AnnotationsForm(forms.Form):
    def __init__(self, options=None, *args, **kwargs):
        super(AnnotationsForm, self).__init__(*args, **kwargs)
        self.fields['annotation'].choices = options

    annotation = ChoiceField(choices=(),required=True)
    header = IntegerField(required=False,min_value=0)
    sheet = IntegerField(required=False,min_value=0)
    
class GraphForm(forms.Form):
    def __init__(self, options=None, *args, **kwargs):
        super(GraphForm, self).__init__(*args, **kwargs)
        self.fields['x'].choices = options
        self.fields['y'].choices = options

    x = ChoiceField(choices=(),required=True)
    y = MultipleChoiceField(choices=(),required=True)