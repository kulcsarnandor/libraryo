from django.contrib import admin
from django_apscheduler.models import DjangoJob, DjangoJobExecution

# ne jelenjen meg a helyi schedule/cronjob felulet feleslegesen a django adminban.
if DjangoJob in admin.site._registry:
    admin.site.unregister(DjangoJob)

if DjangoJobExecution in admin.site._registry:
    admin.site.unregister(DjangoJobExecution)