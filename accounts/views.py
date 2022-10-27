from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.


def index(request):
    return render(request, "accounts/index.html", {"infos": get_user_model().objects.all()})


def signup(request):
    form = CustomUserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("accounts:index")
    return render(request, "accounts/signup.html", {"form": form})


def signin(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "accounts:index")
    return render(request, "accounts/login.html", {"form": form})


@login_required
def signout(request):
    logout(request)
    return redirect("accounts:index")


def detail(request, pk):
    return render(
        request, "accounts/detail.html", {"user": get_object_or_404(get_user_model(), pk=pk)}
    )


@login_required
def follow(request, pk):
    person = get_object_or_404(get_user_model(), pk=pk)
    if person != request.user and request.method == "POST":
        if person.followers.filter(pk=request.user.pk).exists():
            person.followers.remove(request.user)
            is_follow = False
        else:
            person.followers.add(request.user)
            is_follow = True
    else:
        messages.warning(request, "그건 안됨.")
    context = {
        "isFollow": is_follow,
        "followersCount": person.followers.count(),
        "followingsCount": person.followings.count(),
    }
    return JsonResponse(context)


@login_required
def update(request):
    form = CustomUserChangeForm(request.POST or None, instance=request.user)
    if form.is_valid():
        return redirect("accounts:detail", request.user.pk)
    return render(request, "accounts/update.html", {"form": form})
