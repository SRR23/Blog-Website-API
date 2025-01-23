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
    
    def save(self, *args, **kwargs):
        # Generate a unique slug for the blog
        # This method is called before saving the object
        # It checks if the object is being updated or created
        # If the object is being updated, it checks if the title has changed
        # If the title has changed, it generates a new slug
        # If the object is new, it generates a new slug
        
        updating = self.pk is not None # Check if the object is being updated

        if updating:
            # Fetch the original object to check if the title has changed
            original = Blog.objects.get(pk=self.pk)
            if original.title != self.title: # Check if the title has changed
                self.slug = generate_unique_slug(self, self.title, update=True) # Generate a new slug
        else:
            # Generate slug only for new objects
            self.slug = generate_unique_slug(self, self.title)
        
        super().save(*args, **kwargs)

    
    @property
    def related(self):
        # Property to get related blogs
        # This property is used in the BlogDetailSerializer
        # It returns all blogs in the same category except the current blog
        # This is used to display related blogs on the blog detail page
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