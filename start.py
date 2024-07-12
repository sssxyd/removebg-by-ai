import os
import sys
import webbrowser

import psutil
from uvicorn import run
from dotenv import load_dotenv
import server


if sys.platform == "win32":
    os.system('chcp 65001')

if __name__ == "__main__":
    load_dotenv()
    port_str = os.environ.get('HTTP_SERVER_PORT')
    port = int(port_str) if port_str else 10086
    workers_str = os.environ.get('UVICORN_WORKERS')
    physical_cores = int(workers_str) if workers_str else psutil.cpu_count(logical=False)

    run(app="server:app", host="0.0.0.0", port=port, workers=physical_cores)

    if sys.platform == "win32":
        webbrowser.open(f"http://localhost:{port}")

    input("...exit with enter")
