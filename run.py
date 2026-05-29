import argparse
import os
import secrets
import base64
from pathlib import Path
from dotenv import load_dotenv


def generate_if_missing():
    env_path = Path(".env")

    if not env_path.exists():
        env_path.write_text("")

    content = env_path.read_text()
    lines = content.splitlines()
    updated = False

    def get_val(key):
        for line in lines:
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
        return ""

    def set_val(key, value):
        nonlocal lines, updated
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                if not line.split("=", 1)[1].strip():
                    lines[i] = f"{key}={value}"
                    updated = True
                return
        lines.append(f"{key}={value}")
        updated = True

    # ACCESS_TOKEN
    if not get_val("ACCESS_TOKEN"):
        token = secrets.token_hex(32)
        set_val("ACCESS_TOKEN", token)
        print(f"[AUTO] Generated ACCESS_TOKEN: {token}")

    # ENCRYPTION_KEY
    if not get_val("ENCRYPTION_KEY"):
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        key = AESGCM.generate_key(bit_length=256)
        enc_key = base64.urlsafe_b64encode(key).decode()
        set_val("ENCRYPTION_KEY", enc_key)
        print(f"[AUTO] Generated ENCRYPTION_KEY: {enc_key}")

    if updated:
        env_path.write_text("\n".join(lines) + "\n")
        print("[AUTO] Keys saved to .env")


def main():
    generate_if_missing()
    load_dotenv(dotenv_path=Path(".env"))

    parser = argparse.ArgumentParser(description="W-Server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--token", help="Override ACCESS_TOKEN from .env")
    parser.add_argument("--ssl-keyfile", default="Cert/key.pem")
    parser.add_argument("--ssl-certfile", default="Cert/cert.pem")
    parser.add_argument("--no-ssl", action="store_true", help="Disable SSL")
    args = parser.parse_args()

    if args.token:
        os.environ["ACCESS_TOKEN"] = args.token
        print(f"[MANUAL] Using token: {args.token}")

    import uvicorn

    ssl_keyfile = None
    ssl_certfile = None

    if not args.no_ssl:
        if os.path.exists(args.ssl_keyfile) and os.path.exists(args.ssl_certfile):
            ssl_keyfile = args.ssl_keyfile
            ssl_certfile = args.ssl_certfile
        else:
            print(f"WARNING: SSL certs not found, starting without SSL (HTTP only)")

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
    )


if __name__ == "__main__":
    main()