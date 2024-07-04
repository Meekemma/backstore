from rest_framework import serializers
from django.utils import timezone
from django.core.validators import EmailValidator
from geeks_tools.models import *

from django.contrib.auth import get_user_model
User = get_user_model()


from rest_framework import serializers


#Category Serializer Creation
class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)

    def create(self, validated_data):
        return Category.objects.create(**validated_data)



#Category Serializer for nested data
class AdminCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)



#Subcategory creation update using nested category
class  AdminSubcategorySerializer(serializers.ModelSerializer):
    category = AdminCategoryListSerializer()

    class Meta:
        model = Subcategory
        fields = ('id', 'name', 'category')
        read_only_fields = ('id',)

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        category_name = category_data.get('name')
        category, created = Category.objects.get_or_create(name=category_name)
        sub_category = Subcategory.objects.create(category=category, **validated_data)
        return sub_category

    
    def update(self, instance, validated_data):
        category_data = validated_data.pop('category')
        category_name = category_data.get('name')
        category, created = Category.objects.get_or_create(name=category_name)

        instance.category = category

        instance.name = instance.name = validated_data.get('name', instance.name)

        instance.save()
        return instance
    



#Subcategory for nested data
class AdminSubcategorylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ('id', 'name') 
        read_only_fields = ('id',)



#Creation of hashtag using nested subcategory
class AdminHashtagSerializer(serializers.ModelSerializer):
    subcategories = AdminSubcategorylistSerializer()

    class Meta:
        model = Hashtag
        fields = ('id', 'term', 'subcategories')
        read_only_fields = ('id',)

    def validate(self, attrs):
        term = attrs.get('term')
        if term is not None and not term.startswith('#'):
            raise serializers.ValidationError("Hashtag term must start with '#'")
        return attrs
    
    def create(self, validated_data):
        subcategories_data = validated_data.pop('subcategories')
        subcategory_name = subcategories_data.get('name')

        subcategory, created = Subcategory.objects.get_or_create(name=subcategory_name)
        hashtag = Hashtag.objects.create(subcategories=subcategory, **validated_data)
        
        return hashtag


    def update(self, instance, validated_data):
        subcategories_data = validated_data.pop('subcategories')
        subcategory_name = subcategories_data.get('name')

        subcategory, created = Subcategory.objects.get_or_create(name=subcategory_name)
        instance.subcategories = subcategory

        instance.term = validated_data.get('term', instance.term)

        instance.save()
        return instance



#Creation of popularsearch serializer
class AdminPopularSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopularSearch
        fields = ('id', 'name','image')
        read_only_fields = ('id',)

    def create(self, validated_data):
        return PopularSearch.objects.create(**validated_data)
    




#Creation of Suggestion serializer
class AdminSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = ('id', 'text')
        read_only_fields = ('id',)

    def create(self, validated_data):
        return Suggestion.objects.create(**validated_data)



#From this point the nested data is used to for the creation of the usertool
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)

class SubcategorylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ('id', 'name')
        read_only_fields = ('id',)

class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ('id', 'term')
        read_only_fields = ('id',)


