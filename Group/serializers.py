from rest_framework import serializers
from .models import SantaGroup, GroupMember, Pick
from Profile.models import UserProfile
from django.contrib.auth.models import User


def _members_left_to_pick_for_request(group_obj, request):
    """Compute remaining eligible picks for `request.user` in `group_obj`.
        Returns int or None when no request/user available.
    """
    if not request or not getattr(request, 'user', None):
        return None
    try:
        requester_profile = request.user.userprofile
    except Exception:
        return None

    active_member_count = GroupMember.objects.filter(
        group_id=group_obj, is_archived=False
    ).count()

    # Count already-picked profiles in this group (ignore NULL picks)
    picked_count = Pick.objects.filter(group_id=group_obj, picked_profile__isnull=False).count()

    remaining = active_member_count - picked_count
    return max(remaining, 0)


class GroupMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for group members with user details.
    """
    user_id = serializers.IntegerField(source='user_profile_id.user.id', read_only=True)
    email = serializers.CharField(source='user_profile_id.user.email', read_only=True)
    first_name = serializers.CharField(source='user_profile_id.user.first_name', read_only=True)
    last_name = serializers.CharField(source='user_profile_id.user.last_name', read_only=True)
    
    class Meta:
        model = GroupMember
        fields = ['user_id', 'first_name', 'last_name', 'email', 'is_wrapped', 'date_created']


class SantaGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for SantaGroup with member details.
    """
    created_by_name = serializers.CharField(source='created_by.user.get_full_name', read_only=True)
    created_by_id = serializers.IntegerField(source='created_by.user.id', read_only=True)
    member_count = serializers.SerializerMethodField()
    members = GroupMemberSerializer(source='groupmember_set', many=True, read_only=True)
    members_left_to_pick = serializers.SerializerMethodField()
    
    class Meta:
        model = SantaGroup
        fields = [
            'group_id', 
            'group_name', 
            'group_code', 
            'is_open',
            'is_archived',
            'gift_exchange_deadline',
            'join_deadline',
            'budget_min',
            'budget_max',
            'budget_currency',
            'description',
            'exchange_location',
            'is_white_elephant',
            'snatcher_user_id',
            'snatch_revealed_at',
            'snatcher_notified',
            'theme',
            'created_by_name',
            'created_by_id',
            'date_created', 
            'date_updated',
            'member_count',
            'members',
            'members_left_to_pick'
        ]
        read_only_fields = ['group_id', 'group_code', 'created_by_name', 'created_by_id', 'date_created', 'date_updated', 'member_count', 'snatcher_user_id', 'snatch_revealed_at', 'snatcher_notified']
    
    def get_member_count(self, obj):
        return GroupMember.objects.filter(group_id=obj, is_archived=False).count()

    def get_members_left_to_pick(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        return _members_left_to_pick_for_request(obj, request)


class SantaGroupListSerializer(serializers.ModelSerializer):
    """Compact serializer used for group list endpoints.

    Fields: group_id, group_name, group_code, is_open, is_white_elephant, member_count
    """
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = SantaGroup
        fields = [
            'group_id',
            'group_name',
            'group_code',
            'is_open',
            'is_white_elephant',
            'member_count',
        ]

    def get_member_count(self, obj):
        return GroupMember.objects.filter(group_id=obj, is_archived=False).count()

    def get_members_left_to_pick(self, obj):
        request = self.context.get('request') if hasattr(self, 'context') else None
        return _members_left_to_pick_for_request(obj, request)


class CreateGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new group.
    """
    class Meta:
        model = SantaGroup
        fields = [
            'group_name',
            'gift_exchange_deadline',
            'join_deadline',
            'budget_min',
            'budget_max',
            'budget_currency',
            'description',
            'exchange_location',
            'is_white_elephant',
            'theme'
        ]
    
    def validate(self, attrs):
        # Validate budget range
        if attrs.get('budget_min') and attrs.get('budget_max'):
            if attrs['budget_min'] > attrs['budget_max']:
                raise serializers.ValidationError({
                    "budget_min": "Minimum budget cannot be greater than maximum budget."
                })
        return attrs


class UpdateGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a group.
    """
    class Meta:
        model = SantaGroup
        fields = [
            'group_name',
            'is_open',
            'gift_exchange_deadline',
            'join_deadline',
            'budget_min',
            'budget_max',
            'budget_currency',
            'description',
            'exchange_location',
            'is_white_elephant',
            'theme'
        ]
    
    def validate_group_name(self, value):
        # Check if another group with this name exists (excluding current group)
        if SantaGroup.objects.filter(group_name=value).exclude(group_id=self.instance.group_id).exists():
            raise serializers.ValidationError("A group with this name already exists.")
        return value
    
    def validate(self, attrs):
        # Validate budget range
        budget_min = attrs.get('budget_min', self.instance.budget_min if self.instance else None)
        budget_max = attrs.get('budget_max', self.instance.budget_max if self.instance else None)
        
        if budget_min and budget_max and budget_min > budget_max:
            raise serializers.ValidationError({
                "budget_min": "Minimum budget cannot be greater than maximum budget."
            })
        return attrs


class JoinGroupSerializer(serializers.Serializer):
    """
    Serializer for joining a group with a group code.
    """
    group_code = serializers.CharField(max_length=6, required=True)
    
    def validate_group_code(self, value):
        # Convert to uppercase for consistency
        value = value.upper()
        
        # Check if group exists
        try:
            group = SantaGroup.objects.get(group_code=value)
        except SantaGroup.DoesNotExist:
            raise serializers.ValidationError("Invalid group code.")
        
        # Check if group is open
        if not group.is_open:
            raise serializers.ValidationError("This group has been closed by the owner.")
        
        return value


class PickResultSerializer(serializers.Serializer):
    """Serializer for returning a pick result to the requester."""
    pick_id = serializers.UUIDField(read_only=True)
    picked_name = serializers.CharField(read_only=True)
    picked_address = serializers.CharField(read_only=True)
    wishlist_id = serializers.CharField(read_only=True, allow_null=True)
