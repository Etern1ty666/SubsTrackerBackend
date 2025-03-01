from celery import shared_task
from django.core.mail import send_mail
from datetime import date, timedelta
from subscriptions.models import User, Subscription
import requests

from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
from dotenv import load_dotenv
load_dotenv()
import locale


locale.setlocale(category=locale.LC_ALL, locale="Russian")

def get_next_payment_date(payment_date, period: int, period_type):
    now = datetime.now().date()
    next_payment = payment_date
    if next_payment <= now:
        diff = -(next_payment - now)
        if diff.days != 0:
            if period_type == 'day':
                periods_count = diff.days // period + 1  # +1 gives all time future date, if not date can be today
                next_payment = payment_date + relativedelta(days=periods_count * period)
            elif period_type == 'week':
                periods_count = diff.days // (period * 7) + 1  # +1 gives all time future date, if not date can be today
                next_payment = payment_date + relativedelta(days=periods_count * period * 7)
            elif period_type == 'year':
                years_before_now = -relativedelta(payment_date, now).years
                periods_count = years_before_now // period + 1
                next_payment = payment_date + relativedelta(years=periods_count * period)
            elif period_type == 'month':
                delta = relativedelta(payment_date, now)
                months_before_now = -delta.years * 12 + -delta.months
                periods_count = months_before_now // period + 1
                next_payment = payment_date + relativedelta(months=periods_count * period)
    return next_payment

@shared_task
def notifications_mailer():
    '''tomorrow = date.today() + timedelta(days=1)
    users = User.objects.filter(birthday=tomorrow)

    for user in users:
        send_mail(
            subject="С Днем Рождения!",
            message=f"Дорогой {user.first_name}, поздравляем тебя с Днем Рождения!",
            from_email="noreply@yourdomain.com",
            recipient_list=[user.email],
            fail_silently=True,
        )'''
    subscriptions = Subscription.objects.all()
    for subscription in subscriptions:
        if subscription.notifications != 0:
            if subscription.last_notification != datetime.now().date():
                next_payment = get_next_payment_date(
                    payment_date=subscription.paymentDate,
                    period=int(subscription.period),
                    period_type=subscription.periodType
                )
                if next_payment == datetime.now().date() + timedelta(days=int(subscription.notifications)):
                    message = f"🗓 Платеж {subscription.cost}₽\n" \
                              f"{subscription.name}\n\n" \
                              f"Дата платежа: {next_payment.strftime('%d.%m.%Y')}"
                    keyboard = {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "Открыть в приложении",
                                    "web_app": {"url": "https://substracker.ru/"}
                                }
                            ]
                        ]
                    }
                    requests.post(f'https://api.telegram.org/bot{str(os.getenv("TG_BOT_TOKEN"))}/sendMessage',
                                  json={
                                      "chat_id": subscription.user_id,
                                      "text": message,
                                      "reply_markup": keyboard
                                  })
                    subscription.last_notification = datetime.now().date()
                    subscription.save()
    return 'notifications_mailer task done!'
