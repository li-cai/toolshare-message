from django import forms
from django.db import models
from django.contrib.auth.models import User as DJUser
from django.utils.html import escape

from sharer.models import Sharer

import cgi

class MessageForm(forms.Form):
    """
    MessageForm is a Django form for sending Messages to another. It the generates
    a field for the username of the recipient (to_username) and a field for the
    contents of the message (message).
    These fields have a CSS class attribute of 'form-control' so that they look
    nice.
    """
    from_user = models.ForeignKey('Sharer')
    to_username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',
                  'placeholder':'Username', 'list':'usernames'}))

    message = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'placeholder':'Enter Message'}))

    def __init__(self, user, *args, **kwargs):
        """
        Constructor for MessageForm. The from_user of the message form is
        passed in as an argument.
        """
        self.from_user = user
        super(MessageForm, self).__init__(*args, **kwargs)

    def clean_to_username(self):
        """
        This method is called after the is_valid() default validation for the
        to_username field. The ValidationError is thrown when the username from
        the from does not exist or when the to-username is the same as the from-
        username. The string attached to the exception is used in the errorlist.
        """
        to_username = self.cleaned_data['to_username']

        if to_username == self.from_user.django_user.username:
            raise forms.ValidationError('You cannot send a message to yourself.')

        try:
            djuser = DJUser.objects.get(username=to_username)

            to_sharezone = Sharer.objects.get(pk=djuser.id).sharezone
            from_sharezone = self.from_user.sharezone

            if to_sharezone != from_sharezone:
                raise forms.ValidationError('Please enter a User in the same Sharezone.')

        except DJUser.DoesNotExist:
            raise forms.ValidationError('User does not exist. Please try again.')

        return to_username

    def clean_message(self):
        """
        Cleans input in message fields so that HTML is not rendered for messages
        sent from forms.
        """
        self.cleaned_data['message'] = cgi.escape(self.cleaned_data['message'])

        return self.cleaned_data['message']

    def is_valid(self):
        """
        Adds to the default is_valid() method: If the field has an error, the
        CSS class attribute is set to 'form-control error'.
        """
        form = forms.Form.is_valid(self)

        for f in self.errors:
            self.fields[f].widget.attrs.update({'class': 'form-control error'})

        return form
