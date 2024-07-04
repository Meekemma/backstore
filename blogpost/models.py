from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
import json

User = get_user_model()

# Create your models here.
class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['id','name']
    
    def __str__(self):
        return self.name




STATUS = (
    ('Draft', 'Draft'),
    ('Publish', 'Publish')
)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog_category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE)  # Changed from OneToOneField to ForeignKey
    title = models.CharField(max_length=200, unique=True)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='Draft')
    image = models.ImageField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']
    

    def save(self, *args, **kwargs):
        # Custom logic to set default values
        if not self.status:
            self.status = 'Draft'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PopularPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=(('Popular', 'Popular'), ('Unpopular', 'Unpopular')), default='Unpopular')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.post.title} - {self.status}"