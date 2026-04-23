# Skill: Agendamento de Call

## O que faz
Agenda call de vendas com o lead qualificado, propondo horários disponíveis e registrando no sistema.

## Quando usar
Quando um lead é qualificado com score ≥ 7 e demonstra interesse em produto premium.

## Processo

1. **Verificar disponibilidade** — consultar agenda do responsável
2. **Propor 3 horários** — sempre dar opções (manhã/tarde, dias diferentes)
3. **Confirmar** — após escolha, confirmar horário e detalhes
4. **Registrar** — atualizar `dados/leads.csv` com status "call agendada"
5. **Notificar** — enviar alerta no tópico 💰 Vendas

## Template de mensagem

```
Perfeito! Tenho horários disponíveis:
- [Dia] [Data] às [Hora]
- [Dia] [Data] às [Hora]
- [Dia] [Data] às [Hora]

Qual funciona melhor pra você?
```

## Após agendamento

```
Agendado! ✅
[Dia] [Data] às [Hora] — call com [Responsável] ([Duração])
Você vai receber um link por aqui.

Enquanto isso, dá uma olhada nesse [conteúdo relevante].
```

## Regras
- Calls sempre de 20 min (não prometer mais)
- Mínimo 24h de antecedência
- Se lead não aparecer → retry 1x com nova proposta
- Se retry ignorado → marcar como "no-show" e parar
