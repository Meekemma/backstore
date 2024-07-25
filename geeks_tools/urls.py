from django.urls import path
from . import views_main
from . import views_admin
from .views_main import CombinedToolListView,CsvToolListView


urlpatterns = [
    
    path('category/', views_main.categorty_list, name='category'), 
    path('subcategories/<int:category_id>/', views_main.category_subcategories, name='subcategories'),
    path('hashtags/<int:subcategory_id>/', views_main.hashtag_list, name='hashtags'),
    path('user-tool/', views_main.user_tool_creation, name='user-tool'),
    path('setup/', views_main.create_setup, name='setup'),
    path('tool-info/', views_main.create_tool_info, name='tool-info'),
    path('tool-info-detail/<int:tool_info_id>/', views_main.tool_info_view, name='tool-info-detail'),
    path('subcription/', views_main.subscription_create_view, name='subcription'),
    path('search-user-tool/', CombinedToolListView.as_view(), name='user-tool-list'),
    path('search-csv-tools/', CsvToolListView.as_view(), name='search-csv-tool'),
    path('create-bookmark/',  views_main.bookmark_list_create, name='create-bookmark'),
    path('update-bookmark/<int:bookmark_id>/',  views_main.bookmark_detail, name='update-bookmark'),
    path('new-tools/', views_main.general_tool_view, name='new-tools'),
    path('new-tool/<int:tool_id>/', views_main.general_tool_view, name='new-tool'),
    path('individual-tools/', views_main.user_tools_view, name='individual-tools'),
    path('individual-tool/<int:pk>/', views_main.user_tool_detail_view, name='individual-tool'),
    path('user-tool/<int:tool_id>/', views_main.get_user_tool, name='get_user_tool'),
    path('premium-tools/', views_main.premium_combined_tools, name='premium_tools'),
    path('popular-searches/', views_main.popular_search_view, name='popular-searches'),
    path('suggestion/', views_main.suggestion_view, name='suggestion'),
    path('draft/', views_main.draft_combined_tools, name='draft'),
    path('best-tool/', views_main.best_tool_view, name='best-tool'), 
    path('draft_update/<int:pk>/', views_main.draft_update, name='draft_update'),
    path('publish_update/<int:pk>/', views_main.publish_update, name='publish_update'),
    path('all-tools/', views_main.all_combined_view, name='all-tools'),
    path('single-csv/<int:pk>/', views_main.user_csvtool_detail, name='single-csv'),
    path('single-combined-tool/<int:pk>/', views_main.user_combinedtool_detail, name='single-combined-tool'),

    path('user-csv/', views_main.user_tool_csv, name='user-csv'), 

    
     





    # ADMIN RELATED URLS
    path('sub-categories/', views_admin.sub_category_view, name='sub-categories'), 
    path('sub-category/<int:pk>/', views_admin.update_subcategory_view, name='sub-category'),
    path('admin-hashtags/', views_admin.hashtag_view, name='admin-hashtags'),
    path('update-admin-hashtag/<int:pk>/', views_admin.update_hashtag_view, name='update-admin-hashtag'),
    path('admin-popular-search/', views_admin.popular_search, name='admin-popular-search'),
    path('admin-update-popular-search/<int:pk>/', views_admin.update_popular_search, name='admin-update-popular-search'),
    path('admin-suggestions/', views_admin.suggestions, name='admin-suggestions'),
    path('admin-update-suggestion/<int:pk>/', views_admin.update_suggestion, name='admin-update-suggestion'),
    path('admin-combine-tool-list/<int:category_id>/', views_admin.combine_tool_list, name='combine-tool-list'),
    path('admin-create-best-tool/', views_admin.best_tool_create, name='admin-create-best-tool'),
    path('upload-csv/', views_admin.combined_tool_view, name='upload-csv'),
    path('upload-csv/<int:Combined_tool_id>/', views_admin.update_combined_tool_view, name='update-upload-csv'),


    path('admin-csv-tools/', views_admin.csvtool_list, name='admin-csv-tool-list'),
    path('admin-csv-tools-detail/<int:pk>/', views_admin.admin_csvtool_detail, name='admin-csv-tool-detail'),

]
