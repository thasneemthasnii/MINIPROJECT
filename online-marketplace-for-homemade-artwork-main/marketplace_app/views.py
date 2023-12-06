from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, redirect
from marketplace_app.forms import LoginRegister, UserRegister
from marketplace_app.models import Item


def home(request):
    product = Item.objects.all()[:6]
    # latest = Item.objects.order_by('-added_on')[:8]
    context = {
        'products': product,
        # 'latest': latest,
    }
    return render(request, 'home.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pass')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            if user.is_staff:
                return redirect('admin_home')

            elif user.is_user:
                return redirect('user_home')

        else:
            messages.info(request, 'Invalid Credentials')
    return render(request, 'login.html')


def user_register(request):
    login_form = LoginRegister()
    user_form = UserRegister()
    if request.method == 'POST':
        login_form = LoginRegister(request.POST)
        user_form = UserRegister(request.POST)
        if login_form.is_valid() and user_form.is_valid():
            user = login_form.save(commit=False)
            user.is_user = True
            user.save()
            c = user_form.save(commit=False)
            c.user = user
            c.save()
            messages.info(request, 'User Registered Successfully')
            return redirect('login_view')
    return render(request, 'user_register.html', {'login_form': login_form, 'user_form': user_form})


def logout_view(request):
    logout(request)
    return redirect('/')
