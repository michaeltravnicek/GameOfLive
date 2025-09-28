from django.apps import AppConfig


class LeaderboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leaderboard'
    
    # def ready(self):
    #     from .tasks import run_google_sheet_sync
    #     from background_task.models import Task
    #     if not Task.objects.filter(task_name="leaderboard.tasks.run_google_sheet_sync").exists():
    #         run_google_sheet_sync(repeat=60)