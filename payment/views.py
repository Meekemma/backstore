import stripe
import json
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from django.contrib.auth import get_user_model
User = get_user_model()




@csrf_exempt
@api_view(['POST'])
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.data
    event = None

    try:
        event = stripe.Event.construct_from(
        payload, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'charge.succeeded':
        charge = event['data']['object']
        process_charge(charge)
    elif event['type'] == 'charge.updated':
        charge = event['data']['object']
        process_charge(charge)
    elif event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        process_session(session)
        print('session',session)
    elif event['type'] == 'payment_intent.created':
        payment_intent = event['data']['object']
        process_payment_intent(payment_intent)
    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        process_payment_intent(payment_intent)
    else:
        print(f'Unhandled event type {event["type"]}')

    return HttpResponse(status=200)


def process_charge(charge):
    stripe_payment_intent_id = charge['payment_intent']
    amount_received = charge['amount'] / 100  # Convert cents to dollars
    currency = charge['currency']
    status = charge['status']
    email = charge['billing_details']['email']
    
    user = User.objects.get(email=email)

    # Update or create the Payment record
    payment, created = Payment.objects.update_or_create(
        stripe_payment_intent_id=stripe_payment_intent_id,
        defaults={
            'user': user,
            'amount_received': amount_received,
            'currency': currency,
            'status': status,
        }
    )
    return payment

def process_session(session):
    stripe_payment_intent_id = session['payment_intent']
    amount_received = session['amount_total'] / 100  # Convert cents to dollars
    currency = session['currency']
    status = session['payment_status']
    email = session['customer_email']

    product_id = session['metadata'].get('toolId', '')
    product_name = session['metadata'].get('type', '')

    print(f'product_id: {product_id}')
    print(f'product_name: {product_name}')

    user = User.objects.get(email=email)

    payment, created = Payment.objects.update_or_create(
        stripe_payment_intent_id=stripe_payment_intent_id,
        defaults={
            'user': user,
            'amount_received': amount_received,
            'currency': currency,
            'status': status,
            'product_id': product_id,
            'product_name': product_name,
        }
    )
    return payment

def process_payment_intent(payment_intent):
    # Process payment intent data if needed
    pass



@api_view(['GET'])
def payment_email_view(request):
    payment_email = Payment.objects.filter(product_name='newsletter')
    serializer = PaymentSerializer(payment_email, many=True)
    return Response(serializer.data)
