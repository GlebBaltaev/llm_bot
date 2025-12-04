from django.urls import path
from .views import GetMessagesView, DialogsView, index, DeleteThreadView

urlpatterns = [
    path("", index, name="index"),
    path("dialogs/", DialogsView.as_view(), name="dialogs"),
    path('get_messages/', GetMessagesView.as_view(), name='get_messages'),
    path('delete_thread/', DeleteThreadView.as_view(), name='delete_thread'),
]

