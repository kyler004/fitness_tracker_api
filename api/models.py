from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Create your models here.

class UserProfile(models.Model): 
    """Extended user profile with fitness-related information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fitness_profile')
    age = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(120)])
    weight = models.DecimalField(max_digits=5,  decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    height = models.DecimalField(max_digits=5,  decimal_places=2, null=True, blank=True, help_text="Height in kg")
    fitness_goal = models.CharField(
        max_length=50, 
        choices=[
            ('weight_loss', 'Weight Loss'), 
            ('muscle_gain', 'Muscle Gain'), 
            ('endurance', 'Endurance'), 
            ('general_fitness', 'General Fitness'), 
        ], 
        default='general_fitness'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_new=True)

    def __str__(self): 
        return f"{self.user.username}'s Profile"
    
    class Meta: 
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class WorkoutSession(models.Model): 
    """Represents single workout session"""

    WORKOUT_TYPES = [
        ('running', 'Running'), 
        ('cycling', 'Cycling'), 
        ('swimming', 'Swimming'), 
        ('weight_training', 'Weight Training'), 
        ('yoga', 'Yoga'), 
        ('hiit', 'HIIT'), 
        ('walking', 'Walking'),
        ('other', 'Other'),  
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    workout_type = models.CharField(max_length=50, choices=WORKOUT_TYPES)
    title = models.CharField(max_length=200, help_text="e.g., 'Morning in the Park'")
    description = models.TextField(blank=True)

    # Time tracking
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True, help_text="Duration in minutes")

    # Summary metrics
    total_distance = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Total distance in km"
    )
    total_calories = models.IntegerField(null=True, blank=True, help_text="Calories burned")
    avg_heart_rate = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(30), MaxValueValidator(250)]
    )
    max_heart_rate = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(30), MaxValueValidator(250)]
    )

    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.start_time.date()})"

    def save(self, *args, **kwargs):
        """Calculate duration if end_time is set"""
        if self.end_time and self.start_time: 
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)
            super().save(*args, **kwargs)
    
    class Meta: 
        ordering = ['-start_time']
        verbose_name = "Workout Session"
        verbose_name_plural = "Workout Sessions"
        indexes = [
            models.Index(fields=['-start_time']),
            models.Index(fields=['user', '-start_time']), 
            models.Index(fields=['workout_type']), 
        ]
