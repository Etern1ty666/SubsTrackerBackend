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
            if user_not_exists(request.query_params['user_info[id]']):
                User.objects.create(
                                    user_id=request.query_params['user_info[id]'],
                                    language_code=request.query_params['user_info[language_code]'],
                                    first_name=request.query_params['user_info[first_name]'],
                                    last_name=request.query_params['user_info[last_name]'],
                                    username=request.query_params['user_info[username]'],
                                    notifications=True
                                    )
            return Response(True)
        else:
            return Response(False)


class CreateSubscription(APIView):
    def post(self, request):
        print(request.data)
        serializer = SubscriptionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            subscription = serializer.save()
            return Response(SubscriptionSerializer(subscription).data)
        else:
            return Response('Create error')

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
            print(serializer.data)
            return Response(serializer.data)
        else:
            return Response('Update error')


class GetSubscriptions(APIView):
    def get(self, request):
        result = []
        subscriptions = Subscription.objects.filter(user_id=request.query_params["user_id"])
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
        },)
        return Response(result)