from rest_framework import serializers
from django.utils import timezone


def validate_workout_times(start_time, end_time):
    """
    Validate that workout times make sense
    """
    if end_time and start_time:
        if end_time <= start_time:
            raise serializers.ValidationError(
                "End time must be after start time"
            )
        
        # Check if workout is too long (more than 24 hours)
        duration = end_time - start_time
        if duration.total_seconds() > 86400:  # 24 hours
            raise serializers.ValidationError(
                "Workout duration cannot exceed 24 hours"
            )
        
        # Check if workout is in the future
        if start_time > timezone.now():
            raise serializers.ValidationError(
                "Workout cannot start in the future"
            )


def validate_metric_timestamp(session, timestamp):
    """
    Validate that metric timestamp falls within workout session
    """
    if session.start_time and timestamp < session.start_time:
        raise serializers.ValidationError(
            "Metric timestamp cannot be before workout start time"
        )
    
    if session.end_time and timestamp > session.end_time:
        raise serializers.ValidationError(
            "Metric timestamp cannot be after workout end time"
        )

