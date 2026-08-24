import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from automacoes.webhooks.pagarme_fraud import CustomerHistoryResult, FraudHotlist, LocalMogoHistoryChecker, MogoOrderSummary, RelatedCustomerProfile, RiskEngine, extract_charge, format_alert, format_first_purchase_alert, format_same_day_repeat_alert, format_same_day_repeat_notice, names_compatible, normalized_sha256


class FakeHistoryChecker:
    def __init__(self, result):
        self.result = result

    def lookup(self, charge):
        return self.result


def event(event_type, charge_id, *, customer_name="Cliente Limpo", email="cliente.limpo@example.com", document="123", phone=None, amount=23000, card_last4="1111", card_first6="411111", card_exp_month="12", card_exp_year="2030", brand="visa", holder="CLIENTE LIMPO", holder_document=None, created_at=None, status=None, payment_method="credit_card", billing_address=None):
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
                "card": {
                    "brand": brand,
                    "first_six_digits": card_first6,
                    "last_four_digits": card_last4,
                    "exp_month": card_exp_month,
                    "exp_year": card_exp_year,
                    "holder_name": holder,
                    "holder_document": holder_document,
                    **({"billing_address": billing_address} if billing_address else {}),
                },
                "acquirer_message": "Transação capturada" if status == "paid" else "Não autorizado",
                "acquirer_return_code": "00" if status == "paid" else "1035",
            },
        },
    }


class PagarmeFraudTests(unittest.TestCase):
    def test_related_profile_exact_address_includes_full_customer_context(self):
        checker = LocalMogoHistoryChecker("/nonexistent")
        checker._loaded = True
        checker._valid_orders = [MogoOrderSummary(
            order_number="010001", customer_name="Maria Antiga", date="10/08/2026",
            address="Rua das Flores, 10, Apto 201", neighborhood="Botafogo - Rio de Janeiro/RJ",
            amount="150,00", phone="21999990000", document="11122233344", email="maria@example.com",
        )]
        checker._operational_orders = [MogoOrderSummary(
            order_number="010002", customer_name="Cliente Novo",
            address="R. das Flores, 10, ap 201", neighborhood="Botafogo - Rio de Janeiro/RJ",
            amount="200,00", phone="21888880000", document="99988877766", email="novo@example.com",
        )]

        result = checker.lookup(extract_charge(event(
            "charge.paid", "ch_related_address", customer_name="Cliente Novo",
            email="novo@example.com", document="99988877766", phone="21888880000", amount=20000,
        )))

        self.assertEqual(1, len(result.related_profiles))
        profile = result.related_profiles[0]
        self.assertEqual("exact_address", profile.match_kind)
        self.assertEqual("Maria Antiga", profile.name)
        self.assertEqual("maria@example.com", profile.email)
        self.assertEqual("11122233344", profile.document)

    def test_related_profile_different_apartment_is_not_a_match(self):
        checker = LocalMogoHistoryChecker("/nonexistent")
        checker._loaded = True
        checker._valid_orders = [MogoOrderSummary(
            customer_name="Maria Antiga", address="Rua das Flores, 10, Apto 202",
            neighborhood="Botafogo - Rio de Janeiro/RJ", email="maria@example.com",
        )]
        checker._operational_orders = [MogoOrderSummary(
            customer_name="Cliente Novo", address="Rua das Flores, 10, Apto 201",
            neighborhood="Botafogo - Rio de Janeiro/RJ", email="novo@example.com",
        )]

        result = checker.lookup(extract_charge(event(
            "charge.paid", "ch_other_apartment", customer_name="Cliente Novo", email="novo@example.com",
        )))

        self.assertEqual((), result.related_profiles)

    def test_related_profile_full_cardholder_name_alone_is_ignored(self):
        checker = LocalMogoHistoryChecker("/nonexistent")
        checker._loaded = True
        checker._valid_orders = [MogoOrderSummary(
            customer_name="Carlos Pereira Lima", email="carlos@example.com", phone="21999990000",
            document="11122233344", address="Rua Outra, 20, Casa", date="01/08/2026", amount="180,00",
        )]

        result = checker.lookup(extract_charge(event(
            "charge.paid", "ch_holder_related", customer_name="Ana Souza", email="ana@example.com",
            holder="CARLOS PEREIRA LIMA",
        )))

        self.assertEqual((), result.related_profiles)

    def test_related_profile_holder_document_match_is_confirmed(self):
        checker = LocalMogoHistoryChecker("/nonexistent")
        checker._loaded = True
        checker._valid_orders = [MogoOrderSummary(
            customer_name="Carlos Pereira Lima", email="carlos@example.com",
            document="11122233344", date="01/08/2026", amount="180,00",
        )]

        result = checker.lookup(extract_charge(event(
            "charge.paid", "ch_holder_document_related", customer_name="Ana Souza",
            email="ana@example.com", document="99988877766", holder="CARLOS PEREIRA LIMA",
            holder_document="11122233344",
        )))

        self.assertEqual("holder_document", result.related_profiles[0].match_kind)

    def test_related_profile_holder_surname_alone_without_confirmation_is_ignored(self):
        checker = LocalMogoHistoryChecker("/nonexistent")
        checker._loaded = True
        checker._valid_orders = [MogoOrderSummary(customer_name="Outra Pessoa Souza", email="outra@example.com")]

        result = checker.lookup(extract_charge(event(
            "charge.paid", "ch_holder_homonym", customer_name="Ana Lima", email="ana@example.com",
            holder="CARLOS SOUZA",
        )))

        self.assertEqual((), result.related_profiles)

    def test_related_profile_partial_holder_with_phone_confirmation_is_informational(self):
        checker = LocalMogoHistoryChecker("/nonexistent")
        checker._loaded = True
        checker._valid_orders = [MogoOrderSummary(
            customer_name="Outra Pessoa Souza", phone="21999990000", email="outra@example.com",
        )]

        result = checker.lookup(extract_charge(event(
            "charge.paid", "ch_holder_partial_confirmed", customer_name="Ana Lima",
            email="ana@example.com", phone="21999990000", holder="CARLOS SOUZA",
        )))

        self.assertEqual("partial_holder_confirmed", result.related_profiles[0].match_kind)

    def test_related_profiles_appear_in_fraud_and_first_purchase_alerts_without_changing_score(self):
        profile = RelatedCustomerProfile(
            match_kind="exact_address", match_reason="endereço completo igual",
            name="Maria Antiga", phone="21999990000", email="maria@example.com",
            document="11122233344", address="Rua das Flores, 10, Apto 201 - Botafogo",
            last_purchase_date="10/08/2026", last_purchase_amount="150,00", valid_purchase_count=3,
        )
        charge = extract_charge(event("charge.paid", "ch_format_related", customer_name="Cliente Novo"))
        history = CustomerHistoryResult(
            False, None, "not_found", None, None, 0,
            MogoOrderSummary(customer_name="Cliente Novo", address="Rua das Flores, 10, Apto 201"),
            (profile,),
        )
        fraud_result = type("Result", (), {
            "charge": charge, "customer_history": history, "score": 50,
            "reasons": ["sinal forte"], "alert": True,
        })()
        first_result = type("Result", (), {
            "charge": charge, "customer_history": history, "score": 0,
            "reasons": [], "alert": False,
        })()

        fraud_text = format_alert(fraud_result)
        first_text = format_first_purchase_alert(first_result)

        for text in (fraud_text, first_text):
            self.assertIn("Cadastros possivelmente relacionados", text)
            self.assertIn("Maria Antiga", text)
            self.assertIn("maria@example.com", text)
            self.assertIn("não altera score nem decisão operacional", text)
        self.assertEqual(50, fraud_result.score)
        self.assertIn("• Endereço: localizado o mesmo endereço no cadastro do cliente Maria Antiga", first_text)

    def test_second_lifetime_purchase_same_brt_day_is_critical(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found", None))
            engine = RiskEngine(db.name, history_checker=checker)
            engine.handle_event(event(
                "charge.paid", "ch_first_today", document="11122233344",
                created_at="2026-08-12T13:00:00+00:00", amount=11700,
            ))
            result = engine.handle_event(event(
                "charge.paid", "ch_second_today", document="11122233344",
                created_at="2026-08-12T15:00:00+00:00", amount=13700,
            ))

            self.assertIsNotNone(result.same_day_repeat)
            self.assertEqual("critical_first_day", result.same_day_repeat.kind)
            self.assertEqual(2, result.same_day_repeat.sequence)

    def test_third_lifetime_purchase_same_brt_day_stays_critical(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found", None))
            engine = RiskEngine(db.name, history_checker=checker)
            for number, hour in ((1, 13), (2, 14)):
                engine.handle_event(event(
                    "charge.paid", f"ch_today_{number}", document="11122233344",
                    created_at=f"2026-08-12T{hour}:00:00+00:00", amount=10000 * number,
                ))
            result = engine.handle_event(event(
                "charge.paid", "ch_today_3", document="11122233344",
                created_at="2026-08-12T15:00:00+00:00", amount=30000,
            ))

            self.assertEqual("critical_first_day", result.same_day_repeat.kind)
            self.assertEqual(3, result.same_day_repeat.sequence)

    def test_old_customer_second_purchase_today_is_informational(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "document", "valid_purchase", None, valid_purchase_count=1))
            engine = RiskEngine(db.name, history_checker=checker)
            engine.handle_event(event(
                "charge.paid", "ch_yesterday", document="11122233344",
                created_at="2026-08-11T13:00:00+00:00", amount=9000,
            ))
            engine.handle_event(event(
                "charge.paid", "ch_old_first_today", document="11122233344",
                created_at="2026-08-12T13:00:00+00:00", amount=11700,
            ))
            result = engine.handle_event(event(
                "charge.paid", "ch_old_second_today", document="11122233344",
                created_at="2026-08-12T15:00:00+00:00", amount=13700,
            ))

            self.assertEqual("informational_returning", result.same_day_repeat.kind)
            self.assertEqual(2, result.same_day_repeat.sequence)

    def test_first_purchase_next_day_has_no_same_day_repeat(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "document", "valid_purchase", None, valid_purchase_count=1))
            engine = RiskEngine(db.name, history_checker=checker)
            engine.handle_event(event(
                "charge.paid", "ch_previous_day", document="11122233344",
                created_at="2026-08-12T13:00:00+00:00", amount=11700,
            ))
            result = engine.handle_event(event(
                "charge.paid", "ch_next_day", document="11122233344",
                created_at="2026-08-13T13:00:00+00:00", amount=13700,
            ))

            self.assertIsNone(result.same_day_repeat)

    def test_critical_same_day_repeat_alert_says_hold_and_lists_purchases(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found", None))
            engine = RiskEngine(db.name, history_checker=checker)
            engine.handle_event(event(
                "charge.paid", "ch_critical_first", document="11122233344",
                created_at="2026-08-12T13:00:00+00:00", amount=11700,
            ))
            result = engine.handle_event(event(
                "charge.paid", "ch_critical_second", document="11122233344",
                created_at="2026-08-12T15:00:00+00:00", amount=13700,
            ))

            text = format_same_day_repeat_alert(result)
            self.assertIn("MUITO CRÍTICO", text)
            self.assertIn("SEGURAR / NÃO ENTREGAR", text)
            self.assertIn("2ª compra", text)
            self.assertIn("R$ 117,00", text)
            self.assertIn("R$ 137,00", text)

    def test_informational_repeat_notice_does_not_hold(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "document", "valid_purchase", None, valid_purchase_count=2))
            engine = RiskEngine(db.name, history_checker=checker)
            engine.handle_event(event(
                "charge.paid", "ch_old_yesterday", document="11122233344",
                created_at="2026-08-11T13:00:00+00:00", amount=9000,
            ))
            engine.handle_event(event(
                "charge.paid", "ch_info_first", document="11122233344",
                created_at="2026-08-12T13:00:00+00:00", amount=11700,
            ))
            result = engine.handle_event(event(
                "charge.paid", "ch_info_second", document="11122233344",
                created_at="2026-08-12T15:00:00+00:00", amount=13700,
            ))

            text = format_same_day_repeat_notice(result)
            self.assertIn("AVISO INFORMATIVO", text)
            self.assertIn("NÃO SEGURA ENTREGA", text)
            self.assertNotIn("SEGURAR / NÃO ENTREGAR", text)

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

    def test_failed_attempt_within_48h_triggers_alert_for_later_paid_charge(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.payment_failed",
                "ch_fail_previous_day",
                customer_name="Ygor de Campos Garay",
                email="ninjasapo35@gmail.com",
                document="12345678900",
                created_at=(now - timedelta(hours=24)).isoformat(),
                amount=54000,
                card_last4="1111",
                brand="visa",
                holder="YGOR DE CAMPOS GARAY",
            ))
            paid = engine.handle_event(event(
                "charge.paid",
                "ch_paid_major_rubens_vaz",
                customer_name="Ygor de Campos Garay",
                email="ninjasapo35@gmail.com",
                document="12345678900",
                created_at=now.isoformat(),
                amount=48600,
                card_last4="2222",
                brand="mastercard",
                holder="YGOR DE CAMPOS GARAY",
            ))

            self.assertTrue(paid.alert)
            reasons = " ".join(paid.reasons).lower()
            self.assertIn("falha recente", reasons)
            self.assertIn("48h", reasons)
            self.assertIn("cartões diferentes", reasons)

    def test_clean_paid_charge_does_not_trigger_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event("charge.paid", "ch_clean"))
            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)

    def test_same_day_card_prefix_in_different_identity_is_advisory_only(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "document", "valid_purchase", None))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime(2026, 7, 13, 21, 58, tzinfo=timezone.utc)
            engine.handle_event(event(
                "charge.paid",
                "ch_prior_same_bin",
                customer_name="Cliente Um",
                email="cliente.um@example.com",
                document="11111111111",
                holder="CLIENTE UM",
                holder_document="11111111111",
                created_at=(now - timedelta(minutes=20)).isoformat(),
                brand="Amex",
                card_first6="374769",
                card_last4="9973",
            ))

            result = engine.handle_event(event(
                "charge.paid",
                "ch_current_same_bin",
                customer_name="Cliente Dois",
                email="cliente.dois@example.com",
                document="22222222222",
                holder="CLIENTE DOIS",
                holder_document="22222222222",
                created_at=now.isoformat(),
                brand="Amex",
                card_first6="374769",
                card_last4="7435",
            ))

            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)
            self.assertIn("mesmos 6 primeiros dígitos", " ".join(result.reasons).lower())
            self.assertIn("não bloqueia sozinho", " ".join(result.reasons).lower())

    def test_same_day_exact_card_data_does_not_alert_customer_with_prior_valid_purchase(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "document", "valid_purchase", None))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime(2026, 7, 13, 21, 58, tzinfo=timezone.utc)
            engine.handle_event(event(
                "charge.paid",
                "ch_prior_same_card_data",
                customer_name="Cliente Um",
                email="cliente.um@example.com",
                document="11111111111",
                holder="CLIENTE UM",
                holder_document="11111111111",
                created_at=(now - timedelta(minutes=20)).isoformat(),
                brand="Amex",
                card_first6="374769",
                card_last4="7435",
                card_exp_month="09",
                card_exp_year="2030",
            ))

            result = engine.handle_event(event(
                "charge.paid",
                "ch_current_same_card_data",
                customer_name="Cliente Dois",
                email="cliente.dois@example.com",
                document="22222222222",
                holder="CLIENTE DOIS",
                holder_document="22222222222",
                created_at=now.isoformat(),
                brand="Amex",
                card_first6="374769",
                card_last4="7435",
                card_exp_month="09",
                card_exp_year="2030",
            ))

            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)
            reasons = " ".join(result.reasons).lower()
            self.assertNotIn("dados do cartão", reasons)

    def test_exact_card_data_on_another_day_does_not_alert_customer_with_prior_valid_purchase(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "document", "valid_purchase", None))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime(2026, 7, 13, 21, 58, tzinfo=timezone.utc)
            engine.handle_event(event(
                "charge.paid",
                "ch_prior_same_card_data_previous_day",
                customer_name="Cliente Um",
                email="cliente.um@example.com",
                document="11111111111",
                holder="CLIENTE UM",
                holder_document="11111111111",
                created_at=(now - timedelta(days=10)).isoformat(),
                brand="Amex",
                card_first6="374769",
                card_last4="7435",
                card_exp_month="09",
                card_exp_year="2030",
            ))

            result = engine.handle_event(event(
                "charge.paid",
                "ch_current_same_card_data_any_day",
                customer_name="Cliente Dois",
                email="cliente.dois@example.com",
                document="22222222222",
                holder="CLIENTE DOIS",
                holder_document="22222222222",
                created_at=now.isoformat(),
                brand="Amex",
                card_first6="374769",
                card_last4="7435",
                card_exp_month="09",
                card_exp_year="2030",
            ))

            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)
            self.assertNotIn("dados do cartão", " ".join(result.reasons).lower())

    def test_first_purchase_alert_includes_same_day_card_prefix_advisory(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found", None))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime(2026, 7, 13, 21, 58, tzinfo=timezone.utc)
            engine.handle_event(event(
                "charge.paid",
                "ch_prior_same_prefix_first_purchase",
                customer_name="Cliente Um",
                email="cliente.um@example.com",
                document="11111111111",
                holder="CLIENTE UM",
                holder_document="11111111111",
                created_at=(now - timedelta(minutes=20)).isoformat(),
                brand="Amex",
                card_first6="374769",
                card_last4="9973",
            ))

            result = engine.handle_event(event(
                "charge.paid",
                "ch_current_same_prefix_first_purchase",
                customer_name="Cliente Dois",
                email="cliente.dois@example.com",
                document="22222222222",
                holder="CLIENTE DOIS",
                holder_document="22222222222",
                created_at=now.isoformat(),
                brand="Amex",
                card_first6="374769",
                card_last4="7435",
            ))

            self.assertTrue(result.first_purchase_alert)
            alert = format_first_purchase_alert(result)
            self.assertIn("Avisos operacionais", alert)
            self.assertIn("mesmos 6 primeiros dígitos", alert.lower())
            self.assertIn("não bloqueia sozinho", alert.lower())

    def test_clean_paid_card_without_mogo_history_triggers_first_purchase_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="039001",
                    status="Pendente",
                    customer_name="Adriano Velloso Meirelles",
                    fulfillment="Retirada na loja",
                    amount="315,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_first_purchase_pickup",
                customer_name="Adriano Velloso Meirelles",
                email="adriano@example.com",
                amount=31500,
                brand="Mastercard",
                card_last4="1234",
                holder="ADRIANO VELLOSO MEIRELLES",
            ))

            self.assertFalse(result.alert)
            self.assertTrue(result.first_purchase_alert)

            alert = format_first_purchase_alert(result)

            self.assertIn("PRIMEIRA COMPRA — CONFERIR NA RETIRADA", alert)
            self.assertIn("Status operacional: NÃO LIBERAR SEM CONFERÊNCIA", alert)
            self.assertIn("• Cliente: Adriano Velloso Meirelles", alert)
            self.assertIn("• Modalidade: Retirada", alert)
            self.assertIn("• Valor: R$ 315,00", alert)
            self.assertIn("• Cartão: Mastercard final 1234", alert)
            self.assertIn("• Titular do cartão: ADRIANO VELLOSO MEIRELLES", alert)
            self.assertIn("• Endereço: não aplicável — retirada na loja", alert)
            self.assertNotIn("Se possível, confirmar cartão", alert)
            self.assertNotIn("Observação operacional", alert)
            self.assertNotIn("Cartão é conferência auxiliar", alert)

    def test_first_purchase_alert_treats_vem_buscar_as_pickup_even_with_customer_address(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="039069",
                    status="Pendente",
                    customer_name="Elizabeth Rezende Rodrigues Barreto",
                    delivery_date="30/05/2026",
                    delivery_time="10:30",
                    fulfillment="Vem Buscar",
                    address="Rua do cadastro, 123",
                    neighborhood="Leblon - Rio de Janeiro/RJ",
                    amount="315,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_first_purchase_vem_buscar",
                customer_name="Elizabeth Rezende Rodrigues Barreto",
                amount=31500,
                brand="Mastercard",
                card_last4="8615",
                holder="ELIZABETH R R BARRETO",
            ))

            alert = format_first_purchase_alert(result)

            self.assertIn("PRIMEIRA COMPRA — CONFERIR NA RETIRADA", alert)
            self.assertIn("• Modalidade: Retirada", alert)
            self.assertIn("• Endereço: não aplicável — retirada na loja", alert)
            self.assertNotIn("CONFERIR ANTES DE ENTREGAR", alert)

    def test_first_purchase_delivery_alert_includes_schedule_and_delivery_address(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="039100",
                    status="Pendente",
                    customer_name="Cliente Entrega",
                    delivery_date="31/05/2026",
                    delivery_time="14:30",
                    fulfillment="P/Entregar (Motoboy)",
                    address="Rua Dias Ferreira, 123, Apto 401",
                    neighborhood="Leblon - Rio de Janeiro/RJ",
                    amount="315,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_first_purchase_delivery_context",
                customer_name="Cliente Entrega",
                amount=31500,
                brand="Mastercard",
                card_last4="8615",
                holder="CLIENTE ENTREGA",
            ))

            alert = format_first_purchase_alert(result)

            self.assertIn("PRIMEIRA COMPRA — CONFERIR ANTES DE ENTREGAR", alert)
            self.assertIn("• Modalidade: Entrega", alert)
            self.assertIn("• Agendamento: 31/05/2026 14:30", alert)
            self.assertIn("• Endereço de entrega: Rua Dias Ferreira, 123, Apto 401 - Leblon - Rio de Janeiro/RJ", alert)
            self.assertIn("• Endereço: não localizado em compra anterior", alert)
            self.assertNotIn("• Endereço: Rua Dias Ferreira", alert)

    def test_first_purchase_alert_includes_order_context_when_modality_is_unknown(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="039102",
                    status="Pendente",
                    customer_name="Mario Francisco de Souza Andrade",
                    delivery_date="09/07/2026",
                    delivery_time="15:00",
                    address="Rua Visconde de Pirajá, 500",
                    neighborhood="Ipanema - Rio de Janeiro/RJ",
                    amount="230,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_first_purchase_unknown_modality",
                customer_name="Mario Francisco de Souza Andrade",
                amount=23000,
                brand="Mastercard",
                card_last4="1635",
                holder="MARIO FRANCISCO DE SOUZA ANDRADE",
            ))

            alert = format_first_purchase_alert(result)

            self.assertIn("PRIMEIRA COMPRA — CONFERIR ANTES DE ENTREGAR", alert)
            self.assertIn("• Modalidade: Entrega", alert)
            self.assertIn("• Agendamento: 09/07/2026 15:00", alert)
            self.assertIn("• Endereço de entrega: Rua Visconde de Pirajá, 500 - Ipanema - Rio de Janeiro/RJ", alert)

    def test_first_purchase_alert_does_not_hide_order_context_when_modality_is_missing(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="039103",
                    status="Pendente",
                    customer_name="Cliente Sem Modalidade",
                    delivery_date="09/07/2026",
                    delivery_time="15:00",
                    amount="230,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_first_purchase_missing_modality",
                customer_name="Cliente Sem Modalidade",
                amount=23000,
            ))

            alert = format_first_purchase_alert(result)

            self.assertIn("PRIMEIRA COMPRA — CONFERIR ANTES DE ENTREGAR", alert)
            self.assertIn("• Modalidade: não localizada no alerta", alert)
            self.assertIn("• Agendamento: 09/07/2026 15:00", alert)
            self.assertIn("• Endereço de entrega: não localizado no alerta", alert)

    def test_first_purchase_pickup_alerts_any_value(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="039101",
                    status="Pendente",
                    customer_name="Cliente Retirada",
                    fulfillment="Retirada na loja",
                    amount="1,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_first_purchase_pickup_any_value",
                customer_name="Cliente Retirada",
                amount=100,
                holder="CLIENTE RETIRADA",
            ))

            self.assertFalse(result.alert)
            self.assertTrue(result.first_purchase_alert)

    def test_first_purchase_pickup_at_280_still_alerts(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="039102",
                    status="Pendente",
                    customer_name="Cliente Retirada",
                    fulfillment="Retirada na loja",
                    amount="280,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_first_purchase_pickup_at_threshold",
                customer_name="Cliente Retirada",
                amount=28000,
                holder="CLIENTE RETIRADA",
            ))

            self.assertFalse(result.alert)
            self.assertTrue(result.first_purchase_alert)

    def test_first_purchase_special_delivery_neighborhood_alerts_any_value(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="039103",
                    status="Pendente",
                    customer_name="Cliente Flamengo",
                    fulfillment="P/Entregar (Motoboy)",
                    address="Rua Senador Vergueiro, 238, apto 203",
                    neighborhood="Flamengo - Rio de Janeiro/RJ",
                    amount="1,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            at_threshold = engine.handle_event(event(
                "charge.paid",
                "ch_first_purchase_flamengo_1",
                customer_name="Cliente Flamengo",
                amount=100,
                holder="CLIENTE FLAMENGO",
            ))
            second_value = engine.handle_event(event(
                "charge.paid",
                "ch_first_purchase_flamengo_2",
                customer_name="Cliente Flamengo Maior",
                document="2",
                amount=200,
                card_last4="2222",
                holder="CLIENTE FLAMENGO MAIOR",
            ))

            self.assertFalse(at_threshold.alert)
            self.assertTrue(at_threshold.first_purchase_alert)
            self.assertFalse(second_value.alert)
            self.assertTrue(second_value.first_purchase_alert)

    def test_first_purchase_outside_zona_sul_delivery_alerts_any_value(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="039104",
                    status="Pendente",
                    customer_name="Cliente Tijuca",
                    fulfillment="P/Entregar (Motoboy)",
                    address="Rua Conde de Bonfim, 100",
                    neighborhood="Tijuca - Rio de Janeiro/RJ",
                    amount="200,25",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            outside_zona_sul = engine.handle_event(event(
                "charge.paid",
                "ch_first_purchase_tijuca_200",
                customer_name="Cliente Tijuca",
                amount=20025,
                holder="CLIENTE TIJUCA",
            ))

            self.assertFalse(outside_zona_sul.alert)
            self.assertTrue(outside_zona_sul.first_purchase_alert)

    def test_known_fraud_delivery_address_triggers_strong_antifraud_alert_for_any_customer_name(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="039106",
                    status="Pendente",
                    customer_name="Nome Novo Qualquer",
                    fulfillment="P/Entregar (Motoboy)",
                    address="Rua Euclides Da Cunha, nº 106",
                    neighborhood="São Cristóvão - Rio de Janeiro/RJ",
                    amount="120,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_known_fraud_address",
                customer_name="Outro Cliente",
                amount=12000,
                holder="OUTRO CLIENTE",
            ))

            self.assertTrue(result.alert)
            self.assertFalse(result.first_purchase_alert)
            self.assertEqual(50, result.score)
            self.assertIn("endereço com fraude anterior", " ".join(result.reasons).lower())

    def test_major_rubens_vaz_hotlist_triggers_strong_antifraud_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="047286",
                    status="Pendente",
                    customer_name="Patrick Pereira Monnerat",
                    fulfillment="P/Entregar (Motoboy)",
                    address="Rua Major Rúbens Vaz, 127, casa",
                    neighborhood="Gávea - Rio de Janeiro/RJ",
                    amount="486,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_major_rubens_vaz",
                customer_name="Patrick Pereira Monnerat",
                amount=48600,
                holder="PATRICK PEREIRA MONNERAT",
            ))

            self.assertTrue(result.alert)
            self.assertFalse(result.first_purchase_alert)
            self.assertGreaterEqual(result.score, 50)
            self.assertIn("major rubens vaz", " ".join(result.reasons).lower())

    def test_praca_santos_dumont_hotlist_triggers_strong_antifraud_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="050000",
                    status="Pendente",
                    customer_name="Cliente Novo",
                    fulfillment="P/Entregar (Motoboy)",
                    address="Praça Santos Dumont, nº 55",
                    neighborhood="Gávea - Rio de Janeiro/RJ",
                    amount="333,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_praca_santos_dumont",
                customer_name="Cliente Novo",
                amount=33300,
                holder="CLIENTE NOVO",
            ))

            self.assertTrue(result.alert)
            self.assertFalse(result.first_purchase_alert)
            self.assertGreaterEqual(result.score, 50)
            reasons = " ".join(result.reasons).lower()
            self.assertIn("endereço com fraude anterior", reasons)
            self.assertIn("santos dumont", reasons)

    def test_known_fraud_billing_address_triggers_even_without_mogo_operational_match(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found"))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_patrick_major_rubens_vaz_billing",
                customer_name="patrick pereira monnerat",
                email="patrickferreiratrindade09@gmail.com",
                document="03784628656",
                amount=52020,
                brand="Amex",
                card_last4="0537",
                holder="PATRICK P MONNERAT",
                billing_address={
                    "line_1": "127, Rua Major Rúbens Vaz, Gávea",
                    "line_2": "casa",
                    "city": "Rio De Janeiro",
                    "state": "RJ",
                    "zip_code": "22470070",
                },
            ))

            self.assertTrue(result.alert)
            self.assertFalse(result.first_purchase_alert)
            self.assertGreaterEqual(result.score, 50)
            self.assertIn("endereço com fraude anterior", " ".join(result.reasons).lower())
            self.assertIn("major rubens vaz", " ".join(result.reasons).lower())

    def test_first_purchase_value_cutoffs_do_not_suppress_antifraud_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                False,
                None,
                "not_found",
                None,
                None,
                0,
                MogoOrderSummary(
                    order_number="039105",
                    status="Pendente",
                    customer_name="Cliente Flamengo",
                    fulfillment="P/Entregar (Motoboy)",
                    address="Rua Senador Vergueiro, 238",
                    neighborhood="Flamengo - Rio de Janeiro/RJ",
                    amount="227,00",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_low_value_antifraud_signal",
                customer_name="Cliente Flamengo",
                document="12345678900",
                amount=22700,
                holder="TITULAR DIFERENTE",
                holder_document="98765432100",
            ))

            self.assertTrue(result.alert)
            self.assertFalse(result.first_purchase_alert)
            self.assertIn("cpf do cliente diferente", " ".join(result.reasons).lower())

    def test_prior_mogo_history_suppresses_first_purchase_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "phone",
                "valid_purchase",
                None,
                MogoOrderSummary(order_number="032852", customer_name="daniela vaz"),
                valid_purchase_count=2,
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_returning_no_first_purchase",
                customer_name="daniela vaz",
                email="daniela@example.com",
                phone="21988955515",
            ))

            self.assertFalse(result.alert)
            self.assertFalse(result.first_purchase_alert)

    def test_card_holder_document_mismatch_triggers_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_holder_document_mismatch",
                document="12345678900",
                holder_document="98765432100",
            ))

            self.assertTrue(result.alert)
            self.assertEqual(50, result.score)
            self.assertIn("cpf do cliente diferente", " ".join(result.reasons).lower())

    def test_alert_distinguishes_customer_document_from_card_holder_document(self):
        with tempfile.NamedTemporaryFile() as db:
            engine = RiskEngine(db.name)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_holder_document_alert_copy",
                customer_name="Felipe Alvite",
                email="felipealvite@example.com",
                document="099.932.937-50",
                holder="JULIANA DE C LOPEZ",
                holder_document="12429598744",
            ))

            alert = format_alert(result)

            self.assertIn("• Documento do cliente Pagar.me: 099.932.937-50", alert)
            self.assertIn("• Documento do titular do cartão: final 8744", alert)
            self.assertNotIn("• Documento Pagar.me:", alert)

    def test_name_only_mogo_history_does_not_suppress_card_holder_document_mismatch_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "name", "valid_purchase", None, valid_purchase_count=2))
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_returning_holder_document_mismatch",
                document="12345678900",
                holder_document="98765432100",
            ))

            self.assertTrue(result.alert)
            self.assertEqual(50, result.score)
            self.assertIn("cpf do cliente diferente", " ".join(result.reasons).lower())

    def test_prior_paid_pagarme_charge_suppresses_holder_document_mismatch_when_mogo_export_lags(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found"))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.paid",
                "ch_prior_paid_same_customer",
                customer_name="Renata Marquina",
                email="renata@example.com",
                document="12345678900",
                holder="ISABEL C A ALVES",
                holder_document="98765432100",
                created_at=(now - timedelta(days=8)).isoformat(),
            ))

            result = engine.handle_event(event(
                "charge.paid",
                "ch_returning_customer_mogo_lag",
                customer_name="Renata Marquina",
                email="renata@example.com",
                document="12345678900",
                holder="ISABEL C A ALVES",
                holder_document="98765432100",
                created_at=now.isoformat(),
            ))

            self.assertFalse(result.alert)
            self.assertFalse(result.first_purchase_alert)
            self.assertEqual("pagarme_prior_charge", result.customer_history.matched_by)
            self.assertNotIn("cpf do cliente diferente", " ".join(result.reasons).lower())

    def test_cancelled_first_pagarme_charge_does_not_suppress_first_purchase_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found"))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.paid",
                "ch_cancelled_first_purchase",
                customer_name="Talita Gomes Ferreira",
                email="talita@example.com",
                document="12345678900",
                amount=23700,
                created_at=(now - timedelta(hours=2)).isoformat(),
            ))
            engine.handle_event(event(
                "order.canceled",
                "or_cancelled_first_purchase",
                customer_name="Talita Gomes Ferreira",
                email="talita@example.com",
                document="12345678900",
                amount=23700,
                status="canceled",
                created_at=(now - timedelta(hours=1)).isoformat(),
            ))

            result = engine.handle_event(event(
                "charge.paid",
                "ch_second_attempt_after_cancel",
                customer_name="Talita Gomes Ferreira",
                email="talita@example.com",
                document="12345678900",
                amount=23700,
                created_at=now.isoformat(),
            ))

            self.assertTrue(result.first_purchase_alert)

    def test_manually_cancelled_pagarme_charge_does_not_suppress_first_purchase_alert(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(False, None, "not_found"))
            engine = RiskEngine(db.name, history_checker=checker)
            now = datetime.now(timezone.utc)
            engine.handle_event(event(
                "charge.paid",
                "ch_manually_cancelled_first_purchase",
                customer_name="Patrick Pessoa",
                email="patrick@example.com",
                document="12345678900",
                amount=23940,
                created_at=(now - timedelta(hours=2)).isoformat(),
            ))
            with engine._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE antifraud_reviews (
                        charge_id TEXT PRIMARY KEY,
                        decision TEXT NOT NULL,
                        reviewed_at TEXT NOT NULL,
                        reviewed_by TEXT,
                        note TEXT
                    )
                    """
                )
                conn.execute(
                    """
                    INSERT INTO antifraud_reviews (
                        charge_id, decision, reviewed_at, reviewed_by, note
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        "ch_manually_cancelled_first_purchase",
                        "canceled",
                        (now - timedelta(hours=1)).isoformat(),
                        "joao",
                        "venda cancelada pelo Zao",
                    ),
                )

            result = engine.handle_event(event(
                "charge.paid",
                "ch_second_attempt_after_manual_cancel",
                customer_name="Patrick Pessoa",
                email="patrick@example.com",
                document="12345678900",
                amount=23940,
                created_at=now.isoformat(),
            ))

            self.assertTrue(result.first_purchase_alert)
            self.assertFalse(result.customer_history.has_prior_valid_purchase)
            self.assertEqual("not_found", result.customer_history.status)

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

    def test_prior_valid_purchase_suppresses_exact_card_reuse_in_another_customer(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "document",
                "valid_purchase",
                None,
                valid_purchase_count=1,
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            engine.handle_event(event(
                "charge.paid",
                "ch_other_customer_same_card",
                customer_name="Outro Cliente",
                email="outro@example.com",
                document="99988877766",
                holder="OUTRO CLIENTE",
            ))

            result = engine.handle_event(event(
                "charge.paid",
                "ch_returning_same_card",
                customer_name="Cliente Recorrente",
                email="recorrente@example.com",
                document="11122233344",
                holder="CLIENTE RECORRENTE",
            ))

            self.assertFalse(result.alert)
            self.assertEqual(0, result.score)
            self.assertNotIn("cartão", " ".join(result.reasons).lower())

    def test_name_only_history_does_not_suppress_exact_card_reuse(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "name",
                "valid_purchase",
                None,
                valid_purchase_count=2,
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            engine.handle_event(event(
                "charge.paid",
                "ch_name_match_other_customer_same_card",
                customer_name="Outro Cliente",
                email="outro@example.com",
                document="99988877766",
                holder="OUTRO CLIENTE",
            ))

            result = engine.handle_event(event(
                "charge.paid",
                "ch_name_match_returning_same_card",
                customer_name="Cliente Recorrente",
                email="recorrente@example.com",
                document="11122233344",
                holder="CLIENTE RECORRENTE",
            ))

            self.assertTrue(result.alert)
            self.assertGreaterEqual(result.score, 50)
            self.assertIn("dados do cartão", " ".join(result.reasons).lower())

    def test_error_history_flagged_as_prior_purchase_does_not_suppress_exact_card_reuse(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "document",
                "error",
                "timeout",
                valid_purchase_count=1,
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            engine.handle_event(event(
                "charge.paid",
                "ch_error_history_other_customer_same_card",
                customer_name="Outro Cliente",
                email="outro@example.com",
                document="99988877766",
                holder="OUTRO CLIENTE",
            ))

            result = engine.handle_event(event(
                "charge.paid",
                "ch_error_history_returning_same_card",
                customer_name="Cliente Recorrente",
                email="recorrente@example.com",
                document="11122233344",
                holder="CLIENTE RECORRENTE",
            ))

            self.assertTrue(result.alert)
            self.assertEqual(50, result.score)
            reasons = " ".join(result.reasons).lower()
            self.assertIn("dados do cartão", reasons)
            self.assertIn("histórico mogo não validado", reasons)

    def test_untrusted_name_address_history_does_not_suppress_weak_only_alert(self):
        histories = (
            CustomerHistoryResult(True, "name_address", "error", "timeout"),
            CustomerHistoryResult(False, "name_address", "valid_purchase", None),
        )
        for index, history in enumerate(histories):
            with self.subTest(history=history), tempfile.NamedTemporaryFile() as db:
                checker = FakeHistoryChecker(history)
                engine = RiskEngine(db.name, history_checker=checker, hotlist=FraudHotlist.empty())

                result = engine.handle_event(event(
                    "charge.paid",
                    f"ch_untrusted_name_address_weak_{index}",
                    customer_name="Patricia Bernardo",
                    email="contato@example.com",
                    holder="Natalia Nascimento Andrade",
                ))

                self.assertTrue(result.alert)
                self.assertGreaterEqual(result.score, 50)
                self.assertIn("titular diferente", " ".join(result.reasons).lower())

    def test_history_without_match_kind_does_not_suppress_exact_card_reuse_without_identity_fields(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                None,
                "valid_purchase",
                None,
                valid_purchase_count=1,
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            engine.handle_event(event(
                "charge.paid",
                "ch_no_match_kind_other_customer_same_card",
                customer_name="Outro Cliente",
                email="",
                document="",
                holder="OUTRO CLIENTE",
            ))

            result = engine.handle_event(event(
                "charge.paid",
                "ch_no_match_kind_returning_same_card",
                customer_name="Cliente Recorrente",
                email="",
                document="",
                holder="CLIENTE RECORRENTE",
            ))

            self.assertTrue(result.alert)
            self.assertGreaterEqual(result.score, 50)
            self.assertIn("dados do cartão", " ".join(result.reasons).lower())

    def test_unknown_match_kind_does_not_suppress_exact_card_reuse_without_identity_fields(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "legacy_customer_id",
                "valid_purchase",
                None,
                valid_purchase_count=1,
            ))
            engine = RiskEngine(db.name, history_checker=checker)
            engine.handle_event(event(
                "charge.paid",
                "ch_unknown_match_other_customer_same_card",
                customer_name="Outro Cliente",
                email="",
                document="",
                holder="OUTRO CLIENTE",
            ))

            result = engine.handle_event(event(
                "charge.paid",
                "ch_unknown_match_returning_same_card",
                customer_name="Cliente Recorrente",
                email="",
                document="",
                holder="CLIENTE RECORRENTE",
            ))

            self.assertTrue(result.alert)
            self.assertGreaterEqual(result.score, 50)
            self.assertIn("dados do cartão", " ".join(result.reasons).lower())

    def test_prior_valid_purchase_does_not_suppress_known_fraud_address(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "document",
                "valid_purchase",
                None,
                valid_purchase_count=1,
                operational_order=MogoOrderSummary(
                    address="Rua Major Rubens Vaz, 122",
                    neighborhood="Gávea - Rio de Janeiro/RJ",
                ),
            ))
            engine = RiskEngine(db.name, history_checker=checker)

            result = engine.handle_event(event("charge.paid", "ch_returning_fraud_address"))

            self.assertTrue(result.alert)
            self.assertEqual(50, result.score)
            self.assertIn("endereço com fraude anterior", " ".join(result.reasons).lower())

    def test_recurrent_name_only_mogo_customer_does_not_suppress_weak_identity_alerts(self):
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

            self.assertTrue(result.alert)
            self.assertGreaterEqual(result.score, 50)
            reasons = " ".join(result.reasons).lower()
            self.assertIn("titular diferente", reasons)

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

    def test_single_name_only_mogo_purchase_does_not_suppress_checkout_retry_alerts(self):
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

            self.assertTrue(result.alert)
            self.assertGreaterEqual(result.score, 50)
            reasons = " ".join(result.reasons).lower()
            self.assertIn("falha recente", reasons)
            self.assertIn("cartões diferentes", reasons)

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

    def test_hotlisted_alert_shows_large_prior_fraud_list_warning(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(True, "name", "valid_purchase", None))
            hotlist = FraudHotlist.from_customer_documents(["123.456.789-00"])
            engine = RiskEngine(db.name, history_checker=checker, hotlist=hotlist)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_hotlisted_warning",
                customer_name="Cliente Qualquer",
                document="12345678900",
                holder="CLIENTE QUALQUER",
            ))

            alert = format_alert(result)

            self.assertIn("🚨🚨🚨 ATENÇÃO: JÁ CONSTA EM LISTA DE FRAUDADORES ANTERIORES 🚨🚨🚨", alert)
            self.assertIn("HISTÓRICO ANTERIOR DE CHARGEBACK/FRAUDE", alert)
            self.assertIn("NÃO VENDER / NÃO LIBERAR", alert)
            self.assertLess(
                alert.index("JÁ CONSTA EM LISTA DE FRAUDADORES ANTERIORES"),
                alert.index("Status operacional: SEGURAR / NÃO ENTREGAR"),
            )

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

    def test_alert_header_says_mogo_history_found_without_order_number(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "document",
                "valid_purchase",
                None,
                MogoOrderSummary(customer_name="Cliente Recorrente"),
                valid_purchase_count=1,
            ))
            hotlist = FraudHotlist.from_customer_documents(["123"])
            engine = RiskEngine(db.name, history_checker=checker, hotlist=hotlist)
            result = engine.handle_event(event("charge.paid", "ch_history_without_order_number"))

            alert = format_alert(result)

            self.assertIn("HISTÓRICO MOGO: localizado", alert)
            self.assertNotIn("HISTÓRICO MOGO: não localizado", alert)

    def test_alert_header_does_not_say_mogo_history_found_for_error_flagged_as_prior_purchase(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "document",
                "error",
                "timeout",
                MogoOrderSummary(customer_name="Cliente Recorrente"),
                valid_purchase_count=1,
            ))
            hotlist = FraudHotlist.from_customer_documents(["123"])
            engine = RiskEngine(db.name, history_checker=checker, hotlist=hotlist)
            result = engine.handle_event(event("charge.paid", "ch_error_history_without_order_number"))

            alert = format_alert(result)

            self.assertIn("HISTÓRICO MOGO: não localizado", alert)
            self.assertNotIn("HISTÓRICO MOGO: localizado", alert)

    def test_alert_header_does_not_announce_order_number_for_error_history(self):
        with tempfile.NamedTemporaryFile() as db:
            checker = FakeHistoryChecker(CustomerHistoryResult(
                True,
                "document",
                "error",
                "timeout",
                MogoOrderSummary(
                    order_number="039999",
                    customer_name="Cliente Recorrente",
                ),
                valid_purchase_count=1,
            ))
            hotlist = FraudHotlist.from_customer_documents(["123"])
            engine = RiskEngine(db.name, history_checker=checker, hotlist=hotlist)
            result = engine.handle_event(event("charge.paid", "ch_error_history_with_order_number"))

            alert = format_alert(result)

            self.assertIn("HISTÓRICO MOGO: não localizado", alert)
            self.assertNotIn("HISTÓRICO MOGO: pedido #039999", alert)

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

    def test_customer_registry_with_prior_delivery_suppresses_weak_antifraud_alert(self):
        with tempfile.TemporaryDirectory() as root, tempfile.NamedTemporaryFile() as db:
            folder = Path(root) / "Analise Cadastro Clientes"
            folder.mkdir(parents=True)
            (folder / "11-2024.json").write_text(json.dumps({
                "registros": [{
                    "nome": "daniela  vaz",
                    "telefone": "21988955515",
                    "bairro": "Flamengo",
                    "primeiro_pedido": "14/11/2024",
                    "ultimo_pedido": "20/11/2025",
                    "total_pedidos": "1.103,50",
                    "total_delivery": "1.103,50",
                }]
            }), encoding="utf-8")

            checker = LocalMogoHistoryChecker(root)
            engine = RiskEngine(db.name, history_checker=checker)
            result = engine.handle_event(event(
                "charge.paid",
                "ch_returning_customer_registry",
                customer_name="daniela vaz",
                email="juliomtc@uol.com.br",
                document="02410594700",
                phone="21988955515",
                amount=22700,
                holder="JULIO M T COSTA",
                holder_document="02410594700",
            ))

            self.assertFalse(result.alert)
            self.assertEqual(result.score, 0)
            self.assertTrue(result.customer_history.has_prior_valid_purchase)
            self.assertEqual(result.customer_history.matched_by, "phone")

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
