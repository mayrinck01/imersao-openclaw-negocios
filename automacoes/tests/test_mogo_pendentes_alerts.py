import unittest
from datetime import date

from automacoes.scripts.mogo_pendentes_alerts import (
    CAKE_ATENDIMENTO_GROUP,
    EXPEDICAO_CAKE_GROUP,
    build_critical_address_alert_message,
    build_overdue_alert_message,
    build_pending_email_body,
    build_pending_email_subject,
    critical_delivery_address_orders,
    overdue_pending_orders,
    send_whatsapp_group_alerts,
    sort_pending_orders,
    unseen_critical_address_orders,
)


class MogoPendentesAlertsTests(unittest.TestCase):
    def test_sort_pending_orders_uses_real_delivery_date_before_june_dates(self):
        pedidos = [
            {"NumeroPedido": "040100", "DataEntrega": "02/06/2026", "HoraEntregaTxt": "10:00"},
            {"NumeroPedido": "039814", "DataEntrega": "31/05/2026", "HoraEntregaTxt": "19:00"},
            {"NumeroPedido": "040050", "DataEntrega": "01/06/2026", "HoraEntregaTxt": "09:00"},
        ]

        ordenados = sort_pending_orders(pedidos)

        self.assertEqual(
            [pedido["NumeroPedido"] for pedido in ordenados],
            ["039814", "040050", "040100"],
        )

    def test_overdue_pending_orders_detects_delivery_before_today(self):
        pedidos = [
            {
                "NumeroPedido": "039814",
                "NomeCliente": "Cliente A",
                "DataEntrega": "30/05/2026",
                "HoraEntregaTxt": "19:00",
            },
            {
                "NumeroPedido": "039900",
                "NomeCliente": "Cliente B",
                "DataEntrega": "31/05/2026",
                "HoraEntregaTxt": "10:00",
            },
        ]

        atrasados = overdue_pending_orders(pedidos, today=date(2026, 5, 31))

        self.assertEqual([p["NumeroPedido"] for p in atrasados], ["039814"])

    def test_critical_delivery_address_detects_euclides_da_cunha_106_any_customer_name(self):
        pedidos = [
            {
                "NumeroPedido": "044100",
                "NomeCliente": "Cliente Qualquer",
                "DataEntrega": "18/06/2026",
                "HoraEntregaTxt": "18:00",
                "Logradouro": "Rua Euclides Da Cunha",
                "Numero": "106",
                "Bairro": "São Cristóvão",
            },
            {
                "NumeroPedido": "044101",
                "NomeCliente": "Outro Cliente",
                "DataEntrega": "18/06/2026",
                "HoraEntregaTxt": "18:30",
                "Logradouro": "Rua Euclides Da Cunha",
                "Numero": "160",
                "Bairro": "São Cristóvão",
            },
        ]

        criticos = critical_delivery_address_orders(pedidos)

        self.assertEqual([pedido["NumeroPedido"] for pedido in criticos], ["044100"])

    def test_critical_address_alert_message_tells_operation_to_hold_delivery(self):
        message = build_critical_address_alert_message(
            [
                {
                    "NumeroPedido": "044100",
                    "NomeCliente": "Cliente Qualquer",
                    "DataEntrega": "18/06/2026",
                    "HoraEntregaTxt": "18:00",
                    "Logradouro": "Rua Euclides Da Cunha",
                    "Numero": "106",
                    "Bairro": "São Cristóvão",
                    "ValorFinal": "120,00",
                    "StatusPago": "Sim",
                }
            ],
            today_label="18/06/2026",
        )

        self.assertIn("ALERTA GRANDE Mogo", message)
        self.assertIn("endereço com fraude anterior", message)
        self.assertIn("Rua Euclides da Cunha, 106", message)
        self.assertIn("#044100", message)
        self.assertIn("SEGURAR / NÃO ENTREGAR", message)

    def test_unseen_critical_address_orders_filters_already_alerted_order_keys(self):
        pedidos = [
            {
                "NumeroPedido": "044100",
                "Logradouro": "Rua Euclides Da Cunha",
                "Numero": "106",
            },
            {
                "NumeroPedido": "044101",
                "Logradouro": "Rua Euclides Da Cunha",
                "Numero": "106",
            },
        ]

        unseen = unseen_critical_address_orders(pedidos, seen_keys={"044100|rua euclides da cunha 106"})

        self.assertEqual([pedido["NumeroPedido"] for pedido in unseen], ["044101"])

    def test_pending_email_subject_flags_overdue_orders(self):
        subject = build_pending_email_subject(
            total=31,
            today_label="31-05-2026",
            overdue_count=1,
        )

        self.assertIn("ALERTA", subject)
        self.assertIn("1 atrasado", subject)
        self.assertIn("31 pedido(s)", subject)

    def test_pending_email_body_puts_overdue_block_before_schedule(self):
        pedidos = [
            {
                "NumeroPedido": "039814",
                "NomeCliente": "Cliente A",
                "DataEntrega": "30/05/2026",
                "HoraEntregaTxt": "19:00",
                "Bairro": "Leblon",
                "ValorFinal": "31,35",
                "StatusPago": "Sim",
            },
        ]
        body = build_pending_email_body(
            pedidos=pedidos,
            grouped_by_date_hour={"30/05/2026": {"19:00": pedidos}},
            today_label="31-05-2026",
            overdue_orders=pedidos,
        )

        self.assertLess(body.index("PENDENTES ATRASADOS"), body.index("30/05/2026"))
        self.assertIn("#039814", body)
        self.assertIn("Pago: Sim", body)

    def test_overdue_alert_message_is_suitable_for_telegram(self):
        message = build_overdue_alert_message(
            [
                {
                    "NumeroPedido": "039814",
                    "NomeCliente": "Cliente A",
                    "DataEntrega": "30/05/2026",
                    "HoraEntregaTxt": "19:00",
                    "ValorFinal": "31,35",
                    "StatusPago": "Sim",
                }
            ],
            today_label="31/05/2026",
        )

        self.assertIn("ALERTA Mogo", message)
        self.assertIn("pendente(s) com entrega vencida", message)
        self.assertIn("#039814", message)
        self.assertIn("30/05/2026 19:00", message)

    def test_send_whatsapp_group_alerts_posts_to_atendimento_and_expedicao(self):
        calls = []

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b'{"ok": true}'

        def fake_opener(req, timeout=30):
            calls.append((req.full_url, req.data.decode("utf-8"), dict(req.header_items())))
            return FakeResponse()

        results = send_whatsapp_group_alerts(
            "mensagem teste",
            base_url="http://evolution.local",
            instance="cake-interno",
            api_key="fake-key",
            opener=fake_opener,
        )

        self.assertEqual([result["target"] for result in results], [CAKE_ATENDIMENTO_GROUP, EXPEDICAO_CAKE_GROUP])
        self.assertTrue(all(result["ok"] for result in results))
        self.assertEqual(
            [call[0] for call in calls],
            [
                "http://evolution.local/message/sendText/cake-interno",
                "http://evolution.local/message/sendText/cake-interno",
            ],
        )
        self.assertIn(CAKE_ATENDIMENTO_GROUP, calls[0][1])
        self.assertIn(EXPEDICAO_CAKE_GROUP, calls[1][1])
        self.assertIn("mensagem teste", calls[0][1])


if __name__ == "__main__":
    unittest.main()
