from celery import task
from datetime import timedelta
from petri.synergy.utils import create_and_send_email_digest
from petri.account.models import UserProfile


@task
def send_daily_email_digest():

    profiles = UserProfile.objects.filter(email_digest=UserProfile.DAILY_DIGEST, status=UserProfile.APPROVED)

    time_ago = timedelta(days=1)
    create_and_send_email_digest(time_ago=time_ago, to_user_profiles=profiles, subject="[Hacker Union] Daily Digest")


@task
def send_weekly_email_digest():
    profiles = UserProfile.objects.filter(email_digest=UserProfile.WEEKLY_DIGEST, status=UserProfile.APPROVED)

    time_ago = timedelta(days=7)
    create_and_send_email_digest(time_ago=time_ago, to_user_profiles=profiles, subject="[Hacker Union] Weekly Digest")


@task
def send_monthly_email_digest():

    profiles = UserProfile.objects.filter(email_digest=UserProfile.MONTHLY_DIGEST, status=UserProfile.APPROVED)

    time_ago = timedelta(days=30)
    create_and_send_email_digest(time_ago=time_ago, to_user_profiles=profiles, subject="[Hacker Union] Monthly Digest")
