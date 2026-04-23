#!/usr/bin/env python3
"""
Resumo diário de vendas via Link de Pagamento Rede (Userede)
Envia email para mayrinck01@gmail.com e adm@cakeco.com.br
"""
import subprocess, re, sys
from datetime import datetime, timedelta
from filter_pt import pt_text
from audit_pt import audit_text

def buscar_emails_rede(data_str):
    """Busca emails da Rede para uma data específica (formato: YYYY/MM/DD)"""
    data_obj = datetime.strptime(data_str, "%Y/%m/%d")
    data_next = data_obj + timedelta(days=1)
    
    result = subprocess.run(
        ['bash', '-c', f'GOG_KEYRING_PASSWORD="" gog gmail search "from:rede@userede.com.br after:{data_str} before:{data_next.strftime("%Y/%m/%d")}" --max 100 --account joao@cakeco.com.br'],
        capture_output=True, text=True
    )
    
    threads = []
    for line in result.stdout.split('\n'):
        match = re.search(r'(19[a-f0-9]{15})\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', line)
        if match:
            threads.append({'id': match.group(1), 'date': match.group(2)})
    return threads

def ler_email(thread_id):
    """Lê conteúdo de um email"""
    result = subprocess.run(
        ['bash', '-c', f'GOG_KEYRING_PASSWORD="" gog gmail thread {thread_id} --account joao@cakeco.com.br'],
        capture_output=True, text=True
    )
    return result.stdout

def parse_email(conteudo, hora):
    """Extrai dados relevantes do email da Rede"""
    dados = {'hora': hora}
    
    # Status
    if 'cancelado' in conteudo.lower() or 'cancelamento' in conteudo.lower():
        dados['status'] = 'CANCELADO'
    elif 'pagamento aprovado' in conteudo.lower():
        dados['status'] = 'APROVADO'
    else:
        dados['status'] = 'DESCONHECIDO'
    
    # Identificação
    match = re.search(r'Identificação do pedido:\s*\n(.+)', conteudo)
    dados['identificacao'] = match.group(1).strip() if match else '—'
    
    # Valor
    match = re.search(r'Valor do link:\s*\n(R\$\s*[\d.,]+)', conteudo)
    dados['valor_str'] = match.group(1).strip() if match else 'R$ 0,00'
    
    # Valor numérico
    val = re.search(r'R\$\s*([\d.,]+)', dados['valor_str'])
    if val:
        dados['valor'] = float(val.group(1).replace('.', '').replace(',', '.'))
    else:
        dados['valor'] = 0.0
    
    # Data
    match = re.search(r'Pago em:\s*\n(.+)', conteudo)
    dados['pago_em'] = match.group(1).strip() if match else '—'
    
    return dados

def montar_email(data_formatada, aprovados, cancelados):
    """Monta o corpo do email"""
    
    total_aprovado = sum(p['valor'] for p in aprovados)
    total_cancelado = sum(p['valor'] for p in cancelados)
    
    corpo = f"📦 RESUMO DE VENDAS — LINK DE PAGAMENTO REDE\n"
    corpo += f"Data: {data_formatada}\n"
    corpo += "=" * 55 + "\n\n"
    
    # Aprovados
    corpo += f"✅ PAGAMENTOS APROVADOS ({len(aprovados)})\n"
    corpo += "-" * 55 + "\n"
    
    if aprovados:
        corpo += f"{'Hora':<8} {'Identificação do Pedido':<28} {'Valor':>10}\n"
        corpo += "-" * 55 + "\n"
        for p in sorted(aprovados, key=lambda x: x['hora']):
            hora = p['hora'][11:16] if len(p['hora']) > 11 else p['hora']
            corpo += f"{hora:<8} {p['identificacao']:<28} {p['valor_str']:>10}\n"
        corpo += "-" * 55 + "\n"
        corpo += f"{'TOTAL APROVADO':<37} R$ {total_aprovado:>8.2f}\n".replace('.', ',')
    else:
        corpo += "Nenhum pagamento aprovado nesta data.\n"
    
    # Cancelados
    if cancelados:
        corpo += f"\n❌ CANCELAMENTOS ({len(cancelados)})\n"
        corpo += "-" * 55 + "\n"
        corpo += f"{'Hora':<8} {'Identificação do Pedido':<28} {'Valor':>10}\n"
        corpo += "-" * 55 + "\n"
        for p in sorted(cancelados, key=lambda x: x['hora']):
            hora = p['hora'][11:16] if len(p['hora']) > 11 else p['hora']
            corpo += f"{hora:<8} {p['identificacao']:<28} {p['valor_str']:>10}\n"
        corpo += "-" * 55 + "\n"
        corpo += f"{'TOTAL CANCELADO':<37} R$ {total_cancelado:>8.2f}\n".replace('.', ',')
    
    corpo += "\n" + "=" * 55 + "\n"
    corpo += f"LÍQUIDO DO DIA: R$ {(total_aprovado - total_cancelado):>8.2f}\n".replace('.', ',')
    corpo += "=" * 55 + "\n\n"
    corpo += "--\nEnviado automaticamente pelo BigDog 🐕\nCake & Co"
    
    return pt_text(corpo)

def enviar_resumo(data_str):
    """Busca emails, processa e envia resumo"""
    data_obj = datetime.strptime(data_str, "%Y/%m/%d")
    data_formatada = data_obj.strftime("%d/%m/%Y")
    
    print(f"\n📅 Processando {data_formatada}...")
    
    threads = buscar_emails_rede(data_str)
    print(f"   {len(threads)} email(s) encontrado(s)")
    
    if not threads:
        print(f"   Nenhum email da Rede em {data_formatada} — pulando")
        return False
    
    aprovados = []
    cancelados = []
    
    for t in threads:
        conteudo = ler_email(t['id'])
        dados = parse_email(conteudo, t['date'])
        if dados['status'] == 'CANCELADO':
            cancelados.append(dados)
        else:
            aprovados.append(dados)
    
    corpo = montar_email(data_formatada, aprovados, cancelados)
    findings = audit_text(corpo)
    if findings:
        print(f"⚠️ Auditoria PT encontrou {len(findings)} ocorrência(s) suspeita(s) no resumo.")
        for f in findings[:10]:
            print(f"  - linha {f['line']}: {', '.join(f['hits'])}")
        return False
    print(corpo)
    
    # Salvar HTML em arquivo temp para envio
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(corpo)
        html_path = f.name

    # Enviar email
    result = subprocess.run(
        ['bash', '-c', f'''GOG_KEYRING_PASSWORD="" gog gmail send \
  --account cakebigdog@gmail.com \
  --client cakebigdog \
  --to mayrinck01@gmail.com \
  --cc adm@cakeco.com.br \
  --subject "{pt_text(f'Resumo Vendas Link Rede — {data_formatada}')}" \
  --body-html "$(cat {html_path})"'''],
        capture_output=True, text=True
    )
    import os; os.unlink(html_path)
    
    if 'message_id' in result.stdout:
        print(f"   ✅ Email enviado!")
        return True
    else:
        print(f"   ❌ Erro: {result.stderr[:100]}")
        return False

if __name__ == "__main__":
    # Se receber data como argumento usa ela, senão usa ontem
    if len(sys.argv) > 1:
        data = sys.argv[1]  # formato: YYYY/MM/DD
    else:
        ontem = datetime.now() - timedelta(days=1)
        data = ontem.strftime("%Y/%m/%d")
    
    enviar_resumo(data)
