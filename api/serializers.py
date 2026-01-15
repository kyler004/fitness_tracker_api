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

class WorkoutSessionSerializer(serializers.ModelSerializer): 
    """Light weight serializer for listing sessions"""
    user = serializers.StringRelatedField(read_obly=True)
    workout_type_display = serializers.CharField(
        source = 'get_workout_type_display', 
        read_only=True
    )

    class Meta: 
        model = WorkoutSession
        fields = [
            'id', 'user', 'workout_type', 'workout_type_display', 
            'title', 'start_time', 'duration_minutes', 
            'total_distance', 'total_calories', 'avg_heart_rate'
        ]
        read_only_fields = ['id', 'user']

class WorkoutSessionDetailserializer(serializers.ModelSerializer): 
    """Detailed serializer with nested metrics for time series data"""
    user = serializers.StringRelatedField(read_only=True)
    workout_type_display = serializers.CharField(
        source='get_workout_type_display', 
        read_only=True
    )
    metrics = WorkoutMetricSerializer(many=True, read_only=True)
    metrics_count = serializers.SerializerMethodField()

    class Meta: 
        model: WorkoutSession
        fields = [
           'id', 'user', 'workout_type', 'workout_type_display',
            'title', 'description', 'start_time', 'end_time',
            'duration_minutes', 'total_distance', 'total_calories',
            'avg_heart_rate', 'max_heart_rate', 'notes',
            'metrics', 'metrics_count', 'created_at', 'updated_at' 
        ]
        read_only_fields = ['id', 'user', 'duration_minutes', 'created_at', 'updated_at']
    
    def get_metrics_count(self, obj): 
        """Count of time series data points"""
        return obj.metrics.count()

class WorkoutSessionCreateSerializer(serializers.ModelSerializer): 
    """Serializer for creating workout session with optional metrics"""
    metrics = WorkoutMetricSerializer(many=True, required=False)

    class Meta: 
        model = WorkoutSession
        fields = [
            'workout_type', 'title', 'description', 'start_time',
            'end_time', 'total_distance', 'total_calories',
            'avg_heart_rate', 'max_heart_rate', 'notes', 'metrics' 
        ]

    def create(self, validated_data):
        """Handle creation of session with nested metrics"""
        metrics_data = validated_data.pop('metrics', [])

        # Create the workout session
        session = WorkoutSession.objects.create(**validated_data)

        # Create associated metrics
        for metric_data in metrics_data: 
            WorkoutMetric.objects.create(session=session, **metric_data)
        
        return session
    
    def update(self, instance, validated_data): 
        """Handle updating session (metrics updated separately)"""
        metrics_data = validated_data.pop('metrics', None)

        #Update sesoisn fails
        for attr, value in validated_data.items(): 
            setattr(instance, attr, value)
        instance.save()

        # If metrics provided, replace existing ones 
        if metrics_data is not None: 
            instance.metrics.all().delete()
            for metric_data in metrics_data: 
                WorkoutMetric.objects.create(session=instance, **metric_data)
            return instance
        