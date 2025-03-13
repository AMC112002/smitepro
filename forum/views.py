# forum/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

def post_list(request):
    # Obtenemos todos los posts ordenados por fecha
    posts_list = Post.objects.all().order_by('-created_at')
    
    # Añadimos paginación
    paginator = Paginator(posts_list, 9)  # Mostramos 9 posts por página
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Si el parámetro page no es un entero, mostramos la primera página
        posts = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostramos la última página de resultados
        posts = paginator.page(paginator.num_pages)
        
    return render(request, 'forum/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by('-created_at')
    
    # Incrementamos el contador de vistas (si se implementa)
    # post.views = post.views + 1
    # post.save()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('forum:post_detail', pk=post.pk)
    else:
        form = CommentForm()
        
    # Obtenemos posts relacionados
    related_posts = Post.objects.filter(category=post.category).exclude(pk=post.pk)[:3]
        
    context = {
        'post': post, 
        'comments': comments, 
        'form': form,
        'related_posts': related_posts
    }
    
    return render(request, 'forum/post_detail.html', context)

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            # Si hay tags, los procesamos (asumiendo que tienes un campo para tags)
            if 'tags' in form.cleaned_data:
                post.tags.set(form.cleaned_data['tags'])
                
            return redirect('forum:post_detail', pk=post.pk)
    else:
        form = PostForm()
        
    categories = Category.objects.all()
    return render(request, 'forum/post_form.html', {'form': form, 'categories': categories})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Verificamos que el usuario sea el autor
    if request.user != post.author:
        return redirect('forum:post_detail', pk=post.pk)
        
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            return redirect('forum:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
        
    return render(request, 'forum/post_form.html', {'form': form, 'edit_mode': True})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Verificamos que el usuario sea el autor
    if request.user != post.author:
        return redirect('forum:post_detail', pk=post.pk)
        
    if request.method == 'POST':
        post.delete()
        return redirect('forum:post_list')
        
    return render(request, 'forum/post_confirm_delete.html', {'post': post})

@login_required
def comment_edit(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    
    # Verificar que el usuario sea el autor del comentario
    if request.user != comment.author and not request.user.is_staff:
        return redirect('forum:post_detail', pk=post.pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('forum:post_detail', pk=post.pk)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'forum/comment_form.html', {
        'form': form,
        'post': post,
        'comment': comment
    })

@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    
    # Verificar que el usuario sea el autor del comentario
    if request.user != comment.author and not request.user.is_staff:
        return redirect('forum:post_detail', pk=post.pk)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('forum:post_detail', pk=post.pk)
    
    return render(request, 'forum/comment_confirm_delete.html', {
        'comment': comment,
        'post': post
    })