# scripts/demo_cheatsheet.py
"""
╔══════════════════════════════════════════════════════╗
║         HONEYCLOUD DEMO CHEATSHEET                   ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  BEFORE ARRIVE:                                      ║
║  1. docker-compose up -d                             ║
║  2. uvicorn api.threat_api:app --reload              ║
║  3. cd dashboard && npm run dev                      ║
║  4. Open http://localhost:3000 on projector          ║
║                                                      ║
║  DURING LIVE:                                        ║
║  Full demo (3 min):  python scripts/demo.py          ║
║  Quick demo (30s):   python scripts/demo.py --quick  ║
║  Reset dashboard:    curl -X DELETE                  ║
║                      http://localhost:8000/attacks/  ║
║                      clear                           ║
║                                                      ║
║  IF SOMETHING BREAKS:                                ║
║  • Restart API:   Ctrl+C → uvicorn api...            ║
║  • Reset data:    curl -X DELETE localhost:8000/     ║
║                   attacks/clear                      ║
║  • Kafka down:    docker-compose restart kafka       ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
"""
print(__doc__)