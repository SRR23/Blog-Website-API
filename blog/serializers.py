from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import (
    Blog,
    Category,
    Tag,
    Favourite,
    Review,
)

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source='user.username', read_only=True)
    blog = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", 'user', 'blog', 'comment', 'rating', 'created_date']


class BlogSerializer(serializers.ModelSerializer):
    
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_title = serializers.StringRelatedField(source='category', read_only=True)
    
    tags = serializers.CharField(write_only=True)  # Accept comma-separated string for tags
    tag_title = serializers.StringRelatedField(source='tags', many=True, read_only=True)
    
    user = serializers.CharField(source='user.username', read_only=True)
    
    # is_favourited = serializers.SerializerMethodField()
    is_favourited = serializers.BooleanField(read_only=True)  # Use the annotated field directly
    
    reviews = ReviewSerializer(many=True, read_only=True, source='blog_reviews')

    # related = serializers.SerializerMethodField()  # For related blogs

    class Meta:
        model = Blog
        fields = [
            'id',  # Add ID for easier referencing
            'user',
            'title',
            'category',
            'category_title',
            'banner',
            'description',
            'tags',
            'tag_title',
            'is_favourited',
            'reviews',
        ]
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')  # Comma-separated string
        blog = Blog.objects.create(**validated_data)
        blog.tags.set(self._get_or_create_tags(tags_data))  # Parse and add tags
        return blog

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tags_data:
            instance.tags.set(self._get_or_create_tags(tags_data))
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
        user = self.context['request'].user
        if user.is_authenticated:
            return Favourite.objects.filter(user=user, blog=obj).exists()
        return False

    # def get_related(self, obj):
    #     """Return related blogs excluding the current one."""
    #     related_blogs = obj.related
    #     return BlogSerializer(related_blogs, many=True).data


