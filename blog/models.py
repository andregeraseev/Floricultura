from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField('date published')
    image = models.ImageField(upload_to='blog_images/')
    comments_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title
