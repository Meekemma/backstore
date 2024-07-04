from rest_framework import serializers
from django.utils import timezone
from django.core.validators import EmailValidator
from payment.models import *

from django.contrib.auth import get_user_model
User = get_user_model()




class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ('user_email', 'stripe_payment_intent_id', 'amount_received', 'currency', 'status', 'product_id', 'product_name', 'created_at', 'updated_at')
        read_only_fields = ('user', 'created_at', 'updated_at')

    def get_user_email(self, obj):
        return obj.user.email
