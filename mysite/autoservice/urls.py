from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("automobiliai/", views.automobiliai, name="automobiliai"),
    path("automobiliai/<int:auto_id>", views.automobilis, name="automobilis"),
    path("uzsakymai/", views.UzsakymasListView.as_view(), name="uzsakymai"),
    path("uzsakymai/<int:pk>", views.UzsakymasDetailView.as_view(), name="uzsakymas"),
]