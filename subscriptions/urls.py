from django.urls import path
from .views import CheckTelegramData, CreateSubscription, DeleteSubscription, UpdateSubscription, GetSubscriptions, DeleteAllSubscriptions, AddTestSubscriptions

urlpatterns = [
    path('checkTelegramData/', CheckTelegramData.as_view(), name='check_telegram_data'),
    path('createSubscription/', CreateSubscription.as_view(), name='createSubscription'),
    path('deleteSubscription/', DeleteSubscription.as_view(), name='deleteSubscription'),
    path('updateSubscription/', UpdateSubscription.as_view(), name='updateSubscription'),
    path('getSubscriptions/', GetSubscriptions.as_view(), name='getSubscriptions'),
    path('deleteAllSubscriptions/', DeleteAllSubscriptions.as_view(), name='deleteAllSubscriptions'),
    path('addTestSubscriptions/', AddTestSubscriptions.as_view(), name='addTestSubscriptions'),

]