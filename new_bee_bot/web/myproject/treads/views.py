from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.db import connection
from .utils import Database
import asyncpg
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import connection

def index(request):
    return render(request, "index.html")

class DialogsView(View):
    async def get(self, request):
        print("\n=== Запрос в DialogsView получен ===")
        
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        id_tread = request.GET.get("id_tread")

        print(f"Получены параметры: start_date={start_date}, end_date={end_date}, id_tread={id_tread}")

        try:
            data = await Database.fetch_dialogs(start_date, end_date, id_tread)
            print(f"\nПолучено записей: {len(data)}")

            return render(request, "index.html", {
                "threads": data,
                "start_date": start_date,
                "end_date": end_date,
                "id_tread": id_tread
            })
        except Exception as e:
            print(f"\nОШИБКА: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

class GetMessagesView(View):
    async def get(self, request):
        start_date = request.GET.get("start_date")
        id_tread = request.GET.get("id_tread")
        end_date = request.GET.get("end_date")
        
        if not id_tread:
            return JsonResponse({"error": "Не указан ID треда"}, status=400)

        try:
            messages = await Database.fetch_messages(id_tread, start_date, end_date)  # Нужно реализовать в utils
            return JsonResponse({"messages": messages})
        except Exception as e:
            print(f"\nОШИБКА: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteThreadView(View):
    def delete(self, request):
        id_tread = request.GET.get('id_tread')
        if not id_tread:
            return JsonResponse({'error': 'ID треда не указан'}, status=400)

        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM users_treads WHERE id_tread = %s", [id_tread])
                cursor.execute("DELETE FROM dialogs_history WHERE id_tread = %s", [id_tread])

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
