from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view

import requests

from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
from .tasks import send_booking_confirmation_email, send_payment_confirmation_email


# ------------------------------
# Homepage
# ------------------------------
def home_view(request):
    return HttpResponse("Welcome to the ALX Travel App Homepage!")


# ------------------------------
# Listings & Bookings
# ------------------------------
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def perform_create(self, serializer):
        """
        Override perform_create to trigger email notification after booking creation.
        """
        booking = serializer.save()

        # Trigger Celery async task
        send_booking_confirmation_email.delay(booking.id)
        print(f"[INFO] Booking created (ID={booking.id}) → email task triggered")


# ------------------------------
# Payment Views
# ------------------------------
@api_view(['POST'])
def initiate_payment(request):
    """
    Initiates a payment using Chapa API.
    """
    booking_ref = request.data.get("booking_reference")
    amount = request.data.get("amount")
    email = request.data.get("email")

    if not all([booking_ref, amount, email]):
        return Response({"error": "Missing required fields"}, status=400)

    payload = {
        "amount": amount,
        "currency": "ETB",
        "email": email,
        "tx_ref": booking_ref,
        "callback_url": f"{settings.SITE_URL}/api/verify-payment/"
    }

    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}

    try:
        response = requests.post(
            "https://api.chapa.co/v1/transaction/initialize",
            json=payload,
            headers=headers,
            timeout=10
        )
        data = response.json()
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=500)

    if data.get("status") == "success":
        Payment.objects.create(
            booking_reference=booking_ref,
            amount=amount,
            transaction_id=data["data"]["tx_ref"],
            status="Pending"
        )
        return Response(data)

    return Response(data, status=400)


@api_view(['GET'])
def verify_payment(request, tx_ref):
    """
    Verifies a payment with Chapa API.
    """
    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
    url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=500)

    payment = get_object_or_404(Payment, transaction_id=tx_ref)

    if data.get("status") == "success" and data["data"].get("status") == "success":
        payment.status = "Completed"
        payment.save()
        # Trigger Celery email confirmation task
        send_payment_confirmation_email.delay(payment.id)
        print(f"[INFO] Payment completed → email task triggered (Payment ID={payment.id})")
    else:
        payment.status = "Failed"
        payment.save()

    return Response(data)
