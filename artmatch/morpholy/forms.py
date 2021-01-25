from django import forms


class MorpholyForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    select_part = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=[
            ("noun", "名詞"), ("verb", "動詞"), ("adjective", "形容詞"), ])
