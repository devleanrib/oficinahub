from django.db import models


class ShopSettings(models.Model):
    name = models.CharField("Nome da Oficina", max_length=200, default="Oficina Original")
    address = models.CharField("Endereco", max_length=300, default="Rua Santa Helena, 12 - Bairro da Paz")
    phone = models.CharField("Telefone", max_length=20, default="(92) 99389-8610")
    email = models.EmailField("E-mail", blank=True, default="")
    mechanic_name = models.CharField("Mecanico Responsavel", max_length=200, default="Mecanico Responsavel")
    mechanic_credential = models.CharField("Credencial", max_length=100, default="CTPS / CFC XXXXX")

    class Meta:
        verbose_name = "Configuracao da Oficina"
        verbose_name_plural = "Configuracoes da Oficina"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and ShopSettings.objects.exists():
            existing = ShopSettings.objects.first()
            self.pk = existing.pk
        super().save(*args, **kwargs)


class Diagnosis(models.Model):
    SEVERITY_CHOICES = [
        ("Baixa", "Baixa"),
        ("Media", "Media"),
        ("Alta", "Alta"),
        ("Critica", "Critica"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    client_name = models.CharField("Nome do Cliente", max_length=200, blank=True, default="")
    client_document = models.CharField("CPF/CNPJ", max_length=20, blank=True, default="")
    client_phone = models.CharField("Telefone do Cliente", max_length=20, blank=True, default="")
    vehicle_brand = models.CharField("Marca", max_length=100, blank=True, default="")
    vehicle_model = models.CharField("Modelo", max_length=100, blank=True, default="")
    vehicle_year = models.CharField("Ano", max_length=10, blank=True, default="")
    vehicle_engine = models.CharField("Motorizacao", max_length=50, blank=True, default="")
    vehicle_fuel = models.CharField("Combustivel", max_length=30, blank=True, default="")
    vehicle_transmission = models.CharField("Transmissao", max_length=30, blank=True, default="")
    vehicle_mileage = models.IntegerField("Quilometragem", null=True, blank=True)
    vehicle_plate = models.CharField("Placa", max_length=10, blank=True, default="")
    codes = models.JSONField("Codigos OBD-II", default=list)
    overall_severity = models.CharField("Criticidade Geral", max_length=10, choices=SEVERITY_CHOICES, default="Baixa")
    total_codes = models.IntegerField("Total de Codigos", default=0)
    summary = models.TextField("Resumo", blank=True, default="")
    conclusion = models.TextField("Conclusao", blank=True, default="")
    results = models.JSONField("Resultados", default=list)
    report_html = models.TextField("HTML do Relatorio", blank=True, default="")

    class Meta:
        verbose_name = "Diagnostico"
        verbose_name_plural = "Diagnosticos"
        ordering = ["-created_at"]

    def __str__(self):
        vehicle = f"{self.vehicle_brand} {self.vehicle_model}".strip()
        return f"{vehicle or 'Sem veiculo'} - {self.total_codes} codigos ({self.created_at:%d/%m/%Y %H:%M})"

    @property
    def vehicle_display(self):
        parts = [self.vehicle_brand, self.vehicle_model, self.vehicle_year]
        return " ".join(p for p in parts if p).strip() or "Nao informado"
