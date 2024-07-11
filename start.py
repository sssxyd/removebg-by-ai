import os

import psutil
from uvicorn import run
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    port_str = os.environ.get('HTTP_SERVER_PORT')
    port = int(port_str) if port_str else 10086
    workers_str = os.environ.get('UVICORN_WORKERS')
    logical_cores = int(workers_str) if workers_str else psutil.cpu_count(logical=True)
    run(app="server:app", host="0.0.0.0", port=port, workers=logical_cores)
    input("...exit with enter")
