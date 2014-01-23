from django import template
from message.models import Message

register = template.Library()

@register.filter(name='unread_messages')
def unread_messages(user):
    """
    A template tag that returns the user's number of unread messages.
    """
    messages = Message.objects.filter(to_user=user,read=False)

    return len(messages)