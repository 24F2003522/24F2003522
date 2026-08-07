# from celery import Celery
# from celery.schedules import crontab
# from datetime import timedelta
# import os
# import platform
# from dotenv import load_dotenv

# # Load .env file
# load_dotenv()

# # Create celery instance first
# celery = Celery(
#     'celery_app',
#     broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
#     backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
#     include=['tasks'],
# )
# celery_app = celery

# # Configure celery
# celery.conf.update(
#     task_serializer='json',
#     accept_content=['json'],
#     result_serializer='json',
#     timezone='UTC',
#     enable_utc=True,
# )

# # Prefer solo pool on Windows to avoid Windows spawn issues with prefork.
# if platform.system() == 'Windows':
#     celery.conf.update(worker_pool='solo')

# # Auto-discover tasks at module import time so workers see registered tasks
# celery.autodiscover_tasks(['tasks'])

# # Set schedule for background jobs
# celery.conf.beat_schedule = {
#     # Send reminder every 1 minute (for testing)
#     'send-daily-reminder': {
#         'task': 'tasks.send_daily_reminder',
#         'schedule': timedelta(hours=5, minutes=26),
#     },
#     # Generate report on 1st of month at 9 AM
#     'generate-monthly-report': {
#         'task': 'tasks.generate_monthly_report',
#         'schedule': crontab(day_of_month=0, hour=0, minute=1),
#     },
# }

# # Function for Flask app
# def make_celery(app):
#     celery_app.conf.update(app.config)
    
#     # Auto-discover tasks
#     celery_app.autodiscover_tasks(['tasks'])
    
#     return celery_app

# # Ensure tasks are imported when the Celery app is imported.
# # This helps Windows worker child processes load the registered tasks.
# import tasks
