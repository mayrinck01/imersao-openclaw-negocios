#!/usr/bin/env python3
"""
Backfill dos relatórios mensais do Mogo que rodam no dia 5.

Gera arquivos locais sem enviar emails e depois pode ser sincronizado pelo
organizar_drive_mogo.py. Credenciais ficam apenas em memória.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt_module
import json
import os
import runpy
import subprocess
import sys
import time
import traceback
import zipfile
from pathlib import Path

ROOT = Path('/root/workspaces/cake-brain')
SCRIPTS_DIR = ROOT / 'automacoes' / 'scripts'
LOG_DIR = ROOT / 'relatorios' / 'Mogo' / 'exports'

# Relatórios ativos no cron mensal do dia 5.
# Saldo Crédito Carteira fica fora do backfill histórico: o Mogo não oferece filtro de data,
# então gerar meses passados seria apenas o saldo atual com nome antigo.
REPORT_SCRIPTS = [
    'mogo-faturamento-detalhado.py',
    'mogo-venda-nota-assinada.py',
    'mogo-ticket-medio.py',
    'mogo-vendas-analitico.py',
    'mogo-vendas-sintetico.py',
    'mogo-vendas-adicionais.py',
    'mogo-lucratividade-produto.py',
    'mogo-descontos-concedidos.py',
    'mogo-movimentacao-credito-cliente.py',
    'mogo-taxa-servico.py',
    'mogo-analise-cortesias.py',
    'mogo-lancamentos-pedidos.py',
    'mogo-historico-pagamento.py',
    'mogo-entradas-xml-detalhado.py',
    'mogo-compra-produtos.py',
    'mogo-variacao-preco-compra.py',
    'mogo-analise-quantidades-produzidas.py',
    'mogo-analise-insumos-producao.py',
    'mogo-analise-cadastro-clientes.py',
    'mogo-itens-vendidos-agendamento.py',
]

TARGET_MONTHS = [(2026, 1), (2026, 2)] + [(2025, m) for m in range(1, 13)]

OUTPUT_SPECS = {
    'mogo-faturamento-detalhado.py': ('Faturamento Detalhado', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-venda-nota-assinada.py': ('Venda em Nota Assinada', ['{yyyy}-{mm}-venda-nota-assinada.xlsx']),
    'mogo-ticket-medio.py': ('Ticket Medio', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-vendas-analitico.py': ('Vendas Analitico', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-vendas-sintetico.py': ('Vendas Sintetico', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-vendas-adicionais.py': ('Vendas Adicionais', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-lucratividade-produto.py': ('Lucratividade Produto', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-descontos-concedidos.py': ('Descontos Concedidos', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-movimentacao-credito-cliente.py': ('Movimentacao Credito Cliente', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-taxa-servico.py': ('Taxa Servico', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-analise-cortesias.py': ('Analise Cortesias', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-lancamentos-pedidos.py': ('Lancamentos Pedidos', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-historico-pagamento.py': ('Historico Pagamento', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-entradas-xml-detalhado.py': ('Entradas XML Detalhado', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-compra-produtos.py': ('Compra Produtos', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-variacao-preco-compra.py': ('Variacao Preco Compra', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-analise-quantidades-produzidas.py': ('Analise Quantidades Produzidas', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-analise-insumos-producao.py': ('Analise Insumos Producao', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-analise-cadastro-clientes.py': ('Analise Cadastro Clientes', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
    'mogo-itens-vendidos-agendamento.py': ('Itens Vendidos Agendamento', ['{mm}-{yyyy}.xlsx', '{mm}-{yyyy}.json']),
}

_real_datetime = dt_module.datetime
_current_fake_now = _real_datetime(2026, 5, 5, 12, 0, 0)

class FrozenDateTime(_real_datetime):
    @classmethod
    def now(cls, tz=None):
        value = _current_fake_now
        frozen = cls(value.year, value.month, value.day, value.hour, value.minute, value.second, value.microsecond)
        if tz is not None:
            return frozen.replace(tzinfo=tz)
        return frozen

    @classmethod
    def today(cls):
        return cls.now()


def fake_now_for_previous_month(year: int, month: int) -> dt_module.datetime:
    """Scripts geram mês anterior; então congelamos o relógio no dia 5 do mês seguinte."""
    if month == 12:
        return _real_datetime(year + 1, 1, 5, 12, 0, 0)
    return _real_datetime(year, month + 1, 5, 12, 0, 0)


def patch_datetime(fake_now: dt_module.datetime):
    global _current_fake_now
    _current_fake_now = fake_now
    dt_module.datetime = FrozenDateTime


def patch_email_send():
    """Impede disparo de email pelos scripts legados, preservando outros subprocess.run."""
    original_run = subprocess.run

    def safe_run(cmd, *args, **kwargs):
        text = ''
        if isinstance(cmd, (list, tuple)):
            text = ' '.join(map(str, cmd))
        else:
            text = str(cmd)
        if 'gog gmail send' in text:
            return subprocess.CompletedProcess(cmd, 0, stdout='message_id: backfill-email-suppressed\n', stderr='')
        return original_run(cmd, *args, **kwargs)

    subprocess.run = safe_run
    return original_run


def patch_mogo_login():
    """Cacheia credenciais em memória e renova sessão Mogo periodicamente."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    import mogo_login as login_mod  # noqa

    creds = login_mod._get_credentials()
    original_login = login_mod.mogo_login
    login_mod._get_credentials = lambda: creds

    state = {'session': None, 'uses': 0}

    def cached_login(verbose=True):
        # Backfill histórico é longo; sessão Mogo pode expirar/virar 401 no meio.
        # Renovar a cada relatório é mais lento, mas evita cascata de arquivos incompletos.
        state['session'] = original_login(verbose=verbose)
        state['uses'] = 1
        return state['session']

    login_mod.mogo_login = cached_login



