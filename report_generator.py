import os
import logging
from datetime import datetime

from models import DiagnosticReport, DiagnosticResult

logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.debug("ReportGenerator inicializado. Diretorio de saida: %s", output_dir)

    def generate(self, report: DiagnosticReport) -> str:
        sections = [
            self._header(report),
            self._summary(report),
            self._separator(),
        ]

        for result in report.results:
            sections.append(self._code_section(result))
            sections.append(self._separator())

        sections.append(self._conclusion(report))

        content = "\n".join(sections)
        logger.info("Relatorio gerado com sucesso (%d caracteres)", len(content))
        return content

    def save(self, content: str, filename: str | None = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_diagnostico_{timestamp}.md"

        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("Relatorio salvo em: %s", filepath)
        return filepath

    def _header(self, report: DiagnosticReport) -> str:
        return f"""# Relatório de Diagnóstico Automotivo

**Data/Hora de Geração:** {report.generated_at}

**Quantidade de Códigos Analisados:** {report.total_codes}

**Criticidade Geral:** {report.overall_severity}"""

    def _summary(self, report: DiagnosticReport) -> str:
        return f"""## Resumo Executivo

{report.summary}"""

    def _separator(self) -> str:
        return "---"

    def _code_section(self, result: DiagnosticResult) -> str:
        sections = [
            f"## Código {result.code}",
            self._field_section("Significado", result.meaning),
            self._field_section("Descrição Técnica", result.description),
            self._list_section("Possíveis Causas", result.causes),
            self._list_section("Sintomas", result.symptoms),
            self._list_section("Impactos", result.impacts),
            self._severity_section(result.severity),
            self._list_section("Recomendações", result.recommendations),
            self._list_section("Ações Corretivas", result.corrective_actions),
            self._operation_section(result.can_operate),
        ]
        return "\n\n".join(sections)

    def _field_section(self, title: str, content: str) -> str:
        return f"### {title}\n\n{content}"

    def _list_section(self, title: str, items: list[str]) -> str:
        if not items:
            return f"### {title}\n\nNão especificado."
        bullets = "\n".join(f"- {item}" for item in items)
        return f"### {title}\n\n{bullets}"

    def _severity_section(self, severity: str) -> str:
        emoji = self._get_severity_emoji(severity)
        return f"### Criticidade\n\n{emoji} **{severity}**"

    def _operation_section(self, can_operate: bool) -> str:
        if can_operate:
            status = "✅ O veículo pode continuar em operação"
            detail = "Monitore os sintomas e realize as recomendações o mais breve possível."
        else:
            status = "🚫 O veículo NÃO deve ser operado"
            detail = "Existe risco de dano ao veículo ou perigo a segurança. Procure assistência imediatamente."
        return f"### Operacionalidade\n\n{status}\n\n{detail}"

    def _get_severity_emoji(self, severity: str) -> str:
        mapping = {
            "Critica": "🔴",
            "Alta": "🟠",
            "Media": "🟡",
            "Baixa": "🟢",
        }
        return mapping.get(severity, "⚪")

    def _conclusion(self, report: DiagnosticReport) -> str:
        return f"""## Conclusão

{report.conclusion}

---

*Relatório gerado automaticamente pelo Sistema de Diagnóstico Automotivo OBD-II*
*Data: {report.generated_at}*"""