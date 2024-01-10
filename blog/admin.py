from django.contrib import admin
from django.utils.html import format_html

from .models import Post, Post_Comment, Post_Category, Post_Tag

class PostCommentInline(admin.TabularInline):
    model = Post_Comment
    extra = 1

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'pub_date', 'comments_count', 'image_thumbnail')
    list_filter = ('pub_date', 'category')
    search_fields = ('title', 'content')
    inlines = [PostCommentInline]
    prepopulated_fields = {'slug': ('title',)}

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height:auto;">', obj.image.url)
        return '-'
    image_thumbnail.short_description = 'Image'

admin.site.register(Post, PostAdmin)
admin.site.register(Post_Category)
admin.site.register(Post_Tag)

