from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Subscription, User
from .serializers import SubscriptionSerializer
from django.utils import timezone
from urllib.parse import parse_qsl
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = str(os.getenv('TG_BOT_TOKEN'))


def check_webapp_signature(token, init_data):
    try:
        parsed_data = dict(parse_qsl(init_data))
    except ValueError:
        return False
    if "hash" not in parsed_data:
        return False

    hash_ = parsed_data.pop('hash')
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items())
    )
    secret_key = hmac.new(
        key=b"WebAppData", msg=token.encode(), digestmod=hashlib.sha256
    )
    calculated_hash = hmac.new(
        key=secret_key.digest(), msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return calculated_hash == hash_


def get_user_and_validate(request):
    init_data = request.data.get("initData")
    user_info = request.data.get("userInfo")
    if not init_data or not user_info:
        return None, Response("Missing Telegram data", status=400)
    if not check_webapp_signature(bot_token, init_data):
        return None, Response("Invalid signature", status=401)
    return user_info, None


class CheckTelegramData(APIView):
    def post(self, request):
        user_info, error = get_user_and_validate(request)
        if error:
            return error

        user_id = user_info.get("id")
        if not user_id:
            return Response({"error": "Telegram user ID is required"}, status=400)

        user, created = User.objects.get_or_create(
            user_id=user_id,
            defaults={
                'first_name': user_info.get('first_name', ''),
                'last_name': user_info.get('last_name', ''),
                'username': user_info.get('username', ''),
                'language_code': user_info.get('language_code', ''),
                'notifications': True
            }
        )
        if not created:
            user.last_activity = timezone.now()
            user.save()
        return Response(True)


class CreateSubscription(APIView):
    def post(self, request):
        user_info, error = get_user_and_validate(request)
        if error:
            return error

        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save(user_id=user_info['id'])
        return Response(SubscriptionSerializer(subscription).data)


class DeleteSubscription(APIView):
    def post(self, request):
        try:
            sub_id = request.data["subscription_id"]
            sub = Subscription.objects.get(id=sub_id)
            sub.delete()
            return Response(sub_id)
        except:
            return Response("Delete error")


class UpdateSubscription(APIView):
    def post(self, request):
        try:
            subscription = Subscription.objects.get(id=request.data['id'])
            serializer = SubscriptionSerializer(subscription, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
        except:
            pass
        return Response("Update error")


class GetSubscriptions(APIView):
    def post(self, request):
        user_info, error = get_user_and_validate(request)
        if error:
            return error

        subscriptions = Subscription.objects.filter(user_id=user_info['id'])
        result = SubscriptionSerializer(subscriptions, many=True).data
        return Response(result)


class DeleteAllSubscriptions(APIView):
    def post(self, request):
        user_info, error = get_user_and_validate(request)
        if error:
            return error

        user_subscriptions = Subscription.objects.filter(user_id=user_info['id'])
        response = [s.id for s in user_subscriptions]
        user_subscriptions.delete()
        return Response(response)


class AddTestSubscriptions(APIView):
    def post(self, request):
        user_info, error = get_user_and_validate(request)
        if error:
            return error

        user_id = user_info['id']
        test_data = [
            {"name": "Мобильный тариф", "icon": "19", "color": "#2690ce", "cost": "399.99", "period": "30", "periodType": "day", "paymentDate": "2025-02-25", "notifications": True, "category": "internet"},
            {"name": "Домашний интернет", "icon": "5", "color": "#4b942c", "cost": "650", "period": "1", "periodType": "month", "paymentDate": "2025-02-22", "notifications": True, "category": "internet"},
            {"name": "Фильмы", "icon": "3", "color": "#971b57", "cost": "500", "period": "3", "periodType": "month", "paymentDate": "2025-02-14", "notifications": True, "category": "media"},
            {"name": "Музыка", "icon": "16", "color": "#aeb116", "cost": "500", "period": "3", "periodType": "month", "paymentDate": "2025-03-14", "notifications": True, "category": "media"},
            {"name": "Спортзал", "icon": "12", "color": "#97120d", "cost": "4500", "period": "3", "periodType": "month", "paymentDate": "2025-04-14", "notifications": True, "category": "health"},
        ]

        created = []
        for item in test_data:
            item["user_id"] = user_id
            subscription = Subscription.objects.create(**item)
            item["id"] = subscription.id
            created.append(item)
        return Response(created)
