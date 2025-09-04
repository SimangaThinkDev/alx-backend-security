from .celery import app as celery_app

# So the django app includes celery in it's startup
__all__ = ('celery_app',)
