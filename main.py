import argparse
import logging
import sys
import os

from config import load_config, AppConfig
from ai_client import AIClient
from diagnostic_service import DiagnosticService
from report_generator import ReportGenerator
from models import InputData


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
        help="Nome do arquivo de saida (padrao: relatorio_<timestamp>.md)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Iniciar modo interativo",
    )
    return parser.parse_args()


def interactive_mode(config: AppConfig) -> None:
    print("\n" + "=" * 60)
    print("  SISTEMA DE DIAGNOSTICO AUTOMATIVO OBD-II")
    print("=" * 60)

    ai_client = AIClient(config)
    service = DiagnosticService(ai_client)
    reporter = ReportGenerator(config.output_dir)

    while True:
        print("\nModos de entrada:")
        print("  1 - Digitar codigos")
        print("  2 - Ler de arquivo")
        print("  3 - Sair")

        choice = input("\nSelecione uma opcao: ").strip()

        if choice == "3":
            print("Saindo...")
            break

        try:
            if choice == "1":
                codes_input = input("Digite os codigos separados por virgula: ").strip()
                if not codes_input:
                    print("Nenhum codigo informado.")
                    continue
                codes = [c.strip() for c in codes_input.split(",")]
                input_data = InputData.from_list(codes, "cli")

            elif choice == "2":
                filepath = input("Caminho do arquivo: ").strip()
                if not os.path.exists(filepath):
                    print(f"Arquivo nao encontrado: {filepath}")
                    continue
                input_data = InputData.from_file(filepath)

            else:
                print("Opcao invalida.")
                continue

            print(f"\nProcessando {len(input_data.codes)} codigo(s): {', '.join(input_data.codes)}")
            print("Consultando IA... Aguarde.")

            report = service.diagnose(input_data)
            content = reporter.generate(report)
            filepath = reporter.save(content, config.output_dir)

            print(f"\nRelatorio gerado com sucesso!")
            print(f"Arquivo: {filepath}")
            print(f"Criticidade geral: {report.overall_severity}")

        except ValueError as e:
            print(f"\nErro de validacao: {e}")
        except Exception as e:
            print(f"\nErro inesperado: {e}")
            logging.exception("Detalhes do erro")

    print("\nObrigado por usar o Sistema de Diagnostico!")


def cli_mode(args: argparse.Namespace, config: AppConfig) -> None:
    ai_client = AIClient(config)
    service = DiagnosticService(ai_client)
    reporter = ReportGenerator(config.output_dir)

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
        content = reporter.generate(report)
        filepath = reporter.save(content, args.output)

        print(f"\nRelatorio gerado com sucesso!")
        print(f"Arquivo: {filepath}")
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