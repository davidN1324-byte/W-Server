import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    ssl_certfile = os.getenv("SSL_CERTFILE", "Cert/cert.pem")
    ssl_keyfile = os.getenv("SSL_KEYFILE", "Cert/key.pem")

    uvicorn.run(app, 
                host="0.0.0.0", 
                port=5000, 
                ssl_certfile=ssl_certfile, 
                ssl_keyfile=ssl_keyfile)