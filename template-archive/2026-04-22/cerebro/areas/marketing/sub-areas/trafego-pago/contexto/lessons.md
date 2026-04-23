# Lições Aprendidas — Tráfego Pago

> Learnings de campanhas e criativos.

---

## Março 2026

### Não criar arquivos sem checar o remote primeiro
- **Contexto:** Durante sessão 2026-03-26, foi criado um HTML localmente. Cayo pediu pull do remote — o arquivo correto já estava no repositório. O local foi descartado.
- **Lição:** Sempre fazer `git pull` antes de criar qualquer arquivo que possa vir do remote. Verificar se o arquivo já existe antes de gerar.
- **Ação:** Checklist de pré-criação: verificar remote antes de criar qualquer artefato de relatório.

### Canvas requer node pareado — fallback obrigatório
- **Contexto:** Tentativa de usar canvas para renderizar HTML sem node pareado na sessão.
- **Lição:** Canvas só funciona com node pareado. Sem ele, opções de fallback: screenshot via browser headless ou envio como documento pelo Telegram.
- **Ação:** Verificar disponibilidade de node antes de usar canvas em qualquer rotina.

### Telegram não renderiza HTML inline
- **Contexto:** Tentativa de enviar relatório HTML via Telegram.
- **Lição:** Telegram não renderiza HTML inline. Opções: canvas (node), screenshot (browser headless), ou envio como arquivo para download.
- **Ação:** Relatórios HTML → converter para screenshot ou enviar como arquivo .html para download.

### Ferramenta `message` com `filePath` exige campo `buttons`
- **Contexto:** Tentativa de enviar HTML como documento com `message` + `filePath`.
- **Lição:** Validação falhou — campo `buttons` é obrigatório mesmo para envio de arquivo.
- **Ação:** Sempre incluir `buttons: []` ao usar `message` com `filePath`.

---

_Atualizado: março 2026_
