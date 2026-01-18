# fitness/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, WorkoutSession, WorkoutMetric


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for User Profiles"""
    list_display = ['user', 'age', 'weight', 'height', 'bmi_display', 'fitness_goal', 'created_at']
    list_filter = ['fitness_goal', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'bmi_display']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Physical Stats', {
            'fields': ('age', 'weight', 'height', 'bmi_display')
        }),
        ('Fitness', {
            'fields': ('fitness_goal',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def bmi_display(self, obj):
        """Calculate and display BMI"""
        if obj.weight and obj.height:
            height_m = float(obj.height) / 100
            bmi = float(obj.weight) / (height_m ** 2)
            
            # Color code based on BMI ranges
            if bmi < 18.5:
                color = 'blue'
                category = 'Underweight'
            elif bmi < 25:
                color = 'green'
                category = 'Normal'
            elif bmi < 30:
                color = 'orange'
                category = 'Overweight'
            else:
                color = 'red'
                category = 'Obese'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.2f} ({})</span>',
                color, bmi, category
            )
        return '-'
    
    bmi_display.short_description = 'BMI'


class WorkoutMetricInline(admin.TabularInline):
    """Inline display of workout metrics within workout session"""
    model = WorkoutMetric
    extra = 1
    fields = ['timestamp', 'heart_rate', 'speed', 'distance', 'cadence', 'power']
    
    def get_readonly_fields(self, request, obj=None):
        """Make timestamp readonly when editing"""
        if obj:
            return ['timestamp']
        return []


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    """Admin interface for Workout Sessions"""
    list_display = [
        'title', 'user', 'workout_type', 'start_time', 
        'duration_display', 'distance_display', 'calories_display',
        'metrics_count'
    ]
    list_filter = ['workout_type', 'start_time', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['duration_minutes', 'created_at', 'updated_at', 'metrics_count']
    date_hierarchy = 'start_time'
    inlines = [WorkoutMetricInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'workout_type', 'title', 'description')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'duration_minutes')
        }),
        ('Metrics Summary', {
            'fields': ('total_distance', 'total_calories', 'avg_heart_rate', 'max_heart_rate')
        }),
        ('Additional Info', {
            'fields': ('notes', 'metrics_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """Format duration nicely"""
        if obj.duration_minutes:
            hours = obj.duration_minutes // 60
            minutes = obj.duration_minutes % 60
            if hours > 0:
                return f'{hours}h {minutes}m'
            return f'{minutes}m'
        return '-'
    
    duration_display.short_description = 'Duration'
    duration_display.admin_order_field = 'duration_minutes'
    
    def distance_display(self, obj):
        """Format distance with unit"""
        if obj.total_distance:
            return format_html(
                '<span style="font-weight: bold;">{:.2f} km</span>',
                obj.total_distance
            )
        return '-'
    
    distance_display.short_description = 'Distance'
    distance_display.admin_order_field = 'total_distance'
    
    def calories_display(self, obj):
        """Format calories with styling"""
        if obj.total_calories:
            return format_html(
                '<span style="color: #ff6b6b; font-weight: bold;">{} kcal</span>',
                obj.total_calories
            )
        return '-'
    
    calories_display.short_description = 'Calories'
    calories_display.admin_order_field = 'total_calories'
    
    def metrics_count(self, obj):
        """Count of associated metrics"""
        count = obj.metrics.count()
        if count > 0:
            return format_html(
                '<span style="background-color: #4CAF50; color: white; padding: 3px 8px; border-radius: 3px;">{} metrics</span>',
                count
            )
        return format_html('<span style="color: #999;">No metrics</span>')
    
    metrics_count.short_description = 'Time Series Data'
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch"""
        qs = super().get_queryset(request)
        return qs.select_related('user').prefetch_related('metrics')


@admin.register(WorkoutMetric)
class WorkoutMetricAdmin(admin.ModelAdmin):
    """Admin interface for Workout Metrics (Time Series Data)"""
    list_display = [
        'session_link', 'timestamp', 'heart_rate', 'speed', 
        'distance', 'cadence', 'power'
    ]
    list_filter = ['timestamp', 'session__workout_type']
    search_fields = ['session__title', 'session__user__username']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Session', {
            'fields': ('session', 'timestamp')
        }),
        ('Cardio Metrics', {
            'fields': ('heart_rate', 'speed', 'distance', 'cadence')
        }),
        ('Power & Elevation', {
            'fields': ('power', 'elevation'),
            'classes': ('collapse',)
        }),
        ('Strength Training', {
            'fields': ('weight_lifted', 'reps', 'sets'),
            'classes': ('collapse',)
        }),
    )
    
    def session_link(self, obj):
        """Create a clickable link to the session"""
        from django.urls import reverse
        from django.utils.html import format_html
        
        url = reverse('admin:fitness_workoutsession_change', args=[obj.session.id])
        return format_html('<a href="{}">{}</a>', url, obj.session.title)
    
    session_link.short_description = 'Workout Session'
    session_link.admin_order_field = 'session__title'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('session', 'session__user')


# Customize admin site header and title
admin.site.site_header = 'Fitness Tracker Administration'
admin.site.site_title = 'Fitness Tracker Admin'
admin.site.index_title = 'Welcome to Fitness Tracker Admin Portal'