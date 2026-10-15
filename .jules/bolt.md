## 2024-10-15 - N+1 Write Issue with WorkoutMetrics
**Learning:** Using `objects.create` in a loop for time-series data (like workout metrics) causes significant database write overhead (an N+1 insert problem).
**Action:** Always use `bulk_create` when handling nested serialization arrays of time-series data in Django REST Framework to process all metrics in a single database roundtrip.
