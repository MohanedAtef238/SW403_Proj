import subprocess
import os
import sys
import signal

def run_dev():
    """Run both backend and frontend concurrently."""
    print("Starting RAG Pipeline Development Servers...")

    # Start Backend
    backend_process = subprocess.Popen(
        ["uv", "run", "uvicorn", "src.api.main:app", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
        shell=True
    )

    # Start Frontend
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=os.path.join(os.getcwd(), "src", "frontend"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
        shell=True
    )

    def print_output(process, prefix):
        for line in iter(process.stdout.readline, ""):
            print(f"[{prefix}] {line.strip()}")

    import threading
    
    t1 = threading.Thread(target=print_output, args=(backend_process, "BACKEND"))
    t2 = threading.Thread(target=print_output, args=(frontend_process, "FRONTEND"))
    
    t1.start()
    t2.start()

    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    run_dev()
