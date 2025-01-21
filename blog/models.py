from django.db import models
from users.models import User
from django.utils.text import slugify
from .slug import generate_unique_slug
# Create your models here.

class Category(models.Model):
    title=models.CharField(max_length=150, unique=True)
    slug=models.SlugField(null=True, blank=True)
    created_date=models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.title
    
    def save(self,*args,**kwargs):
        self.slug=slugify(self.title)
        super().save(*args,**kwargs)
        

class Tag(models.Model):
    title=models.CharField(max_length=150)
    slug=models.SlugField(null=True,blank=True)
    created_date=models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.title
    
    def save(self,*args,**kwargs):
        self.slug=slugify(self.title)
        super().save(*args,**kwargs)


class Blog(models.Model):
    user=models.ForeignKey(User,related_name='user_blogs',on_delete=models.CASCADE)
    category=models.ForeignKey(Category,related_name='category_blogs',on_delete=models.CASCADE)
    tags=models.ManyToManyField(Tag,related_name='tag_blogs',blank=True)
    title=models.CharField(max_length=250)
    slug=models.SlugField(null=True, blank=True)
    banner=models.ImageField(blank=True, upload_to='blog_banners/')
    description=models.TextField()
    created_date=models.DateField(auto_now_add=True)
    
    
    def __str__(self) -> str:
        return self.title
    
    def save(self,*args,**kwargs):
        updating = self.pk is not None
        
        if updating:
            self.slug = generate_unique_slug(self, self.title, update=True)
            super().save(*args, **kwargs)
        else:
            self.slug=generate_unique_slug(self,self.title)
            super().save(*args,**kwargs)
    
    
    @property
    def related(self):
        return self.category.category_blogs.all().exclude(pk=self.pk)


class Favourite(models.Model):
    user = models.ForeignKey(User, related_name='favourites', on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, related_name='favourited_by', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog')

    def __str__(self):
        return f"{self.user.username} favorited {self.blog.title}"


class Review(models.Model):
    user = models.ForeignKey(User,related_name='user_review',on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog,related_name='blog_reviews',on_delete=models.CASCADE)
    comment = models.TextField(max_length=500)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)],null=True)
    created_date = models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.comment