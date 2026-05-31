import unittest
from datetime import date

from automacoes.scripts.mogo_pendentes_alerts import (
    build_overdue_alert_message,
    build_pending_email_body,
    build_pending_email_subject,
    overdue_pending_orders,
)


class MogoPendentesAlertsTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
