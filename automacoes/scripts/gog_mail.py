import os
import subprocess


def send_gmail(*, account, client, to, subject, body, attach=None, env=None):
    send_env = os.environ.copy()
    if env:
        send_env.update(env)
    send_env["GOG_KEYRING_PASSWORD"] = ""

    cmd = [
        "gog",
        "gmail",
        "send",
        "--account",
        account,
        "--client",
        client,
        "--to",
        to,
        "--subject",
        subject,
        "--body",
        body,
    ]
    if attach:
        cmd.extend(["--attach", attach])

    return subprocess.run(cmd, capture_output=True, text=True, env=send_env)
