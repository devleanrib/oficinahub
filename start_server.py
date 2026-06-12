#!/usr/bin/env python3
"""
Sistema de Diagnostico Automotivo OBD-II
Executavel standalone - inicia servidor web automaticamente.
"""
import os
import sys
import webbrowser
import threading
import socket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")


def find_free_port(start=8000, end=9000):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return 8000


def main():
    import django
    django.setup()

    from django.core.management import call_command

    print("=" * 50)
    print("  SISTEMA DE DIAGNOSTICO AUTOMATIVO OBD-II")
    print("  Oficina Original")
    print("=" * 50)
    print()

    port = find_free_port()

    print(f"  Iniciando servidor na porta {port}...")
    print(f"  Acesse: http://127.0.0.1:{port}")
    print()
    print("  Para parar: Ctrl+C")
    print("=" * 50)
    print()

    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(f"http://127.0.0.1:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        call_command("runserver", f"0.0.0.0:{port}", "--noreload", "--verbosity", "1")
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        sys.exit(0)


if __name__ == "__main__":
    main()
