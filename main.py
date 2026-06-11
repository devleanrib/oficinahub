import argparse
import logging
import sys
import os

from config import load_config, AppConfig
from ai_client import AIClient
from diagnostic_service import DiagnosticService
from report_generator import ReportGenerator
from pdf_generator import PDFGenerator
from models import InputData, VehicleInfo


def setup_logging(level: str = "DEBUG") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.DEBUG),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sistema de Diagnostico Automotivo por Codigos OBD-II",
        epilog="Se nenhum argumento for fornecido, o modo interativo sera iniciado.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--codes",
        type=str,
        help="Lista de codigos separados por virgula (ex: P0300,P0171,U0100)",
    )
    group.add_argument(
        "--file",
        type=str,
        help="Caminho para arquivo de entrada (.json ou .txt)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Nome do arquivo de saida (padrao: laudo_<timestamp>)",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Gerar apenas HTML (sem PDF)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Iniciar modo interativo",
    )
    return parser.parse_args()


def collect_vehicle_interactive() -> VehicleInfo:
    print("\nInforme os dados do veiculo.\n")

    brand = input("Marca: ").strip()
    model = input("Modelo: ").strip()
    year = input("Ano: ").strip()
    engine = input("Motorizacao: ").strip()
    fuel = input("Combustivel: ").strip()
    transmission = input("Transmissao: ").strip()

    mileage_str = input("Quilometragem: ").strip()
    mileage = int(mileage_str) if mileage_str.isdigit() else None

    plate = input("Placa (opcional): ").strip()

    return VehicleInfo(
        brand=brand,
        model=model,
        year=year,
        engine=engine,
        fuel=fuel,
        transmission=transmission,
        mileage=mileage,
        plate=plate,
    )


def show_vehicle_summary(vehicle: VehicleInfo) -> None:
    print("\n" + "=" * 50)
    print("  DADOS DO VEICULO")
    print("=" * 50)
    if vehicle.brand:
        print(f"  Marca:         {vehicle.brand}")
    if vehicle.model:
        print(f"  Modelo:        {vehicle.model}")
    if vehicle.year:
        print(f"  Ano:           {vehicle.year}")
    if vehicle.engine:
        print(f"  Motor:         {vehicle.engine}")
    if vehicle.fuel:
        print(f"  Combustivel:   {vehicle.fuel}")
    if vehicle.transmission:
        print(f"  Transmissao:   {vehicle.transmission}")
    if vehicle.mileage is not None:
        print(f"  Quilometragem: {vehicle.mileage:,}".replace(",", ".") + " km")
    if vehicle.plate:
        print(f"  Placa:         {vehicle.plate}")
    print("=" * 50)


def confirm_vehicle() -> bool:
    while True:
        print("\nOs dados estao corretos?")
        print("  1 - Sim")
        print("  2 - Corrigir")
        choice = input("\nSelecione: ").strip()
        if choice == "1":
            return True
        if choice == "2":
            return False
        print("Opcao invalida.")


def collect_codes_interactive() -> list[str]:
    print("\nInforme os codigos encontrados.")
    print("Digite separados por virgula.")
    print("Exemplo: P0300,P0171,U0100")
    codes_input = input("\nCodigos: ").strip()
    if not codes_input:
        return []
    return [c.strip().upper() for c in codes_input.split(",")]


def show_final_summary(vehicle: VehicleInfo, codes: list[str]) -> None:
    print("\n" + "=" * 50)
    print("  RESUMO DO DIAGNOSTICO")
    print("=" * 50)

    print("\n  VEICULO:")
    vehicle_parts = []
    if vehicle.brand:
        vehicle_parts.append(vehicle.brand)
    if vehicle.model:
        vehicle_parts.append(vehicle.model)
    if vehicle.year:
        vehicle_parts.append(vehicle.year)
    if vehicle_parts:
        print(f"    {' '.join(vehicle_parts)}")
    else:
        print("    Nao informado")

    print(f"\n  CODIGOS ({len(codes)}):")
    for code in codes:
        print(f"    {code}")

    print("\n" + "=" * 50)


