import re
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "relatorio-marketing-automático.sh"


class RelatorioMarketingAutomaticoTest(unittest.TestCase):
    def test_exports_1password_service_account_token_before_output(self):
        lines = SCRIPT.read_text(encoding="utf-8").splitlines()

        set_e_index = lines.index("set -e")
        first_echo_index = next(i for i, line in enumerate(lines) if line.startswith("echo "))
        export_pattern = re.compile(
            r"export OP_SERVICE_ACCOUNT_TOKEN=\$\(cat /root/\.openclaw/credentials/1password-token\.txt\)"
        )
        export_indexes = [i for i, line in enumerate(lines) if export_pattern.fullmatch(line)]

        self.assertEqual(1, len(export_indexes))
        export_index = export_indexes[0]
        self.assertLess(set_e_index, export_index)
        self.assertLess(export_index, first_echo_index)


if __name__ == "__main__":
    unittest.main()
