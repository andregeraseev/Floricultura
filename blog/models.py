from django.db import models
from django.utils.text import slugify
from django.urls import reverse



class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField('date published')
    image = models.ImageField(upload_to='blog_images/')
    comments_count = models.IntegerField(default=0)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    category = models.ForeignKey('Post_Category', related_name='post', on_delete=models.CASCADE, blank=True, null=True)
    tags = models.ManyToManyField('Post_Tag', related_name='tag', blank=True,)

    def __str__(self):
        return self.title

    @property
    def tags_list(self):
        tags = [ tag.name for tag in self.tags.all()]
        return ', '.join(tags)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def get_absolute_url(self):
        return reverse('post', kwargs={'slug': self.slug})

    @property
    def short_content(self):
        return self.content[:120]



class Post_Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comment', on_delete=models.CASCADE)
    content = models.TextField()
    pub_date = models.DateTimeField('date published')
    author = models.CharField(max_length=200)

    def __str__(self):
        return self.content

class Post_Category(models.Model):
    name = models.CharField(max_length=200)


    def __str__(self):
        return self.name

    @property
    def count_posts(self):
        count = 0
        for post in self.post.all():
            count += 1
        return count




class Post_Tag(models.Model):
    tags = models.ManyToManyField('Post', related_name='posts', blank=True)
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return str(self.name)