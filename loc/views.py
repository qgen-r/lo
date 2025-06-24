from django.shortcuts            import render
from django.http                 import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf                 import settings
from .models                     import CustomerLoc
from twilio.rest                 import Client
import requests, json
from ipware import get_client_ip
import requests

twilio_client = Client(settings.TWILIO_ACCOUNT_SID,
                       settings.TWILIO_AUTH_TOKEN)
VERIFY_SID    = settings.TWILIO_VERIFY_SID
# loc/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http           import JsonResponse
from .models               import CustomerLoc
import json

@csrf_exempt
def save_ip(request):
    if request.method == "POST":
        data = json.loads(request.body)
        loc  = CustomerLoc.objects.get(id=data["loc_id"])
        loc.ip_lat  = data.get("ip_lat")
        loc.ip_lon  = data.get("ip_lon")
        loc.ip_city = data.get("ip_city", "")
        loc.save()
        return JsonResponse({"status":"ip saved"})
    return JsonResponse({"error":"invalid method"}, status=400)


def verify_page(request):
    # 1) Create fresh record
    ua  = request.META.get("HTTP_USER_AGENT", "")
    loc = CustomerLoc.objects.create(user_agent=ua)

    # 2) Extract real client IP (not 127.0.0.1 behind proxy)
    client_ip, _ = get_client_ip(request)

    if client_ip:
        try:
            # 3) Call IP geolocation (city-level)
            res = requests.get(f"https://ipapi.co/{client_ip}/json/").json()
            loc.ip_lat  = res.get("latitude")
            loc.ip_lon  = res.get("longitude")
            loc.ip_city = res.get("city", "")
            loc.save()
        except Exception:
            # silent fail—GPS step still follows
            pass

    # 4) Render and pass this record’s PK for GPS+OTP flow
    return render(request, "loc/verify_page.html", {"loc_id": loc.id})


@csrf_exempt
def save_gps(request):
    if request.method == "POST":
        data = json.loads(request.body)
        loc  = CustomerLoc.objects.get(id=data["loc_id"])
        loc.gps_lat, loc.gps_lon = data["latitude"], data["longitude"]
        loc.save()
        return JsonResponse({"status": "gps saved"})
    return JsonResponse({"error": "invalid method"}, status=400)

@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        loc  = CustomerLoc.objects.get(id=data["loc_id"])
        loc.phone = data["phone"]
        loc.save()
        twilio_client.verify.v2.services(VERIFY_SID).verifications.create(
            to=loc.phone, channel="sms"
        )
        return JsonResponse({"status": "otp sent"})
    return JsonResponse({"error": "invalid method"}, status=400)

@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        loc  = CustomerLoc.objects.get(id=data["loc_id"])
        check = twilio_client.verify.v2.services(VERIFY_SID).verification_checks.create(
            to=loc.phone, code=data["code"]
        )
        if check.status == "approved":
            loc.is_verified = True
            loc.save()
        return JsonResponse({"status": check.status})
    return JsonResponse({"error": "invalid method"}, status=400)