def confirm_diagnosis() -> bool:
    while True:
        print("\nConfirmar geracao do diagnostico?")
        print("  1 - Gerar")
        print("  2 - Cancelar")
        choice = input("\nSelecione: ").strip()
        if choice == "1":
            return True
        if choice == "2":
            return False
        print("Opcao invalida.")


def interactive_mode(config: AppConfig) -> None:
    print("\n" + "=" * 60)
    print("  SISTEMA DE DIAGNOSTICO AUTOMATIVO OBD-II")
    print("=" * 60)

    ai_client = AIClient(config)
    service = DiagnosticService(ai_client)
    reporter = ReportGenerator()
    pdf_gen = PDFGenerator(output_dir=config.output_dir)

    while True:
        vehicle = collect_vehicle_interactive()
        show_vehicle_summary(vehicle)

        if not confirm_vehicle():
            continue

        codes = collect_codes_interactive()
        if not codes:
            print("\nNenhum codigo informado.")
            continue

        try:
            input_data = InputData.from_list(codes, "interactive", vehicle)
        except ValueError as e:
            print(f"\nErro de validacao: {e}")
            continue

        show_final_summary(vehicle, input_data.codes)

        if not confirm_diagnosis():
            continue

        print(f"\nProcessando {len(input_data.codes)} codigo(s): {', '.join(input_data.codes)}")
        print("Consultando IA... Aguarde.")

        try:
            report = service.diagnose(input_data)
            context = reporter.prepare_context(report, input_data.vehicle)
            results = pdf_gen.generate(context)

            print(f"\nLaudo gerado com sucesso!")
            if "html_path" in results:
                print(f"HTML: {results['html_path']}")
            if "pdf_path" in results:
                print(f"PDF: {results['pdf_path']}")
            print(f"Criticidade geral: {report.overall_severity}")

        except ValueError as e:
            print(f"\nErro de validacao: {e}")
        except Exception as e:
            print(f"\nErro inesperado: {e}")
            logging.exception("Detalhes do erro")

        print("\nDeseja realizar um novo diagnostico?")
        print("  1 - Sim")
        print("  2 - Sair")
        if input("\nSelecione: ").strip() != "1":
            break

    print("\nObrigado por usar o Sistema de Diagnostico!")


def cli_mode(args: argparse.Namespace, config: AppConfig) -> None:
    ai_client = AIClient(config)
    service = DiagnosticService(ai_client)
    reporter = ReportGenerator()
    pdf_gen = PDFGenerator(output_dir=config.output_dir)

    try:
        if args.codes:
            codes = [c.strip() for c in args.codes.split(",")]
            input_data = InputData.from_list(codes, "cli")
        elif args.file:
            if not os.path.exists(args.file):
                print(f"Arquivo nao encontrado: {args.file}")
                sys.exit(1)
            input_data = InputData.from_file(args.file)
        else:
            print("Nenhuma entrada especificada. Use --help para ver as opcoes.")
            sys.exit(1)

        print(f"Processando {len(input_data.codes)} codigo(s): {', '.join(input_data.codes)}")
        print("Consultando IA... Aguarde.")

        report = service.diagnose(input_data)
        context = reporter.prepare_context(report, input_data.vehicle)
        results = pdf_gen.generate(context, save_html=True, save_pdf=not args.html_only)

        print(f"\nLaudo gerado com sucesso!")
        if "html_path" in results:
            print(f"HTML: {results['html_path']}")
        if "pdf_path" in results:
            print(f"PDF: {results['pdf_path']}")
        print(f"Criticidade geral: {report.overall_severity}")

    except ValueError as e:
        print(f"Erro de validacao: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Erro de execucao: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        logging.exception("Detalhes do erro")
        sys.exit(1)


def main() -> None:
    args = parse_args()

    try:
        config = load_config()
    except ValueError as e:
        print(f"Erro de configuracao: {e}")
        print("Configure a variavel de ambiente OPENAI_API_KEY ou crie um arquivo .env")
        sys.exit(1)

    setup_logging(config.log_level)
    logger = logging.getLogger(__name__)
    logger.info("Sistema iniciado. Modelo: %s", config.openai_model)

    if args.interactive or (not args.codes and not args.file):
        interactive_mode(config)
    else:
        cli_mode(args, config)


if __name__ == "__main__":
    main()
