from django import forms
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as DJUser
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils import dateformat
from message.models import Message
from message.forms import MessageForm
from sharer.models import Sharer

@login_required(login_url='user.views.login')
def sendmessage(request):
    """
    Generates the view for sendmessage.html which displays a form for the User
    to send a message to another user. Upon submission, a Message object with
    the properties from_user, to_user, and message is created and stored in
    the database.
    """
    users = Sharer.objects.filter(sharezone=request.user.user.sharezone, _my_subclass='user'). \
                                  exclude(id=request.user.id)

    if request.method == 'POST':

        form = MessageForm(request.user.user, request.POST)

        if form.is_valid():
            from_user = request.user.user
            to_user = DJUser.objects.get(username=request.POST['to_username']).user
            message = form.cleaned_data['message']

            msg = Message.objects.create(from_user=from_user, to_user=to_user, 
                                         message=message, 
                                         sharezone=request.user.user.sharezone)

            form = MessageForm(request.user.user)
            context = {'success': True, 'form': form, 'users': users}

            return render(request, 'message/sendmessage.html', context)
        else:
            context = {'form': form, 'users': users}
            return render(request, 'message/sendmessage.html', context)

    form = MessageForm(request.user.user)

    context = {'form': form, 'users': users}

    return render(request, 'message/sendmessage.html', context)

@login_required(login_url='user.views.login')
def inbox(request):
    """
    Generates the view for inbox.html which displays a list of messages received
    by the User ordered by timestamp. When the inbox page is rendered, the
    message is marked as read. 
    """
    messages = Message.objects.order_by('from_user', '-timestamp')

    msg_dict = {}

    for message in messages:
        if message.to_user.as_child() == request.user.user.as_child():
            message.read = True
            message.save()
            from_username = message.from_user.name
            if from_username in msg_dict:
                msg_dict[from_username].append(message)
            else:
                msg_dict[from_username] = [message]

    context = {'msg_dict': msg_dict}

    return render(request, 'message/inbox.html', context)

@login_required(login_url='user.views.login')
def reply(request, message_id):
    """
    Generates the view for reply.html for users to reply to a received message.
    Upon submission of the form on the reply page, the form is validated and
    upon success, the reply message is created as a Message object and stored
    in the database. 
    """
    msg = Message.objects.get(pk=message_id)

    if request.method == 'POST':
        form = MessageForm(request.user.user, request.POST)

        if not form['message'].errors:
            from_user = request.user.user
            to_user = msg.from_user
            message = form.cleaned_data['message']

            new_msg = Message.objects.create(from_user=from_user, to_user=to_user, 
                                             message=message,
                                             sharezone=request.user.user.sharezone)

            form = MessageForm(request.user.user)
            context = {'success': True, 'form': form, 'message': msg}

            return render(request, 'message/reply.html', context)
        else:
            context = {'form': form, 'message': msg}
            return render(request, 'message/reply.html', context)

    form = MessageForm(request.user.user)

    context = {'message': msg, 'form': form}
    return render(request, 'message/reply.html', context)

@login_required(login_url='user.views.login')
def delete(request, message_id):
    """
    Generates the view for delete.html which asks to user to confirm the
    deletion of a message. If confirmed, the message is deleted and the user
    is redirected back to inbox.html without the deleted message. If canceled
    the user is redirected back to inbox.html with no changes.
    """
    msg = Message.objects.get(pk=message_id)

    if 'Confirm' in request.GET:
        msg_copy = Message(from_user=msg.from_user, to_user=msg.to_user, 
                           timestamp=msg.timestamp, message=msg.message,
                           sharezone=request.user.user.sharezone)
        msg.delete()

        context = {'message': msg_copy, 'confirm': False}
        return render(request, 'message/delete.html', context)

    elif 'Cancel' in request.GET:
        return redirect('/message/inbox')

    context = {'message': msg, 'confirm': True}
    return render(request, 'message/delete.html', context)

@login_required(login_url='user.views.login')
def history(request):
    """
    Generates the view for admins to view a history of all messages sent from
    a ToolShare user to another user.
    """
    adminof = request.user.admin_of_sharezones.all()
    admin_level = len(adminof) > 0

    if admin_level:
        my_sharezone = request.user.user.sharezone
        messages = Message.objects.filter(sharezone=my_sharezone). \
                                          order_by('from_user', '-timestamp')
        users = Sharer.objects.filter(sharezone=my_sharezone, _my_subclass='user')
    else:
        messages = Message.objects.all().order_by('from_user', '-timestamp')
        users = Sharer.objects.filter(_my_subclass='user')

    msg_dict = {}

    if request.method == 'POST':
        from_username = request.POST['from']
        to_username = request.POST['to']

        if from_username == 'Any' and to_username == 'Any':
            pass

        elif from_username == 'Any':
            for msg in messages:
                from_username = msg.from_user.name

                from_to = (from_username, to_username)

                if msg.to_user.name == to_username:
                    if from_to in msg_dict:
                        msg_dict[from_to].append(msg)
                    else:
                        msg_dict[from_to] = [msg]

            context = {'msg_dict': msg_dict, 'users': users, 
                       'selected_to': to_username}
            return render(request, 'message/history.html', context)

        elif to_username == 'Any':
            for msg in messages:
                to_username = msg.to_user.name

                from_to = (from_username, to_username)

                if msg.from_user.name == from_username:
                    if from_to in msg_dict:
                        msg_dict[from_to].append(msg)
                    else:
                        msg_dict[from_to] = [msg]

            context = {'msg_dict': msg_dict, 'users': users, 
                       'selected_from': from_username}
            return render(request, 'message/history.html', context)

        else:
            from_to = (from_username, to_username)
            print(from_to)
            from_user = DJUser.objects.get(username=from_username)
            to_user = DJUser.objects.get(username=to_username)

            messages = Message.objects.filter(from_user=from_user, to_user=to_user)

            if len(messages) != 0:
                msg_dict[from_to] = messages

            context = {'msg_dict': msg_dict, 'users': users, 
                       'selected_from': from_username, 'selected_to': to_username}
            return render(request, 'message/history.html', context)

    for msg in messages:
        from_username = msg.from_user.name
        to_username = msg.to_user.name

        from_to = (from_username, to_username)

        if from_to in msg_dict:
            msg_dict[from_to].append(msg)
        else:
            msg_dict[from_to] = [msg]

    context = {'msg_dict': msg_dict, 'users': users}
    return render(request, 'message/history.html', context)