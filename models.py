from django.db import models
from sharer.models import Sharer
from sharezone.models import Sharezone

class Message(models.Model):
    """
    The Message Model with the attributes from_user (Sharer), to_user (Sharer),
    timestamp (DateTimeField), and message (CharField).
    """
    from_user = models.ForeignKey(Sharer, related_name='message_from')
    to_user = models.ForeignKey(Sharer, related_name='message_to')
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=1000)
    read = models.BooleanField(default=False)
    sharezone = models.ForeignKey(Sharezone)

    def __str__(self):
        """
        A to-string method that displays the Message object in a readable
        format.
        """
        return 'From: ' + self.from_user.name + '\n' \
               'To: ' + self.to_user.name + '\n'     \
               'Message: ' + self.message + '\n' \

    @classmethod
    def sendConfirm(cls, transaction):
        """
        Sends a message to the recieving user to confirm the transaction
        """
        sender = transaction.sharezone.getShedSender()
        link = "/transaction/confirm/" + str(transaction.id)
        message =   "Please confirm that you recieved a " + str(transaction.tool) \
                    + ' from ' + str(transaction.from_user.name) + "\n" \
                    + "<a href='" + link + "'>Confirm</a>"
        confirm_message = Message(  from_user=sender, \
                                    to_user=transaction.to_user, \
                                    sharezone=transaction.sharezone, \
                                    message=message)
        confirm_message.save()