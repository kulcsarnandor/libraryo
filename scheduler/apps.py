from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduler'
    '''
    #import threading 
    #import os
    #mielott felraktuk volna a render webszerverre, lokalisan futtattuk a cronjob-ot...
    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true':
            return
            
        from .commands import scheduler
        scheduler.start_borrowing_overdue_scheduler()
    '''