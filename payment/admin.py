
# Register your models here.
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user','stripe_payment_intent_id', 'amount_received', 'currency', 'status','product_id','product_name','created_at', 'updated_at')
    search_fields = ('stripe_payment_intent_id', 'status')
    list_filter = ('status', 'currency')
    ordering = ('-created_at',)

# Alternatively, you can use the following approach to register the model
# admin.site.register(Payment, PaymentAdmin)
