from django_filters import rest_framework as filters
from .models import CombinedTool, CsvTool

class CombinedToolFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='user_tool__name', lookup_expr='icontains')
    intro = filters.CharFilter(field_name='user_tool__intro', lookup_expr='icontains')
    hashtag = filters.CharFilter(method='filter_by_hashtag')
    category = filters.CharFilter(field_name='user_tool__category__name', lookup_expr='icontains')
    subcategory = filters.CharFilter(field_name='user_tool__subcategory__name', lookup_expr='icontains')

    class Meta:
        model = CombinedTool
        fields = ['name', 'intro', 'hashtag', 'category', 'subcategory']

    def filter_by_hashtag(self, queryset, name, value):
        return queryset.filter(user_tool__hashtag__term__icontains=value)



class CsvToolFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category', lookup_expr='icontains')
    subcategory = filters.CharFilter(field_name='subcategory', lookup_expr='icontains')
    hashtag = filters.CharFilter(method='filter_by_hashtag')
    intro = filters.CharFilter(field_name='intro', lookup_expr='icontains')
    pricing = filters.CharFilter(field_name='pricing', lookup_expr='icontains')
    logo = filters.CharFilter(field_name='logo', lookup_expr='icontains')
    image1 = filters.CharFilter(field_name='image1', lookup_expr='icontains')

    class Meta:
        model = CsvTool
        fields = ['name', 'category', 'subcategory', 'hashtag', 'intro', 'pricing', 'logo', 'image1']

    def filter_by_hashtag(self, queryset, name, value):
        return queryset.filter(hashtag__icontains=value)

