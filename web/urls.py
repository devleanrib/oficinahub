from django.urls import path
from web import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("analise/", views.nova_analise, name="nova_analise"),
    path("resultado/<int:diagnosis_id>/", views.resultado, name="resultado"),
    path("pdf/<int:diagnosis_id>/", views.gerar_pdf, name="gerar_pdf"),
    path("historico/", views.historico, name="historico"),
    path("diagnostico/<int:diagnosis_id>/", views.diagnostico_detalhes, name="diagnostico_detalhes"),
    path("configuracoes/", views.configuracoes, name="configuracoes"),
]
