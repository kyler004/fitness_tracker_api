from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, WorkoutSession, WorkoutMetric

class UserSerializer(serializers.ModelSerializer): 
    """Basic user serializer"""
    class Meta: 
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer): 
    """User profile with fitness information"""
    user = UserSerializer(read_only=True)
    bmi = serializers.SerializerMethodField()

    class Meta: 
        model = UserProfile
        fields = [
            'id', 'user', 'age', 'weight', 'height', 'fitness_goal', 'bmi', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_bmi(self, obj):
        """Calculate BMI if weight and height are available"""
        if obj.weight and obj.height: 
            height_m = float(obj.height) / 100 #Convert the centimeters to meters
            bmi = float(obj.weight) / (height_m**2)
            return round(bmi, 2)
        return None

class WorkoutMetricSerializer(serializers.ModelSerializer):
    """Serializer for individual workout metrics (time series data)"""
    class Meta:
        model = WorkoutMetric
        fields = [
            'id', 'timestamp', 'heart_rate', 'speed', 'distance',
            'cadence', 'power', 'elevation', 'weight_lifted', 'reps', 'sets'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Ensure at least one metric is provided"""
        metric_fields = [
            'heart_rate', 'speed', 'distance', 'cadence', 
            'power', 'elevation', 'weight_lifted', 'reps', 'sets'
        ]
        if not any(data.get(field) is not None for field in metric_fields):
            raise serializers.ValidationError(
                "At least one metric value must be provided"
            )
        return data