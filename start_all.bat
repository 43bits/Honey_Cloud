@echo off
echo Starting HoneyCloud Sentinel...

echo [1/4] Starting Kafka...
start "Kafka" cmd /k "docker-compose up"

timeout /t 15 /nobreak

echo [2/4] Starting API...
start "FastAPI" cmd /k "cd /d F:\CyberSecurity\honeycloud && venv\Scripts\activate && uvicorn api.threat_api:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak

echo [3/4] Starting Honeypot...
start "Honeypot" cmd /k "cd /d F:\CyberSecurity\honeycloud && venv\Scripts\activate && python -m honeypots.ssh_honeypot"

timeout /t 3 /nobreak

echo [4/4] Starting Dashboard...
start "Dashboard" cmd /k "cd /d F:\CyberSecurity\honeycloud\dashboard && npm run dev"

echo.
echo All services started. Open http://localhost:3000
pause