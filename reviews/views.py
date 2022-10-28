from django.shortcuts import render, redirect
from .forms import ArticleForm, CommentForm
from django.contrib.auth.decorators import login_required
from .models import Article, Comment
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib import messages
import os
from django.http import JsonResponse
from django.db.models import Count

# Create your views here.
def index(request):
    temp = Article.objects.annotate(Count("comment"))
    return render(request, "reviews/index.html", {"contents": temp})


@login_required
def create(request):
    form = ArticleForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        temp = form.save(commit=False)
        temp.user_id = request.user.id
        temp.save()
        return redirect("reviews:detail", temp.id)
    return render(request, "reviews/create.html", {"form": form})


def detail(request, pk):
    context = {"article": Article.objects.get(pk=pk), "form": CommentForm()}
    return render(request, "reviews/detail.html", context)


@login_required
def comment(request, article_pk):
    form = CommentForm(request.POST)
    if form.is_valid():
        temp = form.save(commit=False)
        temp.article_id = article_pk
        temp.user_id = request.user.id
        temp.save()
        arr = []
        temp = Comment.objects.filter(article_id=article_pk).order_by("created_at")
        for i in temp:
            arr.append((i.content, i.user.username))
        context = {
            "content": arr,
        }
        return JsonResponse(context)


@login_required
def comment_delete(request, article_pk, comment_pk):
    temp = Comment.objects.get(pk=comment_pk)
    if request.user.id == temp.user_id:
        temp.delete()
        return redirect("reviews:detail", article_pk)
    else:
        return HttpResponseForbidden


@login_required
def update(request, pk):
    temp = Article.objects.get(pk=pk)
    if request.user.id == temp.user_id:
        form = ArticleForm(
            request.POST or None, request.FILES or None, instance=Article.objects.get(pk=pk)
        )
        if form.is_valid():
            if (temp.image and request.FILES.get("image")) or request.POST.get("image-clear"):
                os.remove(temp.image.path)
            if (temp.thumbnail and request.FILES.get("thumbnail")) or request.POST.get(
                "thumbnail-clear"
            ):
                os.remove(temp.thumbnail.path)
            form.save()
            return redirect("reviews:detail", pk)
        context = {
            "form": form,
        }
        return render(request, "reviews/create.html", context)
    else:
        return HttpResponseForbidden


@login_required
def delete(request, pk):
    temp = Article.objects.get(pk=pk)
    if request.user.id == temp.user_id:
        if temp.image:
            os.remove(temp.image.path)
        if temp.thumbnail:
            os.remove(temp.thumbnail.path)
        Article.objects.get(pk=pk).delete()
        return redirect("reviews:index")
    else:
        return HttpResponseForbidden


@login_required
def like(request, article_pk):
    article = Article.objects.get(pk=article_pk)
    if article.like_users.filter(pk=request.user.pk).exists():
        article.like_users.remove(request.user)
        is_liked = False
    else:
        article.like_users.add(request.user)
        is_liked = True
    context = {"isLiked": is_liked, "likeCount": article.like_users.count()}
    return JsonResponse(context)