#creations of the user tool using the nested data
class UserToolSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    subcategory = SubcategorylistSerializer()
    hashtag = HashtagSerializer(many=True)

    class Meta:
        model = User_tool
        fields = ('id', 'user', 'name', 'url', 'logo', 'intro', 'pricing', 'category', 'subcategory', 'hashtag', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

    def validate(self, data):
        category_name = data['category']['name']
        subcategory_name = data['subcategory']['name']
        hashtags = data.get('hashtag', [])
        url = data.get('url')

        if User_tool.objects.filter(url=url).exists():
            raise serializers.ValidationError(f"The URL '{url}' is already in use by another tool.")

        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            raise serializers.ValidationError(f"Category '{category_name}' does not exist.")

        try:
            subcategory = Subcategory.objects.get(name=subcategory_name, category=category)
        except Subcategory.DoesNotExist:
            raise serializers.ValidationError(f"Subcategory '{subcategory_name}' does not exist in category '{category_name}'.")

        for hashtag_data in hashtags:
            hashtag_term = hashtag_data.get('term')
            if not Hashtag.objects.filter(term=hashtag_term, subcategories=subcategory).exists():
                raise serializers.ValidationError(f"Hashtag '{hashtag_term}' does not exist for subcategory '{subcategory_name}'.")

        return data

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        subcategory_data = validated_data.pop('subcategory')
        hashtags_data = validated_data.pop('hashtag')

        category = Category.objects.get(name=category_data['name'])
        subcategory = Subcategory.objects.get(name=subcategory_data['name'], category=category)

        user_tool = User_tool.objects.create(
            category=category,
            subcategory=subcategory,
            **validated_data
        )

        for hashtag_data in hashtags_data:
            hashtag = Hashtag.objects.get(term=hashtag_data['term'])
            user_tool.hashtag.add(hashtag)

        return user_tool




#Creation of the setup serializer
class SetUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetUp
        fields = ('id', 'user', 'package_name', 'features', 'Pricing', 'timeline')
        read_only_fields = ('id', 'user')

    def validate_features(self, value):
        if len(value) > 10:
            raise serializers.ValidationError("Number of features cannot exceed 10.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        setup = SetUp.objects.create(user=user, **validated_data)
        return setup




#Creation of the Tool Info
class ToolInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolInfo
        fields = ('id', 'user', 'description', 'image1', 'image2', 'image3', 'video', 'links', 'agent', 'features')
        read_only_fields = ['id', 'user']

    def validate_features(self, value):
        if len(value) > 10:
            raise serializers.ValidationError("Number of features cannot exceed 10.")
        return value

    def validate_links(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("Number of links cannot exceed 3.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        tool_info = ToolInfo.objects.create(user=user, **validated_data)
        return tool_info





#This serializer is the combination of the the above serializer 
class AdminCombinedToolSerializer(serializers.ModelSerializer):
    user_tool = UserToolSerializer(required=False, allow_null=True)
    setup = SetUpSerializer(required=False, allow_null=True)
    tool_info = ToolInfoSerializer(required=False, allow_null=True)

    class Meta:
        model = CombinedTool
        fields = ['id', 'user_tool', 'setup', 'tool_info', 'status']
        read_only_fields = ['id']

    def create(self, validated_data):
        user_tool_data = validated_data.pop('user_tool', None)
        setup_data = validated_data.pop('setup', None)
        tool_info_data = validated_data.pop('tool_info', None)

        combined_tool = CombinedTool.objects.create(**validated_data)

        if user_tool_data:
            user_tool = UserToolSerializer(data=user_tool_data)
            user_tool.is_valid(raise_exception=True)
            user_tool_instance = user_tool.save()
            combined_tool.user_tool = user_tool_instance

        if setup_data:
            setup = SetUpSerializer(data=setup_data)
            setup.is_valid(raise_exception=True)
            setup_instance = setup.save()
            combined_tool.setup = setup_instance

        if tool_info_data:
            tool_info = ToolInfoSerializer(data=tool_info_data)
            tool_info.is_valid(raise_exception=True)
            tool_info_instance = tool_info.save()
            combined_tool.tool_info = tool_info_instance

        # Check for the status conditions
        if combined_tool.user_tool and combined_tool.tool_info:
            combined_tool.status = 'publish'
        elif combined_tool.user_tool and combined_tool.setup and combined_tool.tool_info:
            combined_tool.status = 'publish'
        else:
            combined_tool.status = 'draft'

        combined_tool.save()
        return combined_tool

    def update(self, instance, validated_data):
        user_tool_data = validated_data.pop('user_tool', None)
        setup_data = validated_data.pop('setup', None)
        tool_info_data = validated_data.pop('tool_info', None)

        if user_tool_data:
            user_tool = UserToolSerializer(instance.user_tool, data=user_tool_data)
            user_tool.is_valid(raise_exception=True)
            user_tool_instance = user_tool.save()
            instance.user_tool = user_tool_instance

        if setup_data:
            setup = SetUpSerializer(instance.setup, data=setup_data)
            setup.is_valid(raise_exception=True)
            setup_instance = setup.save()
            instance.setup = setup_instance

        if tool_info_data:
            tool_info = ToolInfoSerializer(instance.tool_info, data=tool_info_data)
            tool_info.is_valid(raise_exception=True)
            tool_info_instance = tool_info.save()
            instance.tool_info = tool_info_instance

        # Check for the status conditions
        if instance.user_tool and instance.tool_info:
            instance.status = 'publish'
        elif instance.user_tool and instance.setup and instance.tool_info:
            instance.status = 'publish'
        else:
            instance.status = 'draft'

        instance.save()
        return instance




class CsvToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = CsvTool
        fields = ('id', 'name', 'url', 'category', 'subcategory', 'hashtag', 'intro', 'pricing', 'logo', 'image1', 'created_by', 'created_at')
        read_only_fields = ['id', 'user', 'created_by', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        csv = CsvTool.objects.create(user=user, **validated_data)
        return csv
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.subcategory = validated_data.get('subcategory', instance.subcategory)
        instance.intro = validated_data.get('intro', instance.intro)
        instance.pricing = validated_data.get('pricing', instance.pricing)
        instance.logo = validated_data.get('logo', instance.logo)
        instance.image1 = validated_data.get('image1', instance.image1)
        
        # Handle JSONField 'hashtag'
        hashtag = validated_data.get('hashtag')
        if hashtag is not None:
            instance.hashtag = hashtag

        instance.save()
        return instance


        