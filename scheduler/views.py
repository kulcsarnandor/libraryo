from django.http import JsonResponse
from .commands.scheduler import check_if_borrowing_overdue
import os

def run_cronjob_overdue(request):
    CRONJOB_SECRET = os.environ.get('CRONJOB_SECRET')

    request_token = request.GET.get('token')

    if request_token != CRONJOB_SECRET:
        return JsonResponse({"status": "error", "message": "UNAUTHORIZED..."}, status=403)
    
    try:
        check_if_borrowing_overdue()
        return JsonResponse({"status": "success", "message": "OVERDUE BORROWING CHECK DONE."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)