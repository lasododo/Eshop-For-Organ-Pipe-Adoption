from django import forms


class UploadFileForm(forms.Form):
    """
    <input type="file" name="chooseFile" id="chooseFile">
    """
    file = forms.FileField(widget=forms.FileInput(attrs={
        'id': 'chooseFile'
    }), label='')
