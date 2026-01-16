from django.shortcuts import render
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
# Create your views here.

class UserProfileViewSet(viewsets.ModelViewSet): 
    """ViewSet for User fitness profiles"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Users for user fitness profiles"""
        return UserProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer): 
        """Associate profile with current user"""
        serializer.save(user=self.request.user)

class WorkoutSessionViewSet(viewsets.ModelViewSet): 
    """ViewSet for workout sessions with aggregation endpoint"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Users can only access their own workouts"""
        queryset = WorkoutSession.objects.filter(user=self.request.user)

        # Filter date by range if provided
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

    def get_serializer(self):
        """Use different serializers for different actions"""
        if self.action == 'list': 
            return WorkoutSessionListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return WorkoutSessionCreateSerializer
        return WorkoutSessionDetailSerializer
    def perform_create(self, serializer):
        """Associate workout with current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, method=['get'])
    def statistics(self, request): 
        """
        Docstring for statistics
        
        :param self: Description
        :param request: Description

        get aggregated statistics for a time period
        Query params: period (day/week/month), start_date, end_date
        """

        period = request.query_params.get('period', 'week')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Default to last 30 days if no dates is provided
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

        # Add workout type breakdoswn for each period
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
        Docstring for progress
        
        :param self: Description
        :param request: Description

        Get cummulative progress over time
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
        
        #Get all workouts and calculate cumulative totals
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