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
    worker_count = int(os.environ.get('UVICORN_WORKERS'))
    if worker_count <= 0:
        cpu_cores = psutil.cpu_count(logical=False)
        if cpu_cores and int(cpu_cores) > 0:
            worker_count = int(cpu_cores)
    if worker_count <= 0:
        worker_count = 1
    run(app="server:app", host="0.0.0.0", port=port, workers=worker_count)

    input("...exit with enter")
