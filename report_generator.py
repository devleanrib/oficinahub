import logging
from dataclasses import dataclass, field
from datetime import datetime

from models import DiagnosticReport, VehicleInfo

logger = logging.getLogger(__name__)


@dataclass
class ReportMetadata:
    shop_name: str = "Oficina Mecanica Premium"
    shop_address: str = "Rua Principal, 123 - Centro"
    shop_phone: str = "(11) 3456-7890"
    shop_logo: str | None = None
    client_name: str = "Cliente"
    client_document: str = "***.***.***-**"
    client_phone: str = "(**) *****-****"
    vehicle_brand: str = "Marca"
    vehicle_model: str = "Modelo"
    vehicle_year: str = "Ano/Modelo"
    vehicle_plate: str = "ABC-1234"
    vehicle_vin: str = "***************"
    mechanic_name: str = "Mecanico Responsavel"
    mechanic_credential: str = "CTPS / CFC XXXXX"


class ReportGenerator:
    def __init__(self, metadata: ReportMetadata | None = None):
        self.metadata = metadata or ReportMetadata()
        logger.debug("ReportGenerator inicializado")

    def prepare_context(self, report: DiagnosticReport, vehicle: VehicleInfo | None = None) -> dict:
        from pdf_generator import ReportContext

        vehicle = vehicle or VehicleInfo()

        context = ReportContext(
            report=report,
            vehicle=vehicle,
            shop_name=self.metadata.shop_name,
            shop_address=self.metadata.shop_address,
            shop_phone=self.metadata.shop_phone,
            shop_logo=self.metadata.shop_logo,
            client_name=self.metadata.client_name,
            client_document=self.metadata.client_document,
            client_phone=self.metadata.client_phone,
            vehicle_brand=vehicle.brand or self.metadata.vehicle_brand,
            vehicle_model=vehicle.model or self.metadata.vehicle_model,
            vehicle_year=vehicle.year or self.metadata.vehicle_year,
            vehicle_plate=vehicle.plate or self.metadata.vehicle_plate,
            vehicle_vin=self.metadata.vehicle_vin,
            mechanic_name=self.metadata.mechanic_name,
            mechanic_credential=self.metadata.mechanic_credential,
        )

        logger.info("Contexto preparado para relatorio com %d codigos", report.total_codes)
        return context