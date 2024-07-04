from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
import json

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], blank=True, null=True)
    
    class Meta:
        ordering = ['id','name']
    
    def __str__(self):
        return self.name
    



class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    



class Hashtag(models.Model):
    term = models.CharField(max_length=100)
    subcategories = models.ForeignKey(Subcategory, on_delete=models.CASCADE)

    class Meta:
        ordering = ['term']

    def __str__(self):
        return self.term

    
    

PRICING_CHOICES = (
    ('Free', 'Free'),
    ('Freemium', 'Freemium'),
    ('Premium', 'Premium'),
)

class User_tool(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], blank=True, null=True)
    url = models.URLField(unique=True)
    intro = models.CharField(max_length=70)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='user_tools')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    hashtag = models.ManyToManyField(Hashtag, related_name='user_tools')
    pricing = models.CharField(max_length=10, choices=PRICING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Tool created by {self.user.first_name}"
    




TIMELINE_CHOICES = (
    ('Monthly', 'Monthly'),
    ('Yearly', 'Yearly'),
    ('Annually', 'Annually'),
)

class SetUp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    package_name = models.CharField(max_length=30)
    features = models.JSONField()
    Pricing= models.CharField(max_length=20)
    timeline = models.CharField(max_length=10, choices=TIMELINE_CHOICES)

    def __str__(self):
        return self.package_name
    





class ToolInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True) 
    description = models.TextField()
    image1 = models.ImageField(upload_to='tool_info/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], blank=True, null=True)
    image2 = models.ImageField(upload_to='tool_info/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], blank=True, null=True)
    image3 = models.ImageField(upload_to='tool_info/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], blank=True, null=True) 
    agent = models.JSONField()
    video = models.URLField(blank=True, null=True)
    features = models.JSONField()
    links = models.JSONField()

    def __str__(self):
        if self.user:
            return f"Tool Information for {self.user.first_name}"
        else:
            return "Tool Information"





class Subscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_subscribed = models.BooleanField(default=True)

    def __str__(self):
        return self.email


class CombinedTool(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('publish', 'Publish'),
    ]
    GROUP_CHOICES = [
        ('user','User'),
        ('premium_user', 'premium_user')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_tool = models.ForeignKey(User_tool, on_delete=models.CASCADE, null=True, blank=True)
    setup = models.ForeignKey(SetUp, on_delete=models.CASCADE, null=True, blank=True)
    tool_info = models.ForeignKey(ToolInfo, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.CharField(max_length=100, choices=GROUP_CHOICES, default='user', editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        # Check if the user who created the tool is a premium user
        if self.user.is_premium:
            self.created_by = 'premium_user'
        super().save(*args, **kwargs)

        
    # def save(self, *args, **kwargs):
    #     # Check if all related fields are completed
    #     if self.user_tool  and self.tool_info:
    #         self.status = 'publish'
    #     elif self.user_tool and self.tool_info and self.setup:
    #         self.status = 'publish'
    #     else:
    #         self.status = 'draft'
    #     super().save(*args, **kwargs)


class CsvTool(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(blank=True, null=True)
    url = models.URLField(unique=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    subcategory = models.CharField(max_length=100)
    hashtag = models.JSONField(blank=True, null=True)
    intro = models.TextField(blank=True, null=True)
    pricing = models.CharField(max_length=100)
    logo = models.TextField(blank=True, null=True)  # Consider ImageField if storing images
    image1 = models.TextField(blank=True, null=True)  # Consider ImageField if storing images
    created_by = models.CharField(max_length=100, default='csv', editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Tool created by {self.user.first_name}"



class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    combined_tool = models.ForeignKey('CombinedTool', on_delete=models.CASCADE, related_name='bookmarked_by', null=True, blank=True)
    csv_tool = models.ForeignKey('CsvTool', on_delete=models.CASCADE, related_name='bookmarked_by', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = (('user', 'combined_tool'), ('user', 'csv_tool'))

    




class PopularSearch(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], blank=True, null=True)
    
    class Meta:
        ordering = ['id','name']
    
    def __str__(self):
        return self.name

        

class Suggestion(models.Model):
    text = models.JSONField()

    class Meta:
        ordering = ['id', 'text']
    
    def __str__(self):
        return json.dumps(self.text)


class BestTool(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='category_images/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])], blank=True, null=True)
    combined_tool =models.ManyToManyField(CombinedTool)


    def __str__(self):
        return self.name
























