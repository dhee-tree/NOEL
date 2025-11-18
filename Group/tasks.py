import random
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .models import SantaGroup, GroupMember
from Mail.utils import MailManager


@shared_task
def check_and_select_snatchers():
    """
    Periodic task that runs every hour to check if any White Elephant groups
    need a Snatcher selected (24 hours before gift_exchange_deadline)
    """
    now = timezone.now()
    
    # Find groups that:
    # 1. Are White Elephant groups
    # 2. Haven't selected a Snatcher yet
    # 3. Gift exchange is within 23-25 hours (to catch it within the hourly window)
    groups_needing_snatcher = SantaGroup.objects.filter(
        is_white_elephant=True,
        snatcher_user_id__isnull=True,
        gift_exchange_deadline__isnull=False,
        gift_exchange_deadline__gte=now + timedelta(hours=23),
        gift_exchange_deadline__lte=now + timedelta(hours=25)
    )
    
    for group in groups_needing_snatcher:
        select_snatcher_for_group.delay(str(group.group_id))
    
    return f"Checked {groups_needing_snatcher.count()} groups"


@shared_task
def select_snatcher_for_group(group_id):
    """
    Randomly selects a Snatcher for a White Elephant group and sends notifications
    """
    try:
        group = SantaGroup.objects.get(group_id=group_id)
    except SantaGroup.DoesNotExist:
        return f"Group {group_id} not found"
    
    # Double-check this is a White Elephant group and no Snatcher selected yet
    if not group.is_white_elephant or group.snatcher_user_id:
        return f"Group {group.group_name} doesn't need a Snatcher"
    
    # Get all members
    members = GroupMember.objects.filter(
        group_id=group,
        is_archived=False
    ).select_related('user_profile_id__user')
    
    if members.count() < 2:
        return f"Group {group.group_name} needs at least 2 members"
    
    # Randomly pick one member as The Snatcher
    snatcher_member = random.choice(list(members))
    
    # Update group with Snatcher info
    group.snatcher_user_id = snatcher_member.user_profile_id.user.id
    group.snatch_revealed_at = timezone.now()
    group.snatcher_notified = True
    group.save()
    
    # Send notification to The Snatcher
    send_snatcher_notification(snatcher_member, group)
    
    # Send notification to all other members
    for member in members:
        if member.user_profile_id.user.id != snatcher_member.user_profile_id.user.id:
            send_group_notification(member, group)
    
    return f"Selected {snatcher_member.user_profile_id.user.get_full_name()} as Snatcher for {group.group_name}"


def send_snatcher_notification(snatcher_member, group):
    """
    Send email to the chosen Snatcher
    """
    user = snatcher_member.user_profile_id.user
    subject = f"🎲 YOU ARE THE SNATCHER! - {group.group_name}"
    
    message = f"""
Congratulations {user.first_name}!

You've been randomly chosen as THE SNATCHER for {group.group_name}!

At the gift exchange tomorrow, you have the power to:
✅ Keep your assigned gift
💥 SNATCH someone else's gift!

Keep it secret until the big reveal! 🎁

Gift Exchange Details:
📅 Date: {group.gift_exchange_deadline.strftime('%B %d, %Y at %I:%M %p') if group.gift_exchange_deadline else 'TBD'}
📍 Location: {group.exchange_location or 'TBD'}

Good luck and have fun!
- The NOEL Team
    """
    
    try:
        mail_manager = MailManager(user.email)
        # Assuming MailManager has a generic send method - adjust based on your implementation
        # You may need to add a new method to MailManager for this
        # For now, using a generic approach:
        from django.core.mail import send_mail
        send_mail(
            subject,
            message,
            'noreply@noel.com',  # Adjust to your from email
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send Snatcher notification: {e}")


def send_group_notification(member, group):
    """
    Send email to all other members that a Snatcher has been chosen
    """
    user = member.user_profile_id.user
    subject = f"🕵️ The Snatcher Has Been Chosen - {group.group_name}"
    
    message = f"""
Hi {user.first_name}!

One of your group members has been chosen as The Snatcher for {group.group_name}!
Who could it be? 👀

At tomorrow's gift exchange, one person will have the power to steal a gift!
Bring your best wrapped gift and be ready for some fun surprises! 🎁

Gift Exchange Details:
📅 Date: {group.gift_exchange_deadline.strftime('%B %d, %Y at %I:%M %p') if group.gift_exchange_deadline else 'TBD'}
📍 Location: {group.exchange_location or 'TBD'}

See you there!
- The NOEL Team
    """
    
    try:
        from django.core.mail import send_mail
        send_mail(
            subject,
            message,
            'noreply@noel.com',  # Adjust to your from email
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send group notification: {e}")
