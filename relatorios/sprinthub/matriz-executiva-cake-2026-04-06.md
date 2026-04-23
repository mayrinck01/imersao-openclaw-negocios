# Matriz Executiva Cake — SprintHub
**Data:** 06/04/2026  
**Elaborado por:** BigDog

## Objetivo
Transformar o SprintHub em máquina de relacionamento, venda e inteligência operacional.

---

## 1. O que implementar primeiro

### Prioridade 1 — Base e segmentação
**1) Arrumar e enriquecer a base de leads**

**Objetivo:**
Parar de ter 15 mil contatos “mortos” e começar a ter uma base utilizável.

**Implementar:**
- padronizar campos principais
- criar/validar custom fields:
  - `data_ultimo_contato`
  - `aniversario`
  - `cpf`
  - `origem_compra`
  - `ticket_acumulado` *(opcional depois)*
- normalizar tags principais:
  - `cadastrado`
  - `cliente_ativo`
  - `cliente_inativo`
  - `aniversario_mes`
  - `super_cliente`
  - `pos_venda`
  - `problema_atendimento`

**Valor:**
- segmentação real
- campanhas melhores
- reativação possível
- CRM menos cego

---

### Prioridade 2 — Pós-venda e reativação
**2) Criar fluxo de pós-venda semanal**

**Objetivo:**
Parar de depender só da compra espontânea.

**Implementar:**
- campanha para quem comprou recentemente
- mensagem de relacionamento
- novidade/produto da semana
- CTA simples de recompra

**Valor:**
- aumento de recorrência
- melhora de LTV
- aproveitamento da base atual

**Leitura do BigDog:**
Esse é um dos fluxos com melhor relação esforço/retorno.

---

### Prioridade 3 — Atendimento inteligente
**3) Chatbot IA com fallback humano**

**Objetivo:**
Reduzir carga operacional no pico sem ferrar experiência.

**Implementar:**
- menu inicial
- respostas para dúvidas frequentes
- saída rápida para humano
- regra de horário
- transferência inteligente

**Valor:**
- menos carga no SAC
- mais velocidade de resposta
- redução de dependência dos atendentes mais fortes

**Alerta:**
IA boa com escape humano = ótimo. Robô travando cliente = desastre.

---

### Prioridade 4 — Medição de atendimento
**4) Dashboard de SAC 360**

**Objetivo:**
Parar de operar atendimento no feeling.

**Medir:**
- volume por atendente
- tempo médio
- canal
- horário de pico
- taxa de retorno
- volume por período
- atendimentos sem resposta / com atraso

**Valor:**
- gestão de equipe
- escala
- treinamento
- alocação por horário

---

### Prioridade 5 — CRM de encomendas/eventos
**5) Funil comercial para encomendas, corporativo e eventos**

**Objetivo:**
Não deixar orçamento se perder no WhatsApp.

**Implementar:**
- lead entra
- vira oportunidade
- passa por etapas
- responsável definido
- valor potencial registrado
- follow-up controlado

**Valor:**
- menos perda de oportunidade
- previsibilidade comercial
- visão do pipeline

**Leitura do BigDog:**
Isso pode virar ouro se a Cake crescer mais em corporativo, festas, encomendas maiores e B2B.

---

## 2. O que gera mais retorno rápido

### Top 4
1. **Reativação da base** — já existe base grande
2. **Pós-venda** — cliente que já comprou é mais barato de trazer de volta
3. **Cadastro/recadastro** — melhora segmentação, campanha, CRM e relacionamento
4. **Chatbot IA nas dúvidas frequentes** — reduz custo operacional nos horários de pico

---

## 3. O que colocar em produção já

### Fase 1 — imediato
1. Campo `data_ultimo_contato`
2. Fluxo automático de atualização desse campo
3. Tag `cadastrado`
4. Chatbot de cadastro/recadastro
5. Campanha de pós-venda simples
6. Relatório operacional de SAC semanal

---

## 4. Dashboard que vale montar primeiro

### Dashboard Executivo de Relacionamento

**Base**
- total de leads
- novos leads por semana/mês
- leads com telefone
- leads com aniversário cadastrado
- leads com tag de cliente ativo

**Atendimento**
- atendimentos por período
- por atendente
- por canal
- tempo médio
- horários de pico

**Comercial**
- oportunidades abertas
- oportunidades ganhas/perdidas
- valor potencial do pipeline

**Relacionamento**
- clientes sem contato há 30/60/90 dias
- clientes pós-venda
- base reativável
- clientes com alto potencial

---

## 5. Fluxos que eu faria primeiro

### Fluxo 1 — Atualizar último contato
- **Impacto:** alto
- **Dificuldade:** baixa

### Fluxo 2 — Cadastro/recadastro
- **Impacto:** alto
- **Dificuldade:** média

### Fluxo 3 — Pós-venda semanal
- **Impacto:** muito alto
- **Dificuldade:** média

### Fluxo 4 — Chatbot dúvidas frequentes
- **Impacto:** médio/alto
- **Dificuldade:** média

### Fluxo 5 — Criar oportunidade por gatilho
**Exemplos de gatilho:**
- “orçamento”
- “evento”
- “festa”
- “casamento”
- “corporativo”

**Resultado:** criar oportunidade no CRM.

- **Impacto:** alto
- **Dificuldade:** média/alta

---

## 6. O que não fazer primeiro

Não começar por:
- objeto customizado avançado
- automação muito complexa
- campanha sofisticada demais
- dashboard gigante
- integração cheia de exceção

Porque isso parece bonito, mas atrasa execução.

---

## 7. Ordem real de execução

### Sprint 1
- mapear campos
- padronizar tags
- criar `data_ultimo_contato`
- criar relatório de base

### Sprint 2
- chatbot cadastro/recadastro
- fluxo de atualização de contato
- tag `cadastrado`

### Sprint 3
- campanha pós-venda semanal
- segmento de reativação
- tag `pos_venda`

### Sprint 4
- chatbot IA + fallback humano
- dashboard de SAC

### Sprint 5
- pipeline de encomendas/eventos
- criação automática de oportunidades

---

## 8. Leitura direta do BigDog

Se tu quer retorno de negócio, o SprintHub tem que virar 3 coisas:

### 1. Memória viva do cliente
Quem é, de onde veio, quando falou, como compra.

### 2. Máquina de recorrência
Pós-venda, reativação, relacionamento.

### 3. Painel de controle do atendimento
Quem atende, quanto tempo demora, onde aperta.

---

## 9. Plano recomendado

### Pacote inicial recomendado
1. `data_ultimo_contato`
2. cadastro/recadastro
3. pós-venda semanal
4. dashboard SAC
5. pipeline de encomendas

Esse é o melhor equilíbrio entre:
- impacto
- simplicidade
- retorno
- velocidade de execução

---

## 10. Decisão em uma frase
**Primeiro organizar base e recorrência. Depois escalar atendimento. Depois sofisticar CRM.**
