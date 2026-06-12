import json
import logging

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from web.models import Diagnosis, ShopSettings
from config import load_config
from ai_client import AIClient
from diagnostic_service import DiagnosticService
from report_generator import ReportGenerator, ReportMetadata
from pdf_generator import PDFGenerator
from models import InputData, VehicleInfo

logger = logging.getLogger(__name__)


def dashboard(request):
    total = Diagnosis.objects.count()
    last = Diagnosis.objects.first()
    context = {"total_diagnoses": total, "last_diagnosis": last}
    return render(request, "web/dashboard.html", context)


def nova_analise(request):
    if request.method == "POST":
        step = request.POST.get("step", "1")

        if step == "1":
            request.session["vehicle"] = {
                "brand": request.POST.get("brand", "").strip(),
                "model": request.POST.get("model", "").strip(),
                "year": request.POST.get("year", "").strip(),
                "engine": request.POST.get("engine", "").strip(),
                "fuel": request.POST.get("fuel", "").strip(),
                "transmission": request.POST.get("transmission", "").strip(),
                "mileage": request.POST.get("mileage", "").strip(),
                "plate": request.POST.get("plate", "").strip(),
            }
            return render(request, "web/analise.html", {"step": "2", "vehicle": request.session["vehicle"]})

        if step == "2":
            codes_raw = request.POST.get("codes", "").strip()
            if not codes_raw:
                messages.error(request, "Informe pelo menos um codigo OBD-II.")
                return render(request, "web/analise.html", {"step": "2", "vehicle": request.session.get("vehicle", {})})

            codes = [c.strip().upper() for c in codes_raw.split(",") if c.strip()]
            request.session["codes"] = codes
            return render(request, "web/analise.html", {
                "step": "3",
                "vehicle": request.session.get("vehicle", {}),
                "codes": codes,
            })

        if step == "3":
            return _execute_diagnosis(request)

    return render(request, "web/analise.html", {"step": "1"})


def _execute_diagnosis(request):
    vehicle_data = request.session.get("vehicle", {})
    codes = request.session.get("codes", [])

    if not codes:
        messages.error(request, "Nenhum codigo para analisar.")
        return redirect("nova_analise")

    mileage = vehicle_data.get("mileage")
    vehicle = VehicleInfo(
        brand=vehicle_data.get("brand", ""),
        model=vehicle_data.get("model", ""),
        year=vehicle_data.get("year", ""),
        engine=vehicle_data.get("engine", ""),
        fuel=vehicle_data.get("fuel", ""),
        transmission=vehicle_data.get("transmission", ""),
        mileage=int(mileage) if mileage and mileage.isdigit() else None,
        plate=vehicle_data.get("plate", ""),
    )

    try:
        config = load_config()
        ai_client = AIClient(config)
        service = DiagnosticService(ai_client)
        input_data = InputData.from_list(codes, "web", vehicle)
        report = service.diagnose(input_data)

        shop = ShopSettings.objects.first()
        metadata = ReportMetadata(
            shop_name=shop.name if shop else "Oficina Mecanica Premium",
            shop_address=shop.address if shop else "",
            shop_phone=shop.phone if shop else "",
            mechanic_name=shop.mechanic_name if shop else "",
            mechanic_credential=shop.mechanic_credential if shop else "",
        )
        reporter = ReportGenerator(metadata)
        context_report = reporter.prepare_context(report, vehicle)
        pdf_gen = PDFGenerator(output_dir="output")
        results = pdf_gen.generate(context_report, save_html=True, save_pdf=True)

        diagnosis = Diagnosis.objects.create(
            vehicle_brand=vehicle.brand,
            vehicle_model=vehicle.model,
            vehicle_year=vehicle.year,
            vehicle_engine=vehicle.engine,
            vehicle_fuel=vehicle.fuel,
            vehicle_transmission=vehicle.transmission,
            vehicle_mileage=vehicle.mileage,
            vehicle_plate=vehicle.plate,
            codes=codes,
            overall_severity=report.overall_severity,
            total_codes=report.total_codes,
            summary=report.summary,
            conclusion=report.conclusion,
            results=[{
                "code": r.code, "meaning": r.meaning, "description": r.description,
                "causes": r.causes, "risks": r.risks, "severity": r.severity,
                "recommendations": r.recommendations, "can_operate": r.can_operate,
            } for r in report.results],
            report_html=results.get("html_content", ""),
        )

        messages.success(request, "Diagnostico concluido com sucesso!")
        return redirect("resultado", diagnosis_id=diagnosis.id)

    except ValueError as e:
        messages.error(request, f"Erro de validacao: {e}")
        return redirect("nova_analise")
    except Exception as e:
        logger.exception("Erro ao executar diagnostico")
        messages.error(request, f"Erro ao consultar IA: {e}")
        return redirect("nova_analise")


def resultado(request, diagnosis_id):
    diagnosis = get_object_or_404(Diagnosis, id=diagnosis_id)
    return render(request, "web/resultado.html", {"diagnosis": diagnosis})


def gerar_pdf(request, diagnosis_id):
    diagnosis = get_object_or_404(Diagnosis, id=diagnosis_id)
    if not diagnosis.report_html:
        messages.warning(request, "Relatorio nao encontrado. Gere um novo diagnostico.")
        return redirect("resultado", diagnosis_id=diagnosis.id)

    try:
        from weasyprint import HTML as WHTML
        pdf_bytes = WHTML(string=diagnosis.report_html).write_pdf()
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        filename = f"laudo_{diagnosis.vehicle_brand}_{diagnosis.vehicle_model}_{diagnosis.id}.pdf"
        filename = filename.replace(" ", "_")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        logger.exception("Erro ao gerar PDF")
        messages.error(request, f"Erro ao gerar PDF: {e}")
        return redirect("resultado", diagnosis_id=diagnosis.id)


def historico(request):
    diagnoses = Diagnosis.objects.all()
    return render(request, "web/historico.html", {"diagnoses": diagnoses})


def diagnostico_detalhes(request, diagnosis_id):
    diagnosis = get_object_or_404(Diagnosis, id=diagnosis_id)
    return render(request, "web/diagnostico_detalhes.html", {"diagnosis": diagnosis})


def configuracoes(request):
    shop = ShopSettings.objects.first()
    if not shop:
        shop = ShopSettings.objects.create()

    if request.method == "POST":
        shop.name = request.POST.get("name", shop.name)
        shop.address = request.POST.get("address", shop.address)
        shop.phone = request.POST.get("phone", shop.phone)
        shop.email = request.POST.get("email", shop.email)
        shop.mechanic_name = request.POST.get("mechanic_name", shop.mechanic_name)
        shop.mechanic_credential = request.POST.get("mechanic_credential", shop.mechanic_credential)
        shop.save()
        messages.success(request, "Configuracoes salvas com sucesso!")
        return redirect("configuracoes")

    return render(request, "web/configuracoes.html", {"shop": shop})
