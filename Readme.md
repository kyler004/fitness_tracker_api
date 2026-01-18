# 🏋️ Fitness Tracker API - Complete Guide

## 📋 Project Overview

You've built a comprehensive Fitness Tracker API with Django REST Framework that includes:

✅ User authentication with token-based auth  
✅ User profiles with fitness goals  
✅ Workout session tracking  
✅ Time series data for workout metrics  
✅ Advanced data aggregation (daily/weekly/monthly stats)  
✅ Data visualization endpoints (chart-ready data)  
✅ Heart rate zone analysis  
✅ Progress tracking over time  
✅ Admin interface for data management  
✅ Automatic signal handling  
✅ Input validation and error handling  

---

## 🚀 Complete Setup Instructions

### 1. Install Dependencies

```bash
pip install django djangorestframework
```

### 2. Project Structure

```
fitness_project/
├── manage.py
├── fitness_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── fitness/
    ├── __init__.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── auth_views.py
    ├── signals.py
    ├── validators.py
    ├── exceptions.py
    ├── admin.py
    ├── urls.py
    └── migrations/
```

### 3. Update `settings.py`

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'fitness',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'fitness.exceptions.custom_exception_handler',
}
```

### 4. Update main `urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('fitness.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run the Server

```bash
python manage.py runserver
```

---

## 🔗 API Endpoints Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | Login and get token | No |
| POST | `/api/auth/logout/` | Logout (delete token) | Yes |
| GET | `/api/auth/me/` | Get current user info | Yes |

### User Profile Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profiles/` | List profiles |
| POST | `/api/profiles/` | Create profile |
| GET | `/api/profiles/{id}/` | Get profile details |
| PUT/PATCH | `/api/profiles/{id}/` | Update profile |

### Workout Session Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workouts/` | List workouts (with filtering) |
| POST | `/api/workouts/` | Create workout (with metrics) |
| GET | `/api/workouts/{id}/` | Get workout details |
| PUT/PATCH | `/api/workouts/{id}/` | Update workout |
| DELETE | `/api/workouts/{id}/` | Delete workout |

### Aggregation & Visualization Endpoints

| Method | Endpoint | Description | Query Params |
|--------|----------|-------------|--------------|
| GET | `/api/workouts/statistics/` | Get aggregated stats | period, start_date, end_date |
| GET | `/api/workouts/progress/` | Get cumulative progress | start_date, end_date |
| GET | `/api/workouts/chart_data/` | Get chart-ready data | metric, period, dates |
| GET | `/api/workouts/{id}/heart_rate_zones/` | Analyze HR zones | - |
| GET | `/api/workouts/summary/` | Overall summary | - |

### Workout Metrics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/metrics/` | List metrics |
| POST | `/api/metrics/` | Create metric |
| GET | `/api/metrics/{id}/` | Get metric details |
| PUT/PATCH | `/api/metrics/{id}/` | Update metric |

---

## 📊 Example API Usage

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com"
  }
}
```

### 2. Create a Workout with Time Series Data

```bash
curl -X POST http://localhost:8000/api/workouts/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "workout_type": "running",
    "title": "Morning Run",
    "description": "Beautiful sunrise run",
    "start_time": "2024-01-15T07:00:00Z",
    "end_time": "2024-01-15T07:45:00Z",
    "total_distance": 5.2,
    "total_calories": 450,
    "avg_heart_rate": 145,
    "max_heart_rate": 165,
    "metrics": [
      {
        "timestamp": "2024-01-15T07:00:00Z",
        "heart_rate": 120,
        "speed": 8.5,
        "distance": 0
      },
      {
        "timestamp": "2024-01-15T07:15:00Z",
        "heart_rate": 145,
        "speed": 9.2,
        "distance": 2.3
      },
      {
        "timestamp": "2024-01-15T07:30:00Z",
        "heart_rate": 155,
        "speed": 10.1,
        "distance": 4.1
      },
      {
        "timestamp": "2024-01-15T07:45:00Z",
        "heart_rate": 140,
        "speed": 8.0,
        "distance": 5.2
      }
    ]
  }'
```

### 3. Get Weekly Statistics

```bash
curl -X GET "http://localhost:8000/api/workouts/statistics/?period=week&start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Response:**
```json
[
  {
    "period": "week",
    "date": "2024-01-15",
    "total_workouts": 5,
    "total_duration": 245,
    "total_distance": 28.5,
    "total_calories": 2100,
    "avg_heart_rate": 142.5,
    "workout_types": {
      "running": 3,
      "cycling": 2
    }
  }
]
```

### 4. Get Chart Data

```bash
curl -X GET "http://localhost:8000/api/workouts/chart_data/?metric=distance&period=day" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "labels": ["2024-01-15", "2024-01-16", "2024-01-17"],
  "datasets": [
    {
      "label": "Distance",
      "data": [5.2, 8.1, 6.5],
      "backgroundColor": "rgba(75, 192, 192, 0.2)",
      "borderColor": "rgba(75, 192, 192, 1)",
      "borderWidth": 2
    }
  ]
}
```

---

## 🎨 Django Admin

Access the admin interface at: `http://localhost:8000/admin/`

Features:
- Color-coded BMI display
- Inline metrics editing within workout sessions
- Formatted displays for duration, distance, calories
- Advanced filtering and search
- Optimized queries with prefetch_related

---

## 🧪 Testing the API

### Using Python

```python
import requests

# Register
response = requests.post('http://localhost:8000/api/auth/register/', json={
    'username': 'testuser',
    'password': 'testpass123',
    'email': 'test@example.com'
})
token = response.json()['token']

# Create workout
headers = {'Authorization': f'Token {token}'}
workout = {
    'workout_type': 'running',
    'title': 'Evening Run',
    'start_time': '2024-01-15T18:00:00Z',
    'end_time': '2024-01-15T18:30:00Z',
    'total_distance': 4.0,
    'total_calories': 350
}
response = requests.post('http://localhost:8000/api/workouts/', 
                        json=workout, headers=headers)
print(response.json())

# Get statistics
response = requests.get('http://localhost:8000/api/workouts/statistics/',
                       headers=headers)
print(response.json())
```

---

## 🔒 Security Features

- ✅ Token-based authentication
- ✅ User-scoped data (users can only access their own workouts)
- ✅ Input validation (negative values, invalid dates, etc.)
- ✅ Custom error handling with detailed messages
- ✅ CSRF protection (for session auth)

---

## 📈 Key Features Explained

### Time Series Data

The `WorkoutMetric` model stores timestamped data points:
- Heart rate every 30 seconds
- Speed/distance updates every minute
- Real-time tracking during workouts

### Data Aggregation

Django ORM aggregations provide powerful analytics:
- `Count()` - Number of workouts
- `Sum()` - Total distance, calories
- `Avg()` - Average heart rate
- `TruncDate/TruncWeek/TruncMonth` - Group by time period

### Visualization Endpoints

Data is pre-formatted for charting libraries:
- Chart.js compatible format
- Labels and datasets ready to use
- No frontend processing needed

---

## 🎯 What You've Learned

1. **Django Models**: Relationships (OneToOne, ForeignKey), validators, indexes
2. **DRF Serializers**: Nested serialization, custom validation, computed fields
3. **ViewSets**: CRUD operations, custom actions, query optimization
4. **Django ORM**: Complex queries, aggregations, annotations
5. **Authentication**: Token-based auth, permissions
6. **Signals**: Automatic model creation on user registration
7. **Admin Customization**: Custom displays, inlines, filters
8. **API Design**: RESTful endpoints, query parameters, error handling

---

## 🚀 Next Steps (Optional Enhancements)

- Add file uploads for workout photos
- Implement workout goals and achievements
- Add social features (follow users, leaderboards)
- Create PDF reports of workout history
- Add push notifications for workout reminders
- Implement workout recommendations based on history
- Add export functionality (CSV, JSON)
- Create a frontend dashboard with React/Vue

---

## 📝 Summary

**Your Fitness Tracker API is now COMPLETE and production-ready!** 

You have:
- ✅ Full CRUD operations
- ✅ Authentication system
- ✅ Time series data handling
- ✅ Advanced aggregations
- ✅ Visualization endpoints
- ✅ Admin interface
- ✅ Validation and error handling
- ✅ Automatic signal handling

The API is ready to be consumed by a frontend application or mobile app!

---

## 🤝 Contributing

This is a complete, working API. You can extend it based on your needs!

Happy coding! 🎉