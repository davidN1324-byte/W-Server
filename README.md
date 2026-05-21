# W-Server

A lightweight file exchange server for local networks.  
Upload, download, and delete files via a browser interface.

---

## Requirements

- Python 3.10+ (local) or Docker

---

## Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/davidN1324-byte/W-Server.git
cd W-Server

# 2. Install system dependency (Linux)
sudo apt install libmagic1

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn app.main:app --host 0.0.0.0 --port 5000
```

Open in browser: `http://localhost:5000`

---

## Run with Docker

```bash
# 1. Build the image
docker build -t w-server .

# 2. Run the container
docker run -d -p 5000:5000 --name w-server w-server
```

Open in browser: `http://localhost:5000`

> To persist uploaded files between container restarts, mount a volume:
>
> ```bash
> docker run -d -p 5000:5000 -v $(pwd)/uploads:/app/uploads --name w-server w-server
> ```

---

## Configuration

```json
| Variable | Default | Description |
|---|---|---|
| `MAX_CONTENT_LENGTH` | 100 MB | Max upload file size |
| `ALLOWED_EXTENSIONS` | txt, pdf, png, jpg, jpeg, gif | Allowed file types |
```

---

## SSL (optional)

Place your certificates in the `Cert/` folder and start with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 \
  --ssl-keyfile Cert/key.pem \
  --ssl-certfile Cert/cert.pem
```
