from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import re


@dataclass
class VehicleInfo:
    brand: str = ""
    model: str = ""
    year: str = ""
    engine: str = ""
    fuel: str = ""
    transmission: str = ""
    mileage: Optional[int] = None
    plate: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "VehicleInfo":
        if not data:
            return cls()
        return cls(
            brand=data.get("brand", ""),
            model=data.get("model", ""),
            year=data.get("year", ""),
            engine=data.get("engine", ""),
            fuel=data.get("fuel", ""),
            transmission=data.get("transmission", ""),
            mileage=data.get("mileage"),
            plate=data.get("plate", ""),
        )

    def to_context_string(self) -> str:
        parts = []
        if self.brand:
            parts.append(f"Marca: {self.brand}")
        if self.model:
            parts.append(f"Modelo: {self.model}")
        if self.year:
            parts.append(f"Ano: {self.year}")
        if self.engine:
            parts.append(f"Motorizacao: {self.engine}")
        if self.fuel:
            parts.append(f"Combustivel: {self.fuel}")
        if self.transmission:
            parts.append(f"Transmissao: {self.transmission}")
        if self.mileage is not None:
            parts.append(f"Quilometragem: {self.mileage} km")
        return "\n".join(parts) if parts else ""

    def has_info(self) -> bool:
        return any([self.brand, self.model, self.year, self.engine, self.fuel, self.transmission, self.mileage])


@dataclass
class DiagnosticResult:
    code: str
    meaning: str
    description: str
    causes: list[str]
    risks: list[str]
    severity: str
    recommendations: list[str]
    can_operate: bool

    def __post_init__(self):
        self.code = self.code.upper().strip()
        self.severity = self.severity.capitalize()

    @classmethod
    def from_dict(cls, data: dict, code: str) -> "DiagnosticResult":
        return cls(
            code=code,
            meaning=data.get("meaning", ""),
            description=data.get("description", ""),
            causes=data.get("causes", []),
            risks=data.get("risks", []),
            severity=data.get("severity", "Media"),
            recommendations=data.get("recommendations", []),
            can_operate=data.get("can_operate", True),
        )


@dataclass
class DiagnosticReport:
    generated_at: str
    total_codes: int
    overall_severity: str
    results: list[DiagnosticResult]
    summary: str
    conclusion: str

    @classmethod
    def create(cls, results: list[DiagnosticResult], summary: str, conclusion: str) -> "DiagnosticReport":
        overall_severity = cls._calculate_overall_severity(results)
        return cls(
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_codes=len(results),
            overall_severity=overall_severity,
            results=results,
            summary=summary,
            conclusion=conclusion,
        )

    @staticmethod
    def _calculate_overall_severity(results: list[DiagnosticResult]) -> str:
        if not results:
            return "Baixa"
        severity_order = {"Critica": 4, "Alta": 3, "Media": 2, "Baixa": 1}
        max_severity = max(results, key=lambda r: severity_order.get(r.severity, 0))
        return max_severity.severity


@dataclass
class InputData:
    codes: list[str]
    source: str
    vehicle: VehicleInfo = field(default_factory=VehicleInfo)

    @classmethod
    def from_list(cls, codes: list[str], source: str = "direct", vehicle: VehicleInfo | None = None) -> "InputData":
        normalized = cls._normalize_codes(codes)
        return cls(codes=normalized, source=source, vehicle=vehicle or VehicleInfo())

    @classmethod
    def from_file(cls, filepath: str) -> "InputData":
        import json
        ext = filepath.lower().split(".")[-1]
        if ext == "json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            codes = data.get("codes", [])
            vehicle_data = data.get("vehicle", {})
            vehicle = VehicleInfo.from_dict(vehicle_data) if vehicle_data else VehicleInfo()
        elif ext == "txt":
            with open(filepath, "r", encoding="utf-8") as f:
                codes = [line.strip() for line in f if line.strip()]
            vehicle = VehicleInfo()
        else:
            raise ValueError(f"Formato nao suportado: {ext}. Use .json ou .txt")
        return cls.from_list(codes, ext, vehicle)

    @staticmethod
    def _normalize_codes(codes: list[str]) -> list[str]:
        seen = set()
        normalized = []
        pattern = re.compile(r"^[PCBU]\d{4}$", re.IGNORECASE)
        for code in codes:
            code = code.upper().strip()
            if not pattern.match(code):
                raise ValueError(f"Codigo invalido: {code}. Formato esperado: P0300, C0035, B0020, U0100")
            if code not in seen:
                seen.add(code)
                normalized.append(code)
        return normalized