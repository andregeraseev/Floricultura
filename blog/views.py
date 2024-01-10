from blog.models import Post, Post_Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from blog.models import Post
from django.db.models import Count
from django.views.generic import TemplateView
from django.db.models import Q

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import TemplateView
from .models import Post, Post_Category

class BlogView(TemplateView):
    template_name = 'blog.html'

    def get_context_data(self, request, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obter categoria da query string
        categoria = self.request.GET.get('categoria', 'todas')

        # Filtrar posts por categoria
        if categoria != 'todas':
            all_posts = Post.objects.filter(category=categoria)
        else:
            all_posts = Post.objects.all()

        print('ALLLLL',all_posts)

        # Obter o termo de busca da query string
        query = self.request.GET.get('query', '')

        # Filtrar posts por nome ou tags se houver uma busca
        if query:
            all_posts = all_posts.filter(
                Q(title__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        else:
            # Caso contrário, obter todos os posts
            all_posts = all_posts


        # Configurar o Paginator
        paginator = Paginator(all_posts, 10)  # 10 posts por página

        # Obter o número da página da requisição
        page = request.GET.get('page', 1)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context['posts'] = posts
        context['post_categorys'] = Post_Category.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(request=request, **kwargs))

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(request=request, **kwargs))


class BlogDetailView(TemplateView):
    template_name = 'blog-details.html'

    def get_context_data(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        post = Post.objects.get(slug=kwargs['slug'])

        tags = post.tags.all()

        # Encontrar outros posts que compartilham pelo menos uma tag e excluir o post atual
        related_posts = Post.objects.filter(tags__in=tags).exclude(id=post.id)

        # Agrupar pelos posts e contar o número de tags em comum, e então ordenar
        related_posts = related_posts.annotate(same_tags=Count('tags')).order_by('-same_tags')

        context['post'] = post
        context['related_posts'] = related_posts
        context['post_categorys'] = Post_Category.objects.all()
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(request=request, **kwargs))




class PostView(TemplateView):
    template_name = 'post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = Post.objects.get(id=kwargs['id'])
        return context

