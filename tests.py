from django.test import TestCase
from message.models import Message
from message.forms import MessageForm
from sharer.models import Sharer, Address
from sharezone.models import Sharezone
from django.contrib.auth.models import User as DJUser
from user.models import User

class MessageTest(TestCase):
    """
    Tests for the Message Model and Message Forms.
    """

    def setUp(self):
        """
        Initializes data for the ModelTests.
        """
        address1 = Address.objects.create(address_line_1="42 Life St.",
                                          address_line_2='',
                                          city="Rochester",
                                          state="NY",
                                          zip_code="14623")

        address2 = Address.objects.create(address_line_1="43 Life St.",
                                          address_line_2='',
                                          city="Rochester",
                                          state="NY",
                                          zip_code="14623")

        address3 = Address.objects.create(address_line_1="43 Life St.",
                                          address_line_2='',
                                          city="Rochester",
                                          state="NY",
                                          zip_code="14623")

        admin = DJUser.objects.create_user("admin", "admin@rit.edu", "password")
        self.admin = User.objects.create(django_user=admin, address=address1)

        self.sharezone = Sharezone.objects.create(name="Rochester Institute of Technology",
                                                  description="A University in Rochester")
        self.sharezone.admin.add(admin)

        dj_user1 = DJUser.objects.create_user("tom", "tom@rit.edu", "password")
        dj_user2 = DJUser.objects.create_user("jerry", "jerry@rit.edu", "password")

        self.user1 = User.objects.create(django_user=dj_user1, address=address2)
        self.user2 = User.objects.create(django_user=dj_user2, address=address3)

        sharer1 = Sharer.objects.get(pk=self.user1.id)
        sharer2 = Sharer.objects.get(pk=self.user2.id)

        sharer1.sharezone = self.sharezone
        sharer1.sharezone = self.sharezone

        sharer1.save()
        sharer2.save()

    def test_message(self):
        """
        Tests that Message objects can be created and stored in the database.
        """
        message = Message.objects.create(from_user=self.user1, to_user=self.user2,
                                         message="Hi Jerry! :)", sharezone=self.sharezone)

        self.assertEqual(self.user1, message.from_user)
        self.assertEqual(self.user2, message.to_user)
        self.assertEqual("Hi Jerry! :)", message.message)
        self.assertEqual(self.sharezone, message.sharezone)

    def test_valid_form(self):
        """
        Tests that a form with a specified username and message is valid.
        """
        content = {"to_username": "jerry", "message": "Hello World!"}

        valid_form = MessageForm(self.user1, content)

        self.assertTrue(valid_form.is_valid())

    def test_empty_form(self):
        """
        Tests that an empty form is invalid.
        """
        empty_form = MessageForm(self.user1)

        self.assertFalse(empty_form.is_valid())

    def test_missing_info_forms(self):
        """
        Tests that forms missing information (username or no message) are invalid.
        """
        no_username = {"message": "Bonjour!"}
        no_username_form = MessageForm(self.user1, no_username)

        no_message = {"to_username": "jerry"}
        no_message_form = MessageForm(self.user1, no_message)

        self.assertFalse(no_username_form.is_valid())
        self.assertFalse(no_message_form.is_valid())

    def test_to_yourself_form(self):
        """
        Tests that forms sending a message to yourself are invalid.
        """
        to_yourself = {"to_username": "tom", "message": "Hi me!"}
        to_yourself_form = MessageForm(self.user1, to_yourself)

        self.assertFalse(to_yourself_form.is_valid())

    def test_different_sharezone_form(self):
        """
        Tests that forms sending a message to users in different ShareZones are
        invalid.
        """
        address = Address.objects.create(address_line_1="43 Life St.",
                                         address_line_2='',
                                         city="Rochester",
                                         state="NY",
                                         zip_code="14623")

        djuser = DJUser.objects.create_user("mickey", "mickey@uofr.edu", "password")
        different_sharezone_user = User.objects.create(django_user=djuser, address=address)

        sharezone2 = Sharezone.objects.create(name="University of Rochester", 
                                              description="Another University in Rochester")
        sharezone2.admin.add(djuser)

        sharer = Sharer.objects.get(pk=different_sharezone_user.id)
        sharer.sharezone = sharezone2
        sharer.save()

        different_sharezone1 = {"to_username": "tom", "message": \
                                "I shouldn't be able to send a message to you :("}
        different_sharezone1_form = MessageForm(different_sharezone_user, 
                                                different_sharezone1)

        different_sharezone2 = {"to_username": "mickey", "message": \
                                "I shouldn't be able to send a message to you :("}
        different_sharezone2_form = MessageForm(self.user1, different_sharezone2)

        self.assertFalse(different_sharezone2_form.is_valid())
        self.assertFalse(different_sharezone1_form.is_valid())

    def test_userDNE_form(self):
        """
        Tests that forms sending a message to a user that does not exist are
        invalid.
        """
        user_DNE = {"to_username": "keyboard_smash", "message": "dskljdapwjpi"}
        user_DNE_form = MessageForm(self.user1, user_DNE)

        self.assertFalse(user_DNE_form.is_valid())
