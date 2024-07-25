from rest_framework import serializers
from django.utils import timezone
from django.core.validators import EmailValidator
from geeks_tools.models import *

from django.contrib.auth import get_user_model
User = get_user_model()



#List of all Category with all its fields
class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'image')
        read_only_fields = ('id',)




#Nested Category,subcategory,hashtag on user_tool
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


class UserToolSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    subcategory = SubcategorylistSerializer()
    hashtag = HashtagSerializer(many=True)
    

    class Meta:
        model = User_tool
        fields = ('id', 'user', 'name','url','logo','intro', 'pricing', 'category', 'subcategory', 'hashtag', 'created_at')
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
    


#Setup serializer
class SetUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetUp
        fields = ('id', 'user', 'package_name', 'features', 'Pricing', 'timeline')
        read_only_fields =('id', 'user')

    def validate_features(self, value):
        """
        Validate that the number of features does not exceed 10.
        """
        if len(value) > 10:
            raise serializers.ValidationError("Number of features cannot exceed 10.")
        return value



    def create(self, validated_data):

        user = self.context['request'].user
        setup = SetUp.objects.create(user=user, **validated_data)
        return setup
    




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







class GeneralToolSerializer(serializers.Serializer):
    user_tool = UserToolSerializer()
    setup = SetUpSerializer()
    tool_info = ToolInfoSerializer()

    class Meta:
        read_only = True

    def to_representation(self, instance):
        return {
            'user_tool': UserToolSerializer(instance['user_tool']).data,
            'setup': SetUpSerializer(instance['setup']).data,
            'tool_info': ToolInfoSerializer(instance['tool_info']).data
        }



#Subcription Serializer
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'email', 'subscribed_at', 'is_subscribed']
        read_only_fields = ['id', 'subscribed_at']

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        
        email_validator = EmailValidator()
        try:
            email_validator(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Invalid email format")

        subscribed = Subscription.objects.filter(email=value).first()
        if subscribed:
            raise serializers.ValidationError("Email already registered, please use a different email")

        return value 

    def validate_is_subscribed(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError("Subscription status must be a boolean value")
        return value

    def create(self, validated_data):
        return Subscription.objects.create( **validated_data)
    


class CombinedToolSerializer(serializers.ModelSerializer):
    user_tool = UserToolSerializer(required=False, allow_null=True)
    setup = SetUpSerializer(required=False, allow_null=True)
    tool_info = ToolInfoSerializer(required=False, allow_null=True)

    class Meta:
        model = CombinedTool
        fields = ['id', 'user_tool', 'setup', 'tool_info', 'status','created_by']
        read_only_fields = ['id']


    def update(self, instance, validated_data):
        user_tool_data = validated_data.pop('user_tool', None)
        setup_data = validated_data.pop('setup', None)
        tool_info_data = validated_data.pop('tool_info', None)

        instance.status = validated_data.get('status', instance.status)

        if user_tool_data:
            if instance.user_tool:
                user_tool_serializer = UserToolSerializer(instance.user_tool, data=user_tool_data, partial=True, context=self.context)
            else:
                user_tool_serializer = UserToolSerializer(data=user_tool_data, context=self.context)
            if user_tool_serializer.is_valid():
                user_tool = user_tool_serializer.save()
                instance.user_tool = user_tool

        if setup_data:
            if instance.setup:
                setup_serializer = SetUpSerializer(instance.setup, data=setup_data, partial=True, context=self.context)
            else:
                setup_serializer = SetUpSerializer(data=setup_data, context=self.context)
            if setup_serializer.is_valid():
                setup = setup_serializer.save()
                instance.setup = setup

        if tool_info_data:
            if instance.tool_info:
                tool_info_serializer = ToolInfoSerializer(instance.tool_info, data=tool_info_data, partial=True, context=self.context)
            else:
                tool_info_serializer = ToolInfoSerializer(data=tool_info_data, context=self.context)
            if tool_info_serializer.is_valid():
                tool_info = tool_info_serializer.save()
                instance.tool_info = tool_info

        instance.save()
        return instance








class CsvToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = CsvTool
        fields = ('id', 'name', 'url', 'category', 'subcategory', 'hashtag', 'intro', 'pricing', 'logo', 'image1', 'created_by', 'created_at')
        read_only_fields = ['id', 'user', 'created_by', 'created_at']





class BookmarkSerializer(serializers.ModelSerializer):
    combined_tool = CombinedToolSerializer(read_only=True)
    combined_tool_id = serializers.PrimaryKeyRelatedField(
        queryset=CombinedTool.objects.all(), source='combined_tool', write_only=True, required=False
    )
    csv_tool = CsvToolSerializer(read_only=True)
    csv_tool_id = serializers.PrimaryKeyRelatedField(
        queryset=CsvTool.objects.all(), source='csv_tool', write_only=True, required=False
    )

    class Meta:
        model = Bookmark
        fields = ('id', 'user', 'combined_tool', 'combined_tool_id', 'csv_tool', 'csv_tool_id', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

    def validate(self, data):
        user = self.context['request'].user
        combined_tool = data.get('combined_tool')
        csv_tool = data.get('csv_tool')

        if not combined_tool and not csv_tool:
            raise serializers.ValidationError("You must provide either a combined tool or a CSV tool.")

        if combined_tool and Bookmark.objects.filter(user=user, combined_tool=combined_tool).exists():
            raise serializers.ValidationError("You have already bookmarked this combined tool.")

        if csv_tool and Bookmark.objects.filter(user=user, csv_tool=csv_tool).exists():
            raise serializers.ValidationError("You have already bookmarked this CSV tool.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)




class BestToolSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    combined_tool = CombinedToolSerializer(many=True, read_only=True)
    combined_tool_ids = serializers.PrimaryKeyRelatedField(queryset=CombinedTool.objects.all(), many=True, write_only=True)

    class Meta:
        model = BestTool
        fields = ('id', 'name', 'description', 'category', 'image', 'combined_tool', 'combined_tool_ids')
        read_only_fields = ['id', 'combined_tool']

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        combined_tool_ids = validated_data.pop('combined_tool_ids')
        user = self.context['request'].user

        category, created = Category.objects.get_or_create(**category_data)
        best_tool = BestTool.objects.create(user=user, category=category, **validated_data)

        best_tool.combined_tool.set(combined_tool_ids)

        return best_tool

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', None)
        combined_tool_ids = validated_data.pop('combined_tool_ids', None)

        if category_data:
            category, created = Category.objects.get_or_create(**category_data)
            instance.category = category

        if combined_tool_ids is not None:
            instance.combined_tool.set(combined_tool_ids)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance



