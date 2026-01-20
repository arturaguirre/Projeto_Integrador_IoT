from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Usuário ou senha inválidos")

    return render(request, "accounts/login.html")
