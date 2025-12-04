from django.shortcuts import render
from .models import DialogHistory
from asgiref.sync import sync_to_async

def thread_list(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    tread_id = request.GET.get("tread_id")

    # Call the async fetch_dialogs method using sync_to_async
    dialogs = sync_to_async(Database.fetch_dialogs)("2024-01-01", "2025-01-31", 123)

    # Query all data
    threads = DialogHistory.objects.all()

    # Filter by thread ID
    if tread_id:
        threads = threads.filter(id_tread=tread_id)
        if start_date and end_date:
            threads = threads.filter(created_at__range=[start_date, end_date])
    elif start_date and end_date:
        threads = threads.filter(created_at__range=[start_date, end_date])

    return render(request, "index.html", {"threads": threads, "dialogs": dialogs})