import os
import logging
from datetime import datetime
from dataclasses import dataclass, field

from jinja2 import Environment, FileSystemLoader

from models import DiagnosticReport, VehicleInfo

logger = logging.getLogger(__name__)


@dataclass
class ReportContext:
    report: DiagnosticReport
    vehicle: VehicleInfo = field(default_factory=VehicleInfo)
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
    report_date: str = field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y"))
    report_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S"))

    @property
    def has_critical(self) -> bool:
        return any(not r.can_operate for r in self.report.results)

    @property
    def has_vehicle_info(self) -> bool:
        return self.vehicle.has_info()

    def to_dict(self) -> dict:
        return {
            "report": self.report,
            "vehicle": self.vehicle,
            "has_vehicle_info": self.has_vehicle_info,
            "shop_name": self.shop_name,
            "shop_address": self.shop_address,
            "shop_phone": self.shop_phone,
            "shop_logo": self.shop_logo,
            "client_name": self.client_name,
            "client_document": self.client_document,
            "client_phone": self.client_phone,
            "vehicle_brand": self.vehicle_brand,
            "vehicle_model": self.vehicle_model,
            "vehicle_year": self.vehicle_year,
            "vehicle_plate": self.vehicle_plate,
            "vehicle_vin": self.vehicle_vin,
            "mechanic_name": self.mechanic_name,
            "mechanic_credential": self.mechanic_credential,
            "report_date": self.report_date,
            "report_id": self.report_id,
            "has_critical": self.has_critical,
        }


class PDFGenerator:
    def __init__(self, templates_dir: str = "templates", static_dir: str = "static", output_dir: str = "output"):
        self.templates_dir = templates_dir
        self.static_dir = static_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True,
        )
        logger.debug("PDFGenerator inicializado. Templates: %s | Static: %s", templates_dir, static_dir)

    def generate_html(self, context: ReportContext, template_name: str = "client_report.html") -> str:
        template = self.env.get_template(template_name)
        css_path = os.path.abspath(os.path.join(self.static_dir, "style.css"))
        
        css_content = ""
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
        
        html_content = template.render(css_path=css_path, css_content=css_content, **context.to_dict())
        logger.debug("HTML gerado com sucesso (%d caracteres)", len(html_content))
        return html_content

    def save_html(self, html_content: str, filename: str | None = None) -> str:
        if filename is None:
            filename = f"laudo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info("HTML salvo em: %s", filepath)
        return filepath

    def generate_pdf(self, html_content: str, filename: str | None = None) -> str:
        try:
            from weasyprint import HTML
        except ImportError:
            raise ImportError(
                "WeasyPrint nao esta instalado. Instale com: pip install weasyprint"
            )

        if filename is None:
            filename = f"laudo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        filepath = os.path.join(self.output_dir, filename)
        html = HTML(string=html_content)
        html.write_pdf(filepath)

        logger.info("PDF gerado em: %s", filepath)
        return filepath

    def generate(self, context: ReportContext, save_html: bool = True, save_pdf: bool = True) -> dict:
        html_content = self.generate_html(context)

        results = {"html_content": html_content}

        if save_html:
            results["html_path"] = self.save_html(html_content)

        if save_pdf:
            results["pdf_path"] = self.generate_pdf(html_content)

        return results