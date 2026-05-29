# W-Server

A lightweight file exchange server for local networks.  
Upload, download, and delete files via a browser interface.  
Files are encrypted at rest using AES-256-GCM.

---

## Requirements

- Python 3.10+ (local) or Docker

---

## Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/davidN1324-byte/W-Server.git
cd W-Server

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set your ACCESS_TOKEN and ENCRYPTION_KEY

# 4. Generate ACCESS_TOKEN
python3 -c "import secrets; print('ACCESS_TOKEN=' + secrets.token_hex(32))"

# 5. Generate ENCRYPTION_KEY (AES-256)
python3 -c "
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
key = AESGCM.generate_key(bit_length=256)
print('ENCRYPTION_KEY=' + base64.urlsafe_b64encode(key).decode())
"

# 6. Start the server
python3 run.py
```

Open in browser: `https://localhost:5000`

---

## Run with Docker

```bash
# 1. Build the image
docker build -t w-server .

# 2. Run the container
docker run -d -p 5000:5000 --env-file .env --name w-server w-server
```

Open in browser: `https://localhost:5000`

> To persist uploaded files between container restarts, mount a volume:
>
> ```bash
> docker run -d -p 5000:5000 --env-file .env \
>   -v $(pwd)/uploads:/app/uploads \
>   --name w-server w-server
> ```

Or with Docker Compose:

```bash
docker compose up -d
```

---

## CLI Options

```json
python3 run.py [OPTIONS]

  --host           Bind address              (default: 0.0.0.0)
  --port           Port                      (default: 5000)
  --token          Override ACCESS_TOKEN from .env
  --ssl-keyfile    Path to key.pem           (default: Cert/key.pem)
  --ssl-certfile   Path to cert.pem          (default: Cert/cert.pem)
  --no-ssl         Disable SSL, run over HTTP
```

Examples:

```bash
# Token from .env, SSL auto-detected from Cert/
python3 run.py

# Custom token, SSL auto-detected
python3 run.py --host 192.168.1.100 --port 8443 --token my_secret_token

# Without SSL (HTTP only)
python3 run.py --host 192.168.1.100 --port 5000 --token my_secret_token --no-ssl
```

> If `Cert/key.pem` and `Cert/cert.pem` are present, SSL is enabled automatically.  
> Use `--no-ssl` to force HTTP regardless of certificates.

---

## Configuration

All settings are loaded from `.env`:

| Variable              | Default                                    | Description                        |
|-----------------------|--------------------------------------------|------------------------------------|
| `ACCESS_TOKEN`        | —                                          | Required. Auth token               |
| `ENCRYPTION_KEY`      | —                                          | Required. AES-256 encryption key   |
| `MAX_CONTENT_LENGTH`  | `104857600` (100 MB)                       | Max upload file size               |
| `ALLOWED_EXTENSIONS`  | `txt,pdf,png,jpg,jpeg,gif`                 | Allowed file extensions            |
| `ALLOWED_MIMES`       | `text/plain,application/pdf,image/png,...` | Allowed MIME types                 |
| `MAX_CONNECTIONS`     | `10`                                       | Max simultaneous connections       |
| `FILE_TTL_HOURS`      | `0` (disabled)                             | Auto-delete files after N hours    |
| `PORT`                | `5000`                                     | Server port                        |

---

## SSL

Generate a self-signed certificate:

```bash
mkdir Cert
openssl req -x509 -newkey rsa:4096 \
  -keyout Cert/key.pem -out Cert/cert.pem \
  -days 365 -nodes -subj "/CN=w-server"
```

Certificates are loaded automatically from `Cert/` on startup.  
The browser will show a warning for self-signed certs — this is expected.

---

## Security

- All files are encrypted at rest using **AES-256-GCM**
- Traffic is encrypted via **HTTPS/TLS**
- Access is protected by a **token** passed in `X-Access-Token` header
- Rate limiting on all endpoints
- Path traversal protection on download and delete

> **Important:** keep your `ENCRYPTION_KEY` safe. If lost, encrypted files cannot be recovered.

---

## Logs

Logs are written to `logs/server.log` and printed to console simultaneously.  
The active `ACCESS_TOKEN` (first 6 chars) is printed once at startup.
