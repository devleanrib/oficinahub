import json
import logging
from typing import List

from ai_client import AIClient
from models import DiagnosticResult, DiagnosticReport, InputData, VehicleInfo
from prompts import DIAGNOSIS_PROMPT, VEHICLE_CONTEXT_TEMPLATE

logger = logging.getLogger(__name__)


class DiagnosticService:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    def diagnose(self, input_data: InputData) -> DiagnosticReport:
        logger.info("Iniciando diagnostico para %d codigos: %s", len(input_data.codes), input_data.codes)
        results = []

        for code in input_data.codes:
            logger.debug("Processando codigo: %s", code)
            result = self.diagnose_single(code, input_data.vehicle)
            results.append(result)

        summary = self._generate_summary(results)
        conclusion = self._generate_conclusion(results)

        report = DiagnosticReport.create(results, summary, conclusion)
        logger.info("Diagnostico concluido. Criticidade geral: %s", report.overall_severity)
        return report

    def diagnose_single(self, code: str, vehicle: VehicleInfo | None = None) -> DiagnosticResult:
        vehicle_context = self._build_vehicle_context(vehicle)
        prompt = DIAGNOSIS_PROMPT.format(code=code, vehicle_context=vehicle_context)
        response = self.ai_client.generate(prompt)
        data = self._parse_ai_response(response, code)
        return DiagnosticResult.from_dict(data, code)

    def _build_vehicle_context(self, vehicle: VehicleInfo | None) -> str:
        if not vehicle or not vehicle.has_info():
            return ""
        return VEHICLE_CONTEXT_TEMPLATE.format(
            brand=vehicle.brand or "Nao informado",
            model=vehicle.model or "Nao informado",
            year=vehicle.year or "Nao informado",
            engine=vehicle.engine or "Nao informado",
            fuel=vehicle.fuel or "Nao informado",
            transmission=vehicle.transmission or "Nao informado",
            mileage=vehicle.mileage if vehicle.mileage is not None else "Nao informado",
        )

    def _parse_ai_response(self, response: str, code: str) -> dict:
        try:
            data = json.loads(response)
            logger.debug("Resposta parseada com sucesso para %s", code)
        except json.JSONDecodeError as e:
            logger.error("Falha ao parsear JSON para %s: %s", code, e)
            logger.debug("Resposta bruta: %s", response[:500])
            raise ValueError(f"Resposta da IA nao e JSON valido para {code}") from e

        required_fields = [
            "meaning", "description", "causes", "risks",
            "severity", "recommendations", "can_operate"
        ]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Campo obrigatorio ausente na resposta para {code}: {field}")

        if not isinstance(data["causes"], list):
            data["causes"] = [str(data["causes"])]
        if not isinstance(data["risks"], list):
            data["risks"] = [str(data["risks"])]
        if not isinstance(data["recommendations"], list):
            data["recommendations"] = [str(data["recommendations"])]

        valid_severities = {"Baixa", "Media", "Alta", "Critica"}
        if data["severity"] not in valid_severities:
            logger.warning("Criticidade invalida '%s' para %s, usando 'Media'", data["severity"], code)
            data["severity"] = "Media"

        if not isinstance(data["can_operate"], bool):
            data["can_operate"] = str(data["can_operate"]).lower() in ("true", "1", "sim", "yes")

        return data

    def _generate_summary(self, results: List[DiagnosticResult]) -> str:
        if not results:
            return "Nenhum codigo de falha analisado."

        severity_counts = {}
        for r in results:
            severity_counts[r.severity] = severity_counts.get(r.severity, 0) + 1

        parts = [f"Foram analisados {len(results)} codigo(s) de falha OBD-II."]
        for sev in ["Critica", "Alta", "Media", "Baixa"]:
            if sev in severity_counts:
                parts.append(f"{severity_counts[sev]} codigo(s) com criticidade {sev.lower()}.")

        cannot_operate = [r.code for r in results if not r.can_operate]
        if cannot_operate:
            parts.append(f"ATENCAO: Veiculo NAO deve operar - codigos: {', '.join(cannot_operate)}")
        else:
            parts.append("Veiculo pode continuar em operacao com monitoramento.")

        return " ".join(parts)

    def _generate_conclusion(self, results: List[DiagnosticResult]) -> str:
        if not results:
            return "Nenhuma acao necessaria."

        critical = [r for r in results if r.severity == "Critica"]
        high = [r for r in results if r.severity == "Alta"]

        if critical:
            codes = ", ".join(r.code for r in critical)
            return (
                f"ACAO IMEDIATA NECESSARIA: {len(critical)} codigo(s) critico(s) detectado(s) ({codes}). "
                "O veiculo apresenta risco de dano severo ou perigo a seguranca. "
                "Procure uma oficina especializada imediatamente."
            )

        if high:
            codes = ", ".join(r.code for r in high)
            return (
                f"ATENCAO REQUERIDA: {len(high)} codigo(s) de alta criticidade ({codes}). "
                "Agende diagnostico completo o mais breve possivel para evitar agravamento."
            )

        if any(r.severity == "Media" for r in results):
            return (
                "Codigos de criticidade media detectados. Recomenda-se agendar manutencao preventiva "
                "nos proximos dias para evitar piora do quadro."
            )

        return "Codigos de baixa criticidade. Monitore o veiculo e realize manutencao na proxima revisao programada."