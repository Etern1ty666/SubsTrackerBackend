from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Subscription, User
from .serializers import SubscriptionSerializer
import hmac
import hashlib
from django.http import JsonResponse
import hashlib
import hmac
from operator import itemgetter
from urllib.parse import parse_qsl
from django.utils import timezone
import os
import json
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
        f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
    )
    secret_key = hmac.new(
        key=b"WebAppData", msg=token.encode(), digestmod=hashlib.sha256
    )
    calculated_hash = hmac.new(
        key=secret_key.digest(), msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return calculated_hash == hash_


def user_not_exists(user_id):
    user = User.objects.filter(user_id=user_id).first()
    if user:
        return False
    else:
        return True


def update_last_activity(user_id):
    user = User.objects.filter(user_id=user_id).first()
    user.last_activity = timezone.now()
    user.save()


class CheckTelegramData(APIView):
    def get(self, request):
        if check_webapp_signature(token=bot_token, init_data=request.query_params['init_data']):
            user_data = {
                'user_id': request.query_params.get('user_info[id]'),
                'language_code': request.query_params.get('user_info[language_code]', ''),
                'first_name': request.query_params.get('user_info[first_name]', ''),
                'last_name': request.query_params.get('user_info[last_name]', ''),
                'username': request.query_params.get('user_info[username]', ''),
                'notifications': True
            }

            if not user_data['user_id']:
                return Response({'error': 'Тelegram user ID is required'}, status=400)

            if user_not_exists(request.query_params['user_info[id]']):
                User.objects.create(**user_data)
            return Response(True)
        else:
            return Response(False)


class CreateSubscription(APIView):
    def post(self, request):
        init_data = request.headers.get('Tg-Init-Data')
        user_info = json.loads(request.headers.get('Tg-User-Info'))
        if check_webapp_signature(token=bot_token, init_data=init_data):
            serializer = SubscriptionSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                subscription = serializer.save(user_id=user_info['id'])
                return Response(SubscriptionSerializer(subscription).data)
            else:
                return Response('Create error')
        else:
            return Response('Authorize via telegram', status=401)


class DeleteSubscription(APIView):
    def post(self, request):
        try:
            sub_id = request.data["subscription_id"]
            sub = Subscription.objects.get(id=sub_id)
            sub.delete()
            return Response(sub_id)
        except:
            return Response('Delete error')


class UpdateSubscription(APIView):
    def post(self, request):

        subscription = Subscription.objects.get(id=request.data['id'])

        serializer = SubscriptionSerializer(subscription, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response('Update error')


class GetSubscriptions(APIView):
    def get(self, request):
        init_data = request.headers.get('Tg-Init-Data')
        user_info = json.loads(request.headers.get('Tg-User-Info'))
        if check_webapp_signature(token=bot_token, init_data=init_data):
            result = []
            subscriptions = Subscription.objects.filter(user_id=user_info['id'])
            for sub in subscriptions:
                result.append({
                    'id': sub.id,
                    'name': sub.name,
                    'icon': sub.icon,
                    'color': sub.color,
                    'cost': sub.cost,
                    'period': sub.period,
                    'periodType': sub.periodType,
                    'paymentDate': sub.paymentDate,
                    'notifications': sub.notifications,
                    'category': sub.category
                }, )
            return Response(result)
        else:
            return Response('Authorize via telegram', status=401)


class DeleteAllSubscriptions(APIView):
    def post(self, request):
        init_data = request.headers.get('Tg-Init-Data')
        user_info = json.loads(request.headers.get('Tg-User-Info'))
        if check_webapp_signature(token=bot_token, init_data=init_data):
            user_subscriptions = Subscription.objects.filter(user_id=user_info['id'])
            response = []
            for subscription in user_subscriptions:
                response.append(subscription.id)
                subscription.delete()
            return Response(response)
        else:
            return Response('Authorize via telegram', status=401)


class AddTestSubscriptions(APIView):
    def post(self, request):
        init_data = request.headers.get('Tg-Init-Data')
        user_info = json.loads(request.headers.get('Tg-User-Info'))
        if check_webapp_signature(token=bot_token, init_data=init_data):
            test_subscriptions = [{
                'id': 0,
                "user_id": user_info['id'],
                "name": "Мобильный тариф",
                "icon": "19",
                "color": "#2690ce",
                "cost": "399.99",
                "period": "30",
                "periodType": "day",
                "paymentDate": "2025-02-25",
                "notifications": "1",
                "category": "internet"
            },
            {
                'id': 0,
                "user_id": user_info['id'],
                "name": "Домашний интернет",
                "icon": "5",
                "color": "#4b942c",
                "cost": "650",
                "period": "1",
                "periodType": "month",
                "paymentDate": "2025-02-22",
                "notifications": "1",
                "category": "internet"
            },
            {
                'id': 0,
                "user_id": user_info['id'],
                "name": "Фильмы",
                "icon": "3",
                "color": "#971b57",
                "cost": "500",
                "period": "3",
                "periodType": "month",
                "paymentDate": "2025-02-14",
                "notifications": "1",
                "category": "media"
            },
            {
                'id': 0,
                "user_id": user_info['id'],
                "name": "Музыка",
                "icon": "16",
                "color": "#aeb116",
                "cost": "500",
                "period": "3",
                "periodType": "month",
                "paymentDate": "2025-03-14",
                "notifications": "1",
                "category": "media"
            },
            {
                'id': 0,
                "user_id": user_info['id'],
                "name": "Спортзал",
                "icon": "12",
                "color": "#97120d",
                "cost": "4500",
                "period": "3",
                "periodType": "month",
                "paymentDate": "2025-04-14",
                "notifications": "1",
                "category": "health"
            },
            ]
            for test_subscription in test_subscriptions:
                new_subscription = Subscription.objects.create(
                    user_id=test_subscription['user_id'],
                    name=test_subscription['name'],
                    icon=test_subscription['icon'],
                    color=test_subscription['color'],
                    cost=test_subscription['cost'],
                    period=test_subscription['period'],
                    periodType=test_subscription['periodType'],
                    paymentDate=test_subscription['paymentDate'],
                    notifications=test_subscription['notifications'],
                    category=test_subscription['category']
                )
                test_subscription["id"] = new_subscription.id
            return Response(test_subscriptions)
        else:
            return Response('Authorize via telegram', status=401)

