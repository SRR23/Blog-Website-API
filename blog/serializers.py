from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import (
    Blog,
    Category,
    Tag,
    Favourite,
    Review,
)

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']

# Tag Serializer
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'title', 'slug']

# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source='user.username', read_only=True) # Use the username for the user
    title = serializers.StringRelatedField(read_only=True) # Use the title for the blog

    class Meta:
        model = Review
        fields = ["id", 'user', 'title', 'comment', 'rating', 'created_date']



class BlogSerializer(serializers.ModelSerializer):
    
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_title = serializers.StringRelatedField(source='category', read_only=True)
    
    tags = serializers.CharField(write_only=True)  # Accept comma-separated string for tags
    tag_title = serializers.StringRelatedField(source='tags', many=True, read_only=True)
    
    user = serializers.CharField(source='user.username', read_only=True)
    
    is_favourited = serializers.BooleanField(read_only=True)  # Use the annotated field directly
    
    reviews = ReviewSerializer(many=True, read_only=True, source='blog_reviews')

    class Meta:
        model = Blog
        fields = [
            'id',  # Add ID for easier referencing
            'user',
            'title',
            'slug',
            'category',
            'category_title',
            'banner',
            'description',
            'tags',
            'tag_title',
            'created_date',
            'is_favourited',
            'reviews',
        ]
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')  # Comma-separated string
        blog = Blog.objects.create(**validated_data)
        blog.tags.set(self._get_or_create_tags(tags_data))  # Parse and add tags
        return blog

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)  # Get new tags

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if tags_data:
            # Get current tags before updating
            old_tags = list(instance.tags.all())

            # Update tags (this will replace old tags with new ones)
            instance.tags.set(self._get_or_create_tags(tags_data))

            # Delete orphaned tags (tags that are not linked to any blog)
            for tag in old_tags:
                if not Blog.objects.filter(tags=tag).exists():  # Check if the tag is used in any blog
                    tag.delete()

        instance.save()
        return instance

    def _get_or_create_tags(self, tags):
        """
        Parse comma-separated tags and resolve to Tag objects (create if necessary).
        """
        tag_objects = []
        for tag_name in tags.split(','):  # Split comma-separated tags
            tag_name = tag_name.strip()
            if tag_name:  # Avoid empty strings
                tag_obj, created = Tag.objects.get_or_create(title=tag_name)
                tag_objects.append(tag_obj)
        return tag_objects
    
    # get_is_favourited method to check if the user is authenticated before querying:
    def get_is_favourited(self, obj):
        user = self.context['request'].user # Get the user from the context
        if user.is_authenticated:
            return Favourite.objects.filter(user=user, blog=obj).exists() # Check if the user has favourited the blog
        return False


# Blog Detail Serializer
# Includes related blogs
# Inherits from BlogSerializer
class BlogDetailSerializer(BlogSerializer):
    related_blogs = serializers.SerializerMethodField()
    # is_favourited = serializers.BooleanField(read_only=True)  # Use the annotated field directly

    class Meta(BlogSerializer.Meta):
        fields = BlogSerializer.Meta.fields + ['related_blogs'] # Include related_blogs in the fields

    def get_related_blogs(self, obj):
        related_blogs = obj.related # Use the property to get related blogs
        return RelatedBlogSerializer(related_blogs, many=True).data # Serialize the related blogs

# Related Blog Serializer
class RelatedBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'banner', 'created_date']
