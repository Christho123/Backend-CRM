from rest_framework import serializers


class UserAuditDetailSerializer(serializers.Serializer):
    user = serializers.DictField()
    active = serializers.BooleanField()
    active_sessions = serializers.IntegerField()
    sessions = serializers.ListField()
    events = serializers.ListField()

