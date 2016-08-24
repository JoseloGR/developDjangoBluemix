from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from comments.forms import CommentForm
from comments.models import Comment
from .models import Post
from .forms import PostForm
# Create your views here.

def index(request):
    return render(request, "base.html", {})

def post_list(request):
    today = timezone.now().date()
    queryset_list = Post.objects.active() #filter(draft=False).filter(publish__lte=timezone.now()) #.all()

    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()

    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query)|
            Q(content__icontains=query)|
            Q(user__first_name__icontains=query)|
            Q(user__last_name__icontains=query)
            ).distinct()

    paginator = Paginator(queryset_list, 4) # Show 25 contacts per page
    page_request_var = "tux"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g.  9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    classactive = 'class=active'
    context = {
        "title": "List",
        "post_list": queryset,
        "page_request_var": page_request_var,
        "today": today,
        'activenowposts': classactive,
        'parentplace': 'Posts',
        'place': 'Posts Recientes',
    }
    return render(request, "posts/list.html", context)

def post_create(request):
    #if not request.user.is_staff or not request.user.is_superuser:
    #    raise Http404

    #if not request.user.is_authenticated():
    #    raise Http404

    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        print(form.cleaned_data.get("title"))
        instance.user = request.user
        instance.save()
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect(instance.get_absolute_url())
    else:
        messages.error(request, "Not Successfully Created")
    context = {
        "form": form,
    }
    return render(request, "posts/form.html", context)

def post_detail(request, id=None):
    instance = get_object_or_404(Post, id=id)

    if instance.draft or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404

    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id,
    }
    #comments = Comment.objects.filter_by_instance(instance)
    comment_form = CommentForm(request.POST or None, initial=initial_data)
    if comment_form.is_valid():
        print(comment_form.cleaned_data)
        c_type = comment_form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        obj_id = comment_form.cleaned_data.get("object_id")
        content_data = comment_form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None

        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()

        new_comment, created = Comment.objects.get_or_create(
                                    user =  request.user,
                                    content_type = content_type,
                                    object_id = obj_id,
                                    content = content_data,
                                    parent = parent_obj
                                )
        if created:
            print("Yeah it worked")
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())


    comments = instance.comments

    context = {
        "title": instance.title,
        "instance": instance,
        "comments": comments,
        "comment_form": comment_form,
    }
    return render(request, "posts/detail.html", context)

def post_update(request, id=None):
    #if not request.user.is_staff or not request.user.is_superuser:
    #    raise Http404
    instance = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        #message succes
        messages.success(request, "Item Saved")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "title": instance.title,
        "instance": instance,
        "form": form,
    }
    return render(request, "posts/form.html", context)


def post_delete(request, id=None):
    #if not request.user.is_staff or not request.user.is_superuser:
    #    raise Http404
    instance = get_object_or_404(Post, id=id)
    instance.delete()
    messages.success(request, "Item Deleted")
    return redirect("posts:list")
