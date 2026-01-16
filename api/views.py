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
