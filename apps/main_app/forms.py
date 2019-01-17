from django import forms

COUNT_CHOICES = (20, '20'), (30, '30'), (40, '40'), (50, '50')
# グーグル検索数を表す。1ページ10サイト単位、10件だけだと少なすぎるし、50以上は必要ない。


class IndexFrom(forms.Form):
    def __init__(self, *args, **kwargs):
        """親クラスのForm初期値を呼び出し、classにform-controlを適用させている。
            これによってformのみの記入で全体にbootstrapを効かせることが出来る
        """
        super(IndexFrom, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = "form-control"

    search_keyword = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '検索キーワードを入力してください'}),
        label='search_keyword',
        max_length=255,
        required=True,

    )
    search_count = forms.ChoiceField(
        label='search_count',
        widget=forms.Select,
        choices=COUNT_CHOICES,
        required=False
    )

    input_task_id = forms.CharField(
        # このフォームにはviewsから動的に初期値が渡される様になってある
        widget=forms.TextInput(attrs={'placeholder': 'task_id'}),
        label='input_task_id',
        max_length=255,
        required=False,

    )

    input_unique_id = forms.CharField(
        # このフォームにはviewsから動的に初期値が渡されるようになってある
        widget=forms.TextInput(attrs={'placeholder': 'unique_id'}),
        label='input_unique_id',
        max_length=255,
        required=False,

    )
