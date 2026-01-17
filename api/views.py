from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Max, Min, Q
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict

from .models import UserProfile, WorkoutSession, WorkoutMetric
from .serializers import (
    UserProfileSerializer, WorkoutSessionListSerializer,
    WorkoutSessionDetailSerializer, WorkoutSessionCreateSerializer,
    WorkoutMetricSerializer, WorkoutStatsSerializer,
    WorkoutProgressSerializer, WorkoutChartDataSerializer,
    HeartRateZoneSerializer
)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user fitness profiles"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users can only access their own profile"""
        return UserProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Associate profile with current user"""
        serializer.save(user=self.request.user)


class WorkoutSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for workout sessions with aggregation endpoints"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users can only access their own workouts"""
        queryset = WorkoutSession.objects.filter(user=self.request.user)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)
        
        # Filter by workout type
        workout_type = self.request.query_params.get('workout_type')
        if workout_type:
            queryset = queryset.filter(workout_type=workout_type)
        
        return queryset.select_related('user').prefetch_related('metrics')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return WorkoutSessionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return WorkoutSessionCreateSerializer
        return WorkoutSessionDetailSerializer
    
    def perform_create(self, serializer):
        """Associate workout with current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get aggregated statistics for a time period
        Query params: period (day/week/month), start_date, end_date
        """
        period = request.query_params.get('period', 'week')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = timezone.now()
        else:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        # Get workouts in date range
        workouts = WorkoutSession.objects.filter(
            user=request.user,
            start_time__gte=start_date,
            start_time__lte=end_date
        )
        
        # Choose truncation function based on period
        if period == 'day':
            trunc_func = TruncDate
        elif period == 'week':
            trunc_func = TruncWeek
        else:
            trunc_func = TruncMonth
        
        # Aggregate by period
        stats = workouts.annotate(
            period_date=trunc_func('start_time')
        ).values('period_date').annotate(
            total_workouts=Count('id'),
            total_duration=Sum('duration_minutes'),
            total_distance=Sum('total_distance'),
            total_calories=Sum('total_calories'),
            avg_heart_rate=Avg('avg_heart_rate')
        ).order_by('period_date')
        
        # Add workout type breakdown for each period
        results = []
        for stat in stats:
            period_workouts = workouts.filter(
                start_time__date=stat['period_date'] if period == 'day'
                else None
            )
            
            # Count by workout type
            type_counts = workouts.filter(
                start_time__gte=stat['period_date']
            ).values('workout_type').annotate(
                count=Count('id')
            )
            
            workout_types = {item['workout_type']: item['count'] for item in type_counts}
            
            results.append({
                'period': period,
                'date': stat['period_date'],
                'total_workouts': stat['total_workouts'] or 0,
                'total_duration': stat['total_duration'] or 0,
                'total_distance': stat['total_distance'] or 0,
                'total_calories': stat['total_calories'] or 0,
                'avg_heart_rate': stat['avg_heart_rate'] or 0,
                'workout_types': workout_types
            })
        
        serializer = WorkoutStatsSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def progress(self, request):
        """
        Get cumulative progress over time
        Query params: start_date, end_date
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not end_date:
            end_date = timezone.now()
        else:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        # Get all workouts and calculate cumulative totals
        workouts = WorkoutSession.objects.filter(
            user=request.user,
            start_time__gte=start_date,
            start_time__lte=end_date
        ).annotate(
            date=TruncDate('start_time')
        ).values('date').annotate(
            daily_workouts=Count('id'),
            daily_distance=Sum('total_distance'),
            daily_calories=Sum('total_calories'),
            daily_duration=Sum('duration_minutes')
        ).order_by('date')
        
        # Calculate cumulative values
        cumulative_workouts = 0
        cumulative_distance = 0
        cumulative_calories = 0
        cumulative_duration = 0
        
        results = []
        for workout in workouts:
            cumulative_workouts += workout['daily_workouts']
            cumulative_distance += float(workout['daily_distance'] or 0)
            cumulative_calories += workout['daily_calories'] or 0
            cumulative_duration += workout['daily_duration'] or 0
            
            results.append({
                'date': workout['date'],
                'cumulative_workouts': cumulative_workouts,
                'cumulative_distance': cumulative_distance,
                'cumulative_calories': cumulative_calories,
                'cumulative_duration': cumulative_duration
            })
        
        serializer = WorkoutProgressSerializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """
        Get data formatted for charting libraries (Chart.js, etc.)
        Query params: metric (calories/distance/duration), period (day/week/month)
        """
        metric = request.query_params.get('metric', 'calories')
        period = request.query_params.get('period', 'week')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not end_date:
            end_date = timezone.now()
        else:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if not start_date:
            days = 30 if period == 'day' else 90
            start_date = end_date - timedelta(days=days)
        else:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        # Choose truncation and aggregation
        if period == 'day':
            trunc_func = TruncDate
        elif period == 'week':
            trunc_func = TruncWeek
        else:
            trunc_func = TruncMonth
        
        # Map metric to field
        metric_field_map = {
            'calories': 'total_calories',
            'distance': 'total_distance',
            'duration': 'duration_minutes',
            'workouts': 'id'
        }
        
        field = metric_field_map.get(metric, 'total_calories')
        
        # Aggregate data
        if metric == 'workouts':
            data = WorkoutSession.objects.filter(
                user=request.user,
                start_time__gte=start_date,
                start_time__lte=end_date
            ).annotate(
                period_date=trunc_func('start_time')
            ).values('period_date').annotate(
                value=Count(field)
            ).order_by('period_date')
        else:
            data = WorkoutSession.objects.filter(
                user=request.user,
                start_time__gte=start_date,
                start_time__lte=end_date
            ).annotate(
                period_date=trunc_func('start_time')
            ).values('period_date').annotate(
                value=Sum(field)
            ).order_by('period_date')
        
        # Format for chart
        labels = [item['period_date'].strftime('%Y-%m-%d') for item in data]
        values = [float(item['value'] or 0) for item in data]
        
        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': metric.capitalize(),
                    'data': values,
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 2
                }
            ]
        }
        
        serializer = WorkoutChartDataSerializer(chart_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def heart_rate_zones(self, request, pk=None):
        """
        Analyze heart rate zones for a specific workout
        Zones: Recovery (50-60%), Aerobic (60-70%), Tempo (70-80%), 
               Threshold (80-90%), Maximum (90-100%)
        """
        session = self.get_object()
        
        # Get user's max heart rate (estimate: 220 - age)
        try:
            profile = request.user.fitness_profile
            max_hr = 220 - (profile.age or 30)
        except:
            max_hr = 190  # Default
        
        # Define zones
        zones = [
            ('Recovery', 0.5, 0.6),
            ('Aerobic', 0.6, 0.7),
            ('Tempo', 0.7, 0.8),
            ('Threshold', 0.8, 0.9),
            ('Maximum', 0.9, 1.0)
        ]
        
        # Get all heart rate metrics for this session
        metrics = session.metrics.filter(
            heart_rate__isnull=False
        ).order_by('timestamp')
        
        if not metrics.exists():
            return Response(
                {'detail': 'No heart rate data available for this workout'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        total_readings = metrics.count()
        zone_data = []
        
        for zone_name, lower, upper in zones:
            lower_hr = int(max_hr * lower)
            upper_hr = int(max_hr * upper)
            
            count = metrics.filter(
                heart_rate__gte=lower_hr,
                heart_rate__lt=upper_hr
            ).count()
            
            percentage = (count / total_readings * 100) if total_readings > 0 else 0
            
            # Estimate time in zone (assuming metrics are evenly spaced)
            time_in_zone = int((count / total_readings) * (session.duration_minutes or 0))
            
            zone_data.append({
                'zone_name': zone_name,
                'zone_range': f'{lower_hr}-{upper_hr} BPM',
                'time_in_zone': time_in_zone,
                'percentage': round(percentage, 2)
            })
        
        serializer = HeartRateZoneSerializer(zone_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get overall summary statistics for the user
        """
        workouts = WorkoutSession.objects.filter(user=request.user)
        
        summary = workouts.aggregate(
            total_workouts=Count('id'),
            total_distance=Sum('total_distance'),
            total_calories=Sum('total_calories'),
            total_duration=Sum('duration_minutes'),
            avg_duration=Avg('duration_minutes'),
            avg_heart_rate=Avg('avg_heart_rate'),
            max_distance=Max('total_distance'),
            favorite_workout=Count('workout_type')
        )
        
        # Get workout type distribution
        type_distribution = workouts.values('workout_type').annotate(
            count=Count('id'),
            total_duration=Sum('duration_minutes')
        ).order_by('-count')
        
        # Get recent trend (last 7 days vs previous 7 days)
        today = timezone.now()
        last_week = workouts.filter(
            start_time__gte=today - timedelta(days=7)
        ).aggregate(
            count=Count('id'),
            distance=Sum('total_distance')
        )
        
        previous_week = workouts.filter(
            start_time__gte=today - timedelta(days=14),
            start_time__lt=today - timedelta(days=7)
        ).aggregate(
            count=Count('id'),
            distance=Sum('total_distance')
        )
        
        return Response({
            'overall': summary,
            'workout_distribution': list(type_distribution),
            'recent_trend': {
                'last_week': last_week,
                'previous_week': previous_week
            }
        })


class WorkoutMetricViewSet(viewsets.ModelViewSet):
    """ViewSet for workout metrics (time series data)"""
    serializer_class = WorkoutMetricSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get metrics for user's workouts"""
        session_id = self.request.query_params.get('session_id')
        queryset = WorkoutMetric.objects.filter(
            session__user=self.request.user
        )
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        return queryset.select_related('session')
    
    def perform_create(self, serializer):
        """Validate that the session belongs to the user"""
        session = serializer.validated_data['session']
        if session.user != self.request.user:
            raise serializers.ValidationError(
                "You can only add metrics to your own workouts"
            )
        serializer.save()