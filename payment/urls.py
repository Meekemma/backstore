from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('newsletter-transactions/', views.payment_email_view, name='newsletter-transactions'),

]
