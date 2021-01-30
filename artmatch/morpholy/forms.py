from django import forms


class MorpholyForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea,
    label="解析対象")

    select_part = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=[
            ("noun", "名詞"), ("verb", "動詞"), ("adjective", "形容詞"), ],
        label="出力項目")
