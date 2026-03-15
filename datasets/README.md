# Datasets

Download these datasets and place the CSV files in this folder.

| Dataset | Link |
|---|---|
| AWS Honeypot Attack Data | https://www.kaggle.com/datasets/casimian2000/aws-honeypot-attack-data |
| CIC Honeynet Dataset | https://www.honeynetproject.com/dataset.html |
| Hornet 40 Dataset | https://data.mendeley.com/datasets/tcfzkbpw46/3 |
| Dionaea Honeypot Dataset | https://www.kaggle.com/datasets/startingsecurity/cybersecurity-honeypot-attacks |

After downloading, place `aws_honeypot_marx_geo.csv` in this folder
and run `python scripts/train_all_models.py`.
```

---

## Final GitHub Checklist
```
✅ README.md              — professional, complete
✅ .env.example           — shows required keys
✅ requirements.txt       — all Python deps
✅ docker-compose.yml     — Kafka setup
✅ datasets/README.md     — dataset download links
✅ models/ folder         — add .gitkeep file
✅ .gitignore             — exclude venv, .env, models
```

Create `.gitignore`:
```
venv/
.env
__pycache__/
*.pyc
models/*.pkl
models/*.keras
datasets/*.csv
node_modules/
dashboard/.next/
.DS_Store