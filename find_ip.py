#!/usr/bin/env python3
"""
Script para auxiliarconexao do celular ao servidor.
Execute: python find_ip.py
"""
import socket
import subprocess
import sys


def get_windows_ip():
    try:
        result = subprocess.run(
            ["ip", "route"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if "default" in line:
                parts = line.split()
                idx = parts.index("via")
                return parts[idx + 1]
    except Exception:
        pass
    return None


def get_all_ips():
    ips = []
    try:
        result = subprocess.run(
            ["hostname", "-I"],
            capture_output=True, text=True, timeout=5
        )
        ips = result.stdout.strip().split()
    except Exception:
        pass
    return ips


def main():
    print("=" * 55)
    print("  COMO ACESSAR DO CELULAR (iPhone/Android)")
    print("=" * 55)
    print()

    windows_ip = get_windows_ip()
    all_ips = get_all_ips()

    print("  PASSO 1: Descubra o IP da sua maquina Windows")
    print("  - Abra o Prompt de Comando (cmd) no Windows")
    print("  - Digite: ipconfig")
    print("  - Procure 'IPv4' na placa de rede Wi-Fi ou Ethernet")
    print()

    if windows_ip:
        print(f"  IP detectado (gateway WSL): {windows_ip}")
    print()

    print("  PASSO 2: No celular, abra o navegador e digite:")
    print()
    if windows_ip:
        print(f"    http://{windows_ip}:8000")
    print()
    print("  IMPORTANTE:")
    print("  - Celular e computador devem estar na MESMA rede Wi-Fi")
    print("  - Se nao funcionar, tente os IPs abaixo:")
    for ip in all_ips:
        if ip != windows_ip:
            print(f"    http://{ip}:8000")
    print()
    print("  PASSO 3 (iPhone - adicionar como app):")
    print("  - Abra Safari e acesse o endereco acima")
    print("  - Toque no icone de compartilhar (quadrado com seta)")
    print("  - Selecione 'Adicionar a Tela de Inicio'")
    print("  - Pronto! O app aparece como um aplicativo nativo")
    print()
    print("=" * 55)


if __name__ == "__main__":
    main()
