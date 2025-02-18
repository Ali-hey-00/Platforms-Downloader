from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from redis import Redis
from redis.exceptions import RedisError
from django.conf import settings
import os

def health_check(request):
    """
    Health check endpoint for monitoring system status
    """
    health = {
        'status': 'healthy',
        'database': True,
        'redis': True,
        'media_writable': True
    }
    
    # Check database connection
    try:
        connections['default'].cursor()
    except OperationalError:
        health['database'] = False
        health['status'] = 'unhealthy'

    # Check Redis connection
    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        redis_client.ping()
    except RedisError:
        health['redis'] = False
        health['status'] = 'unhealthy'

    # Check media directory is writable
    media_path = os.path.join(settings.MEDIA_ROOT, 'downloads')
    if not os.path.exists(media_path):
        try:
            os.makedirs(media_path)
        except OSError:
            health['media_writable'] = False
            health['status'] = 'unhealthy'

    status_code = 200 if health['status'] == 'healthy' else 503
    return JsonResponse(health, status=status_code)