from rest_framework import serializers
from .models import Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            'id',
            'user_id',
            'name',
            'icon',
            'color',
            'cost',
            'period',
            'periodType',
            'paymentDate',
            'notifications',
            'category'
        ]