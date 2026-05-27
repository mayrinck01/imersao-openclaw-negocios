import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from automacoes.webhooks.pagarme_fraud import CustomerHistoryResult, FraudHotlist, LocalMogoHistoryChecker, MogoOrderSummary, RiskEngine, extract_charge, format_alert, names_compatible, normalized_sha256


class FakeHistoryChecker:
    def __init__(self, result):
        self.result = result

    def lookup(self, charge):
        return self.result


def event(event_type, charge_id, *, customer_name="Cliente Limpo", email="cliente.limpo@example.com", document="123", phone=None, amount=23000, card_last4="1111", brand="visa", holder="CLIENTE LIMPO", holder_document=None, created_at=None, status=None, payment_method="credit_card"):
    created_at = created_at or datetime.now(timezone.utc).isoformat()
    status = status or ("paid" if event_type == "charge.paid" else "failed")
    if holder_document is None:
        holder_document = document
    return {
        "id": f"hook_{charge_id}",
        "type": event_type,
        "created_at": created_at,
        "data": {
            "id": charge_id,
            "amount": amount,
            "status": status,
            "payment_method": payment_method,
            "customer": {"name": customer_name, "email": email, "document": document, "phones": ({"mobile_phone": {"country_code": "55", "area_code": phone[:2], "number": phone[2:]}} if phone else {})},
            "last_transaction": {
                "status": "captured" if status == "paid" else "not_authorized",
                "card": {"brand": brand, "last_four_digits": card_last4, "holder_name": holder, "holder_document": holder_document},
                "acquirer_message": "Transação capturada" if status == "paid" else "Não autorizado",
                "acquirer_return_code": "00" if status == "paid" else "1035",
            },
        },
    }


class PagarmeFraudTests(unittest.TestCase):
    def test_name_initial_is_compatible_with_full_middle_name(self):
        self.assertTrue(names_compatible("Joao Victor Martins", "JOAO V MARTINS"))

    def test_different_card_holder_triggers_alert_on_paid_charge(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event("charge.paid", "ch_1", customer_name="Patricia Bernardo", holder="Natalia Nascimento Andrade"))
            self.assertTrue(result.alert)
            self.assertIn("titular diferente", " ".join(result.reasons).lower())

    def test_partial_customer_name_in_email_or_holder_suppresses_holder_mismatch_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_iasminy",
                customer_name="Iasminy",
                email="vergetti.iasminy@gmail.com",
                holder="IASMINY VERGETTI",
            ))
            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)
            self.assertNotIn("titular diferente", " ".join(result.reasons).lower())

    def test_recent_failed_attempt_triggers_alert_even_without_card_change(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            now = datetime.now(timezone.utc)
            failed = engine.handle_event(event(
                "charge.payment_failed",
                "ch_fail_same_card",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                card_last4="8391",
            ))
            self.assertFalse(failed.alert)
            paid = engine.handle_event(event(
                "charge.paid",
                "ch_paid_same_card",
                created_at=now.isoformat(),
                card_last4="8391",
            ))
            self.assertTrue(paid.alert)
            self.assertIn("falha recente", " ".join(paid.reasons).lower())

    def test_recent_failed_charge_then_paid_same_identity_triggers_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            now = datetime.now(timezone.utc)
            failed = engine.handle_event(event("charge.payment_failed", "ch_fail", created_at=(now - timedelta(minutes=5)).isoformat(), card_last4="8391", brand="mastercard"))
            self.assertFalse(failed.alert)
            paid = engine.handle_event(event("charge.paid", "ch_paid", created_at=now.isoformat(), card_last4="0299", brand="elo"))
            self.assertTrue(paid.alert)
            reasons = " ".join(paid.reasons).lower()
            self.assertIn("falha recente", reasons)
            self.assertIn("cartões diferentes", reasons)

    def test_clean_paid_charge_does_not_trigger_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event("charge.paid", "ch_clean"))
            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)

    def test_card_holder_document_mismatch_triggers_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "document", "valid_purchase", None))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_holder_document_mismatch",
                document="12345678900",
                holder_document="98765432100",
            ))

            self.assertTrue(result.alert)
            self.assertEqual(50, result.score)
            self.assertIn("cpf do cliente diferente", " ".join(result.reasons).lower())

    def test_card_holder_document_missing_triggers_operational_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_holder_document_missing",
                document="12345678900",
                holder_document="",
            ))

            self.assertTrue(result.alert)
            self.assertEqual(50, result.score)
            self.assertIn("cpf do titular do cartão ausente", " ".join(result.reasons).lower())

    def test_pix_paid_charge_never_triggers_antifraud_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_pix",
                customer_name="Patricia Bernardo",
                holder="Natalia Nascimento Andrade",
                payment_method="pix",
            ))
            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)

    def test_pix_failure_does_not_pollute_later_card_charge(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.payment_failed",
                "ch_pix_fail",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                payment_method="pix",
            ))
            result = engine.handle_event(event(
                "charge.paid",
                "ch_card_clean",
                created_at=now.isoformat(),
                payment_method="credit_card",
            ))
            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)

    def test_mogo_prior_valid_purchase_suppresses_holder_mismatch_only(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "email", "valid_purchase", None))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_returning_holder_mismatch",
                customer_name="Cliente Recorrente",
                email="cliente.recorrente@example.com",
                holder="Outro Titular",
            ))
            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)
            self.assertNotIn("titular diferente", " ".join(result.reasons).lower())

    def test_mogo_prior_valid_purchase_suppresses_recent_failure_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "email", "valid_purchase", None))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.payment_failed",
                "ch_fail_returning",
                email="cliente@example.com",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                card_last4="1111",
            ))
            result = engine.handle_event(event(
                "charge.paid",
                "ch_paid_returning",
                email="cliente@example.com",
                created_at=now.isoformat(),
                card_last4="1111",
            ))
            self.assertFalse(result.alert)
            self.assertNotIn("falha recente", " ".join(result.reasons).lower())

    def test_single_name_only_mogo_match_does_not_suppress_retry_alert_when_identity_fields_exist(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "name",
                "valid_purchase",
                None,
                valid_purchase_count=1,
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.payment_failed",
                "ch_name_only_fail",
                email="cliente.identificado@example.com",
                document="12345678900",
                phone="21999999999",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                card_last4="1111",
                brand="visa",
            ))
            result = engine.handle_event(event(
                "charge.paid",
                "ch_name_only_paid",
                email="cliente.identificado@example.com",
                document="12345678900",
                phone="21999999999",
                created_at=now.isoformat(),
                card_last4="2222",
                brand="mastercard",
            ))

            self.assertTrue(result.alert)
            reasons = " ".join(result.reasons).lower()
            self.assertIn("falha recente", reasons)
            self.assertIn("cartões diferentes", reasons)

    def test_recurrent_name_only_mogo_customer_suppresses_weak_identity_alerts(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "name",
                "valid_purchase",
                None,
                valid_purchase_count=2,
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_miguel_like",
                customer_name="Miguel Angel Gomez",
                email="mconsuelo.quintero@udea.edu.co",
                document="04426337771",
                holder="MARIA QUINTERO",
            ))

            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)
            reasons = " ".join(result.reasons).lower()
            self.assertNotIn("titular diferente", reasons)
            self.assertNotIn("email pouco compatível", reasons)

    def test_name_address_mogo_match_suppresses_card_holder_document_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "name_address",
                "valid_purchase",
                None,
                MogoOrderSummary(
                    order_number="008715",
                    customer_name="Luciana",
                    address="Rua Dona Mariana, 182, 1206 bloco 1",
                    neighborhood="Botafogo - Rio de Janeiro/RJ",
                    origin="iFood",
                ),
                valid_purchase_count=1,
                operational_order=MogoOrderSummary(
                    order_number="008749",
                    customer_name="Luciana Lopes Marinho",
                    address="Rua Dona Mariana, 182, 1206 bloco 1",
                    neighborhood="Botafogo - Rio de Janeiro/RJ",
                    amount="153,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_luciana_address_match",
                customer_name="Luciana Lopes Marinho",
                holder="Outro Titular",
                document="12345678900",
                holder_document="98765432100",
                amount=15300,
            ))

            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)
            reasons = " ".join(result.reasons).lower()
            self.assertNotIn("cpf do cliente diferente", reasons)
            self.assertNotIn("titular diferente", reasons)

    def test_single_mogo_purchase_suppresses_checkout_retry_alerts(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "name",
                "valid_purchase",
                None,
                valid_purchase_count=1,
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.payment_failed",
                "ch_single_purchase_fail",
                email="",
                document="",
                holder_document="98765432100",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                card_last4="1111",
                brand="visa",
            ))
            result = engine.handle_event(event(
                "charge.paid",
                "ch_single_purchase_paid",
                email="",
                document="",
                holder_document="98765432100",
                created_at=now.isoformat(),
                card_last4="2222",
                brand="mastercard",
            ))

            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)
            reasons = " ".join(result.reasons).lower()
            self.assertNotIn("falha recente", reasons)
            self.assertNotIn("cartões diferentes", reasons)

    def test_mogo_prior_valid_purchase_suppresses_multiple_cards_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "email", "valid_purchase", None))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.payment_failed",
                "ch_card_a",
                email="cliente@example.com",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                card_last4="1111",
                brand="visa",
            ))
            result = engine.handle_event(event(
                "charge.paid",
                "ch_card_b",
                email="cliente@example.com",
                created_at=now.isoformat(),
                card_last4="2222",
                brand="mastercard",
            ))
            self.assertFalse(result.alert)
            self.assertNotIn("cartões diferentes", " ".join(result.reasons).lower())

    def test_recurrent_mogo_customer_suppresses_checkout_retry_alerts(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "email",
                "valid_purchase",
                None,
                valid_purchase_count=2,
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.payment_failed",
                "ch_recurrent_fail_a",
                email="cliente@example.com",
                created_at=(now - timedelta(minutes=5)).isoformat(),
                card_last4="1111",
                brand="visa",
            ))
            engine.handle_event(event(
                "charge.payment_failed",
                "ch_recurrent_fail_b",
                email="cliente@example.com",
                created_at=(now - timedelta(minutes=4)).isoformat(),
                card_last4="2222",
                brand="mastercard",
            ))
            result = engine.handle_event(event(
                "charge.paid",
                "ch_recurrent_paid",
                email="cliente@example.com",
                created_at=now.isoformat(),
                card_last4="3333",
                brand="elo",
            ))

            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)
            reasons = " ".join(result.reasons).lower()
            self.assertNotIn("falha recente", reasons)
            self.assertNotIn("cartões diferentes", reasons)

    def test_hotlisted_customer_name_triggers_alert_even_with_mogo_history(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "name", "valid_purchase", None))
            hotlist = FraudHotlist(
                frozenset(),
                customer_name_hashes=frozenset({normalized_sha256("Contestacao Confirmada")}),
            )
            engine = RiskEngine(db.name, history_checker=checker, hotlist=hotlist)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_hotlisted_customer_name",
                customer_name="Contestacao Confirmada",
                email="cliente@example.com",
                holder="CONTESTACAO CONFIRMADA",
            ))
            self.assertTrue(result.alert)
            self.assertIn("lista quente", " ".join(result.reasons).lower())

    def test_hotlisted_holder_name_alone_does_not_trigger_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "name", "valid_purchase", None))
            hotlist = FraudHotlist.from_holder_names(["Titular Cartao"])
            engine = RiskEngine(db.name, history_checker=checker, hotlist=hotlist)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_hotlisted_holder_only",
                customer_name="Cliente Cadastro",
                email="cliente@example.com",
                holder="TITULAR CARTAO",
            ))
            self.assertFalse(result.alert)
            self.assertNotIn("lista quente", " ".join(result.reasons).lower())

    def test_hotlisted_customer_document_triggers_alert_even_with_mogo_history(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "name", "valid_purchase", None))
            hotlist = FraudHotlist.from_customer_documents(["123.456.789-00"])
            engine = RiskEngine(db.name, history_checker=checker, hotlist=hotlist)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_hotlisted_document",
                customer_name="Cliente Qualquer",
                document="12345678900",
                holder="CLIENTE QUALQUER",
            ))
            self.assertTrue(result.alert)
            self.assertIn("lista quente", " ".join(result.reasons).lower())

    def test_hotlisted_card_alone_does_not_trigger_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "name", "valid_purchase", None))
            hotlist = FraudHotlist.from_cards([("Visa", "0294")])
            engine = RiskEngine(db.name, history_checker=checker, hotlist=hotlist)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_hotlisted_card",
                card_last4="0294",
                brand="visa",
            ))
            self.assertFalse(result.alert)
            self.assertNotIn("lista quente", " ".join(result.reasons).lower())

    def test_mogo_lookup_failure_does_not_suppress_weak_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "error", "timeout"))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_lookup_failed",
                customer_name="Patricia Bernardo",
                holder="Natalia Nascimento Andrade",
            ))
            self.assertTrue(result.alert)
            reasons = " ".join(result.reasons).lower()
            self.assertIn("titular diferente", reasons)
            self.assertIn("histórico mogo não validado", reasons)

    def test_alert_includes_mogo_order_context_when_available(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "phone",
                "valid_purchase",
                None,
                MogoOrderSummary(
                    order_number="037222",
                    status="Pago",
                    customer_name="Cliente Recorrente",
                    date="22/05/2026",
                    delivery_date="27/05/2026",
                    delivery_time="15:30",
                    address="Rua Dias Ferreira, 123",
                    neighborhood="Leblon",
                    amount="213,30",
                    origin="Neemo",
                    item="TORTA F13",
                ),
            ))
            hotlist = FraudHotlist.from_customer_documents(["123"])
            engine = RiskEngine(db.name, history_checker=checker, hotlist=hotlist)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.payment_failed",
                "ch_mogo_fail",
                phone="21999999999",
                created_at=(now - timedelta(minutes=5)).isoformat(),
            ))
            result = engine.handle_event(event(
                "charge.paid",
                "ch_mogo_paid",
                phone="21999999999",
                created_at=now.isoformat(),
                card_last4="2222",
            ))

            alert = format_alert(result)

            self.assertIn("POSSÍVEL FRAUDE — SEGURAR ENTREGA", alert)
            self.assertIn("HISTÓRICO MOGO: pedido #037222", alert)
            self.assertIn("Status operacional: SEGURAR / NÃO ENTREGAR", alert)
            self.assertIn("*Score antifraude: 50 — 🌡️ 🔴 FORTE (50+ segura entrega)*", alert)
            self.assertIn("Status operacional: SEGURAR / NÃO ENTREGAR\n\n*Score antifraude: 50", alert)
            self.assertLess(alert.index("Status operacional: SEGURAR / NÃO ENTREGAR"), alert.index("*Score antifraude: 50"))
            self.assertLess(alert.index("*Score antifraude: 50"), alert.index("Pedido"))
            self.assertLess(alert.index("Pedido"), alert.index("Resumo"))
            self.assertIn("• Modalidade: Entrega", alert)
            self.assertIn("• Agendamento: 27/05/2026 15:30", alert)
            self.assertIn("• Endereço de entrega: Rua Dias Ferreira, 123 - Leblon", alert)
            self.assertIn("Resumo", alert)
            self.assertIn("• Valor do pedido: R$ 230,00", alert)
            self.assertNotIn("• Origem pagamento: Pagar.me", alert)
            self.assertNotIn("• Cobrança Pagar.me:", alert)
            self.assertIn("• Nível do alerta: FORTE", alert)
            self.assertIn("Cliente no Mogo", alert)
            self.assertIn("• Nome: Cliente Recorrente", alert)
            self.assertIn("Pagamento Pagar.me", alert)
            self.assertIn("Motivos do alerta", alert)
            self.assertIn("• Dado em lista quente", alert)

    def test_alert_says_mogo_order_not_found_when_no_context(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found", None))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_no_mogo_context",
                customer_name="Patricia Bernardo",
                email="alepmotta19@gmail.com",
                holder="Natalia Nascimento Andrade",
            ))

            alert = format_alert(result)

            self.assertIn("HISTÓRICO MOGO: não localizado", alert)
            self.assertIn("Status operacional: SEGURAR / NÃO ENTREGAR", alert)
            self.assertIn("*Score antifraude: 120 — 🌡️ 🔴 FORTE (50+ segura entrega)*", alert)
            self.assertLess(alert.index("Status operacional: SEGURAR / NÃO ENTREGAR"), alert.index("*Score antifraude: 120"))
            self.assertLess(alert.index("*Score antifraude: 120"), alert.index("Resumo"))
            self.assertIn("alepmotta19@gmail.com", alert)
            self.assertNotIn("alepmotta19@gmail,com", alert)

    def test_alert_treats_order_without_schedule_as_immediate(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "phone",
                "valid_purchase",
                None,
                MogoOrderSummary(
                    order_number="037333",
                    status="Pago",
                    customer_name="Cliente Urgente",
                    address="Rua Visconde de Pirajá, 44",
                    neighborhood="Ipanema",
                    amount="208,80",
                    origin="WhatsApp",
                    item="BOLO",
                ),
            ))
            hotlist = FraudHotlist.from_customer_documents(["123"])
            engine = RiskEngine(db.name, history_checker=checker, hotlist=hotlist)
            result = engine.handle_event(event("charge.paid", "ch_immediate_delivery", phone="21999999999"))

            alert = format_alert(result)

            self.assertIn("Pedido", alert)
            self.assertIn("• Modalidade: Entrega", alert)
            self.assertIn("• Agendamento: não informado — ⚠️ tratar como para agora", alert)
            self.assertIn("• Endereço de entrega: Rua Visconde de Pirajá, 44 - Ipanema", alert)

    def test_alert_uses_operational_mogo_order_when_no_prior_history(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="038708",
                    status="Pendente",
                    customer_name="Cristina Tobji",
                    delivery_date="27/05/2026",
                    delivery_time="16:00",
                    fulfillment="P/Entregar (Motoboy)",
                    address="Rua Dona Mariana, 136, 104",
                    neighborhood="Botafogo - Rio de Janeiro/RJ",
                    amount="208,80",
                    origin="Neemo",
                    phone="21988780670",
                    email="cristina.tobji@jree.com.br",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_operational_order",
                customer_name="Cristina Tobji",
                email="cristina.tobji@jree.com.br",
                document="54246911100",
                phone="21988780670",
                amount=20880,
                holder="J R S DE AQUINO",
                holder_document="12345678901",
            ))

            alert = format_alert(result)

            self.assertIn("HISTÓRICO MOGO: não localizado", alert)
            self.assertIn("Pedido", alert)
            self.assertIn("• Modalidade: Entrega", alert)
            self.assertIn("• Agendamento: 27/05/2026 16:00", alert)
            self.assertIn("• Endereço de entrega: Rua Dona Mariana, 136, 104 - Botafogo - Rio de Janeiro/RJ", alert)
            self.assertIn("• Pedido operacional: #038708 localizado no Mogo", alert)
            self.assertNotIn("• Origem pagamento: Pagar.me", alert)
            self.assertNotIn("• Cobrança Pagar.me:", alert)

    def test_alert_treats_operational_order_without_delivery_time_as_immediate(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="038709",
                    status="Pendente",
                    customer_name="Cliente Agora",
                    delivery_date="26/05/2026",
                    delivery_time="",
                    fulfillment="P/Entregar (Motoboy)",
                    address="Rua Jardim Botanico, 100",
                    neighborhood="Jardim Botanico - Rio de Janeiro/RJ",
                    amount="150,00",
                    phone="21999999999",
                    email="agora@example.com",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_operational_order_now",
                customer_name="Cliente Agora",
                email="agora@example.com",
                phone="21999999999",
                amount=15000,
                holder="Outro Nome",
                holder_document="12345678901",
            ))

            alert = format_alert(result)

            self.assertIn("• Modalidade: Entrega", alert)
            self.assertIn("• Agendamento: 26/05/2026 — sem hora agendada — ⚠️ tratar como para agora", alert)
            self.assertIn("• Endereço de entrega: Rua Jardim Botanico, 100 - Jardim Botanico - Rio de Janeiro/RJ", alert)

    def test_local_mogo_history_checker_finds_operational_pending_order_without_valid_history(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "Pendentes"
            folder.mkdir(parents=True)
            (folder / "26-05-2026.json").write_text(json.dumps({
                "registros": [{
                    "NumeroPedido": "038708",
                    "StatusEntrega": "Pendente",
                    "NomeCliente": "Cristina Tobji",
                    "DataEntrega": "27/05/2026",
                    "HoraEntregaTxt": "16:00",
                    "ObsEntrega_Descricao": "P/Entregar (Motoboy)",
                    "Logradouro": "Rua Dona Mariana",
                    "Numero": "136",
                    "Complemento": "104",
                    "Bairro": "Botafogo",
                    "Cidade": "Rio de Janeiro",
                    "Estado": "RJ",
                    "CelularCliente": "21988780670",
                    "Email": "cristina.tobji@jree.com.br",
                    "ValorTotal": "208,80",
                    "OrigemPedido": "Neemo",
                }]
            }), encoding="utf-8")
            checker = LocalMogoHistoryChecker(root)
            result = checker.lookup(extract_charge(event(
                "charge.paid",
                "ch_pending_order",
                customer_name="Cristina Tobji",
                email="cristina.tobji@jree.com.br",
                document="54246911100",
                phone="21988780670",
                amount=20880,
            )))

            self.assertFalse(result.has_prior_valid_purchase)
            self.assertIsNotNone(result.operational_order)
            self.assertEqual(result.operational_order.order_number, "038708")
            self.assertEqual(result.operational_order.delivery_date, "27/05/2026")
            self.assertEqual(result.operational_order.delivery_time, "16:00")
            self.assertEqual(result.operational_order.address, "Rua Dona Mariana, 136, 104")
            self.assertEqual(result.operational_order.neighborhood, "Botafogo - Rio de Janeiro/RJ")

    def test_local_mogo_history_checker_matches_paid_purchase_by_phone(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "Historico Pagamento"
            folder.mkdir(parents=True)
            (folder / "01-2026.json").write_text(json.dumps({
                "registros": [{
                    "cliente": "Cliente Telefone",
                    "telefone": "21 99999-9999",
                    "dataPag": "10/01/2026",
                    "numPed": "008001",
                }]
            }), encoding="utf-8")
            checker = LocalMogoHistoryChecker(root)
            result = checker.lookup(extract_charge(event("charge.paid", "ch_phone", phone="21999999999")))
            self.assertTrue(result.has_prior_valid_purchase)
            self.assertEqual(result.matched_by, "phone")
            self.assertEqual(result.valid_purchase_count, 1)

    def test_local_mogo_history_checker_returns_order_context(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "Lancamentos Pedidos"
            folder.mkdir(parents=True)
            (folder / "05-2026.json").write_text(json.dumps({
                "registros": [{
                    "A0": "22/05/2026",
                    "A13": "037222",
                    "A10": "Pago",
                    "A2": "TORTA F13",
                    "A4": "213,30",
                    "A5": "Alexandra Pereira",
                    "OrigemPedido": "neemo",
                }]
            }), encoding="utf-8")
            checker = LocalMogoHistoryChecker(root)
            result = checker.lookup(extract_charge(event(
                "charge.paid",
                "ch_context",
                customer_name="Alexandra Pereira",
                email="semnome@example.com",
                document="",
            )))

            self.assertTrue(result.has_prior_valid_purchase)
            self.assertIsNotNone(result.order)
            self.assertEqual(result.order.order_number, "037222")
            self.assertEqual(result.order.status, "Pago")
            self.assertEqual(result.order.origin, "neemo")
            self.assertEqual(result.order.item, "TORTA F13")

    def test_local_mogo_history_checker_counts_unique_valid_purchases(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "Lancamentos Pedidos"
            folder.mkdir(parents=True)
            (folder / "01-2026.json").write_text(json.dumps({
                "registros": [
                    {"A5": "Cliente Recorrente", "A10": "Pago", "A13": "008001", "A2": "Item 1"},
                    {"A5": "Cliente Recorrente", "A10": "Pago", "A13": "008001", "A2": "Item 2"},
                    {"A5": "Cliente Recorrente", "A10": "Pago", "A13": "008002", "A2": "Item 3"},
                ]
            }), encoding="utf-8")
            checker = LocalMogoHistoryChecker(root)
            result = checker.lookup(extract_charge(event(
                "charge.paid",
                "ch_recurrent_name",
                customer_name="Cliente Recorrente",
                email="semnome@example.com",
                document="",
            )))

            self.assertTrue(result.has_prior_valid_purchase)
            self.assertEqual(result.valid_purchase_count, 2)

    def test_local_mogo_history_checker_matches_paid_purchase_by_careful_name_fallback(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "Lancamentos Pedidos"
            folder.mkdir(parents=True)
            (folder / "01-2026.json").write_text(json.dumps({
                "registros": [{
                    "A5": "Patricia Bernardo",
                    "A10": "Pago",
                    "A13": "008002",
                }]
            }), encoding="utf-8")
            checker = LocalMogoHistoryChecker(root)
            result = checker.lookup(extract_charge(event("charge.paid", "ch_name", customer_name="Patricia Bernardo", email="semnome@example.com", document="")))
            self.assertTrue(result.has_prior_valid_purchase)
            self.assertEqual(result.matched_by, "name")

    def test_local_mogo_history_checker_matches_partial_name_with_exact_delivery_address(self):
        with tempfile.TemporaryDirectory() as root:
            delivered = Path(root) / "Pedidos Entregues"
            delivered.mkdir(parents=True)
            (delivered / "10-01-2026.json").write_text(json.dumps({
                "registros": [{
                    "NumeroPedido": "008715",
                    "StatusEntrega": "Entregue",
                    "NomeCliente": "Luciana",
                    "Logradouro": "Rua Dona Mariana",
                    "Numero": "182",
                    "Complemento": "1206 bloco 1",
                    "Bairro": "Botafogo",
                    "Cidade": "Rio de Janeiro",
                    "Estado": "RJ",
                    "OrigemPedido": "iFood",
                }]
            }), encoding="utf-8")
            pending = Path(root) / "Pendentes"
            pending.mkdir(parents=True)
            (pending / "27-05-2026.json").write_text(json.dumps({
                "registros": [{
                    "NumeroPedido": "008749",
                    "StatusEntrega": "Pendente",
                    "NomeCliente": "Luciana Lopes Marinho",
                    "Logradouro": "Rua Dona Mariana",
                    "Numero": "182",
                    "Complemento": "1206 bloco 1",
                    "Bairro": "Botafogo",
                    "Cidade": "Rio de Janeiro",
                    "Estado": "RJ",
                    "ValorTotal": "153,00",
                }]
            }), encoding="utf-8")

            checker = LocalMogoHistoryChecker(root)
            result = checker.lookup(extract_charge(event(
                "charge.paid",
                "ch_luciana_partial_address",
                customer_name="Luciana Lopes Marinho",
                email="outro@example.com",
                document="12345678900",
                amount=15300,
            )))

            self.assertTrue(result.has_prior_valid_purchase)
            self.assertEqual(result.matched_by, "name_address")
            self.assertEqual(result.order.order_number, "008715")
            self.assertEqual(result.operational_order.order_number, "008749")

    def test_local_mogo_history_checker_ignores_non_paid_purchase_status(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "Lancamentos Pedidos"
            folder.mkdir(parents=True)
            (folder / "01-2026.json").write_text(json.dumps({
                "registros": [{
                    "A5": "Patricia Bernardo",
                    "A10": "Cancelado",
                    "A13": "008003",
                }]
            }), encoding="utf-8")
            checker = LocalMogoHistoryChecker(root)
            result = checker.lookup(extract_charge(event("charge.paid", "ch_cancelled", customer_name="Patricia Bernardo", email="semnome@example.com", document="")))
            self.assertFalse(result.has_prior_valid_purchase)
            self.assertEqual(result.status, "not_found")


if __name__ == "__main__":
    unittest.main()
