from rest_framework import serializers
from .models import SantaGroup, GroupMember, Pick
from Profile.models import UserProfile
from django.contrib.auth.models import User


class GroupMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for group members with user details.
    """
    user_id = serializers.IntegerField(source='user_profile_id.user.id', read_only=True)
    username = serializers.CharField(source='user_profile_id.user.username', read_only=True)
    email = serializers.CharField(source='user_profile_id.user.email', read_only=True)
    first_name = serializers.CharField(source='user_profile_id.user.first_name', read_only=True)
    last_name = serializers.CharField(source='user_profile_id.user.last_name', read_only=True)
    
    class Meta:
        model = GroupMember
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'is_wrapped', 'date_created']


class SantaGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for SantaGroup with member details.
    """
    created_by_name = serializers.CharField(source='created_by.user.get_full_name', read_only=True)
    created_by_id = serializers.IntegerField(source='created_by.user.id', read_only=True)
    member_count = serializers.SerializerMethodField()
    members = GroupMemberSerializer(source='groupmember_set', many=True, read_only=True)
    
    class Meta:
        model = SantaGroup
        fields = [
            'group_id', 
            'group_name', 
            'group_code', 
            'is_open', 
            'created_by_name',
            'created_by_id',
            'date_created', 
            'date_updated',
            'member_count',
            'members'
        ]
        read_only_fields = ['group_id', 'group_code', 'created_by_name', 'created_by_id', 'date_created', 'date_updated', 'member_count']
    
    def get_member_count(self, obj):
        return GroupMember.objects.filter(group_id=obj, is_archived=False).count()


class CreateGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new group.
    """
    class Meta:
        model = SantaGroup
        fields = ['group_name']
    
    def validate_group_name(self, value):
        if SantaGroup.objects.filter(group_name=value).exists():
            raise serializers.ValidationError("A group with this name already exists.")
        return value
    
    def create(self, validated_data):
        # The user_profile will be set in the view
        return SantaGroup.objects.create(**validated_data)


class UpdateGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a group.
    """
    class Meta:
        model = SantaGroup
        fields = ['group_name', 'is_open']
    
    def validate_group_name(self, value):
        # Check if another group with this name exists (excluding current group)
        if SantaGroup.objects.filter(group_name=value).exclude(group_id=self.instance.group_id).exists():
            raise serializers.ValidationError("A group with this name already exists.")
        return value


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