def expected_paths(script_name: str, year: int, month: int) -> list[Path]:
    folder, patterns = OUTPUT_SPECS[script_name]
    values = {'yyyy': f'{year:04d}', 'mm': f'{month:02d}'}
    return [ROOT / 'relatorios' / 'Mogo' / folder / pattern.format(**values) for pattern in patterns]


def file_is_healthy(path: Path) -> bool:
    if not path.exists() or not path.is_file() or path.stat().st_size <= 0:
        return False
    if path.suffix.lower() == '.json':
        try:
            json.loads(path.read_text(encoding='utf-8'))
            return True
        except Exception:
            return False
    if path.suffix.lower() == '.xlsx':
        try:
            with zipfile.ZipFile(path) as zf:
                return zf.testzip() is None
        except Exception:
            return False
    return True


def already_downloaded(script_name: str, year: int, month: int) -> bool:
    return all(file_is_healthy(path) for path in expected_paths(script_name, year, month))


def run_one(script_name: str, year: int, month: int) -> dict:
    script_path = SCRIPTS_DIR / script_name
    started = time.time()
    old_argv = sys.argv[:]
    sys.argv = [str(script_path)]
    status = 'ok'
    error = ''
    try:
        runpy.run_path(str(script_path), run_name='__main__')
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 0
        if code not in (0, None):
            status = 'error'
            error = f'SystemExit({code})'
    except Exception as exc:
        status = 'error'
        error = f'{type(exc).__name__}: {exc}'
        traceback.print_exc()
    finally:
        sys.argv = old_argv
    return {
        'script': script_name,
        'year': year,
        'month': month,
        'status': status,
        'error': error,
        'duration_s': round(time.time() - started, 1),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--months', default='', help='Opcional: lista YYYY-MM separada por vírgula')
    parser.add_argument('--only-script', action='append', default=[], help='Rodar apenas script específico; pode repetir')
    parser.add_argument(
        '--confirm-backfill',
        action='store_true',
        help='Obrigatório para reprocessar meses fechados. Cron mensal normal nunca deve usar isso.'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Rebaixa mesmo quando os arquivos esperados já existem e passam validação.'
    )
    args = parser.parse_args()

    if not args.confirm_backfill:
        raise SystemExit('ABORTADO: backfill histórico exige --confirm-backfill explícito. Cron mensal normal não reprocessa meses fechados.')

    os.chdir(ROOT)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    result_path = LOG_DIR / f'mogo-backfill-dia5-{_real_datetime.now().strftime("%Y%m%d-%H%M%S")}.jsonl'

    months = TARGET_MONTHS
    if args.months:
        months = []
        for item in args.months.split(','):
            y, m = item.strip().split('-')
            months.append((int(y), int(m)))

    scripts = args.only_script or REPORT_SCRIPTS

    original_run = patch_email_send()
    patch_mogo_login()

    total = len(months) * len(scripts)
    done = 0
    errors = 0
    print(f'BACKFILL_START months={len(months)} scripts={len(scripts)} total={total} result={result_path}', flush=True)

    with result_path.open('w', encoding='utf-8') as out:
        for year, month in months:
            fake_now = fake_now_for_previous_month(year, month)
            patch_datetime(fake_now)
            print(f'\nMONTH_START {year}-{month:02d} fake_now={fake_now:%Y-%m-%d}', flush=True)
            for script_name in scripts:
                done += 1
                if not args.force and already_downloaded(script_name, year, month):
                    res = {
                        'script': script_name,
                        'year': year,
                        'month': month,
                        'status': 'skipped_existing',
                        'error': '',
                        'duration_s': 0.0,
                        'files': [str(path) for path in expected_paths(script_name, year, month)],
                    }
                    print(f'SKIP {done}/{total} {year}-{month:02d} {script_name} existing=healthy', flush=True)
                else:
                    print(f'RUN {done}/{total} {year}-{month:02d} {script_name}', flush=True)
                    res = run_one(script_name, year, month)
                if res['status'] not in ('ok', 'skipped_existing'):
                    errors += 1
                out.write(json.dumps(res, ensure_ascii=False) + '\n')
                out.flush()
                print(f'DONE {done}/{total} {year}-{month:02d} {script_name} status={res["status"]} duration={res["duration_s"]}s', flush=True)

    subprocess.run = original_run
    print(f'BACKFILL_DONE total={total} errors={errors} result={result_path}', flush=True)
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
