# Fusion-Repo

This repository is an automatic fusion of the following projects:
- [mannomannX/website-analyzer-dashboard](https://github.com/mannomannX/website-analyzer-dashboard)
- [mannomannX/website-analyzer-api](https://github.com/mannomannX/website-analyzer-api)

Last update: Sat Jul  5 15:00:31 UTC 2025


# Project-Tree

├── .github/
│   └── workflows/
│       └── sync.yml
├── README.md
├── website-analyzer-api/
│   ├── .github/
│   │   └── workflows/
│   │       └── monomono-trigger.yml
│   ├── .gitignore
│   ├── app/
│   │   ├── init.py
│   │   ├── pycache/
│   │   │   ├── init.cpython-311.pyc
│   │   │   └── main.cpython-311.pyc
│   │   ├── api/
│   │   │   ├── init.py
│   │   │   ├── pycache/
│   │   │   │   ├── init.cpython-311.pyc
│   │   │   │   └── dependencies.cpython-311.pyc
│   │   │   ├── dependencies.py
│   │   │   └── routes/
│   │   │       ├── pycache/
│   │   │       │   ├── analysis.cpython-311.pyc
│   │   │       │   └── auth.cpython-311.pyc
│   │   │       ├── admin.py
│   │   │       ├── analysis.py
│   │   │       └── auth.py
│   │   ├── core/
│   │   │   ├── init.py
│   │   │   ├── pycache/
│   │   │   │   ├── init.cpython-311.pyc
│   │   │   │   ├── analyzer.cpython-311.pyc
│   │   │   │   ├── confidence_scorer.cpython-311.pyc
│   │   │   │   ├── config.cpython-311.pyc
│   │   │   │   ├── crawler.cpython-311.pyc
│   │   │   │   ├── page_classifier.cpython-311.pyc
│   │   │   │   ├── parser.cpython-311.pyc
│   │   │   │   └── security.cpython-311.pyc
│   │   │   ├── analyzer.py
│   │   │   ├── confidence_scorer.py
│   │   │   ├── config.py
│   │   │   ├── crawler.py
│   │   │   ├── page_classifier.py
│   │   │   ├── parser.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── init.py
│   │   │   ├── pycache/
│   │   │   │   ├── init.cpython-311.pyc
│   │   │   │   ├── database.cpython-311.pyc
│   │   │   │   └── models.cpython-311.pyc
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── main.py
│   │   ├── schemas/
│   │   │   ├── init.py
│   │   │   ├── pycache/
│   │   │   │   ├── init.cpython-311.pyc
│   │   │   │   ├── analysis.cpython-311.pyc
│   │   │   │   └── token.cpython-311.pyc
│   │   │   ├── analysis.py
│   │   │   ├── token.py
│   │   │   └── user.py
│   │   └── worker/
│   │       ├── init.py
│   │       ├── pycache/
│   │       │   ├── init.cpython-311.pyc
│   │       │   ├── celery_app.cpython-311.pyc
│   │       │   └── tasks.cpython-311.pyc
│   │       ├── celery_app.py
│   │       └── tasks.py
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   ├── README.md
│   ├── requirements.txt
│   └── scripts/
│       └── create_admin_user.py
└── website-analyzer-dashboard/
├── .github/
│   └── workflows/
│       └── monomono-trigger.yml
└── website-analyzer-dashboard/
├── .gitignore
├── eslint.config.js
├── index.html
├── package-lock.json
├── package.json
├── public/
│   └── vite.svg
├── README.md
├── src/
│   ├── api/
│   │   └── apiClient.js
│   ├── App.css
│   ├── App.jsx
│   ├── assets/
│   │   └── react.svg
│   ├── index.css
│   ├── main.jsx
│   └── pages/
│       └── LoginPage.jsx
└── vite.config.js
