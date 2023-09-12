from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from accounts.forms import Information 
from accounts.models import InformationUser 
import re
from django.core.validators import validate_email
from django.utils.html import escape
from django.urls import reverse
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# Create your views here.


def register(request):
    if request.method == 'POST':
        username = escape(request.POST['username'])
        email = escape(request.POST['email'])
        password = escape(request.POST['password'])
        password2 = escape(request.POST['password2'])
        # If password is correct
        if password == password2:
            # If username with special characters
            if not re.search('^\w+$', username):
                messages.info(request,"Username include special character")
                return redirect('register')
            # If the username exists
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken, please use another one.')
                return redirect('register')
            # If the email is not formatted correctly
            try:
                validate_email(email)
            except:
                messages.info(request,"Email is not formatted correctly")
                return redirect('register')
            # If the email exists
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email taken already, please use another one.')
                return redirect('register')
            # Create new user and redirect
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            return redirect('/')
        messages.info(request, 'Password not matching, please try again.')
        return redirect('register')
    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        username = escape(request.POST['username'])
        password = escape(request.POST['password'])
        user = auth.authenticate(username=username, password=password)
        # If login successfully
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        messages.info(request, 'Invalid credentials, please try again')
        return redirect('login')
    return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return redirect('/')

def information(request):
    if not request.user.is_active:
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
        # get information from forms
        form = Information(request.POST)
        if form.is_valid:
            # get information user
            user = User.objects.get(id=request.user.id)
            if request.FILES and request.FILES['Avatar']:
                # Cập nhập avatar nếu có
                f = request.FILES.get('Avatar')
                filename = user.username+os.path.splitext(f.name)[1]
                try:
                    os.remove(os.path.join(
                        settings.MEDIA_ROOT, 'avatar/'+filename))
                except:
                    pass
                fs = FileSystemStorage()
                filename = fs.save('avatar/'+filename, f)
                # Lưu lại thông tin của đường dẫn ảnh
                user.last_name = fs.url(filename)
            # update information user
            user.email = request.POST['Email']
            user.save()
            # update information user
            infoUser = InformationUser.objects.get(User=request.user)
            infoUser.Facebook = request.POST['Facebook']
            infoUser.Phone = request.POST['Phone']
            infoUser.save()
            messages.add_message(request, messages.INFO,
                                 'Update information success')
    form = Information()
    InformationUser.objects.get_or_create(User=request.user)
    data = InformationUser.objects.get(User=request.user)
    return render(
        request,
        'information.html',
        {
            "form": form,
            "data": data
        }
    )
