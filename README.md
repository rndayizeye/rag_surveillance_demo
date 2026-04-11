---
title: RAG Surveillance Demo
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.43.0"
python_version: "3.11"
app_file: app.py
pinned: false
---

# STI Surveillance (RAG)

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

![App Screenshot](https://private-user-images.githubusercontent.com/66800883/576983211-d5d9ba26-18e0-43b1-871a-c2225ac4dcac.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NzU5MzA4NzEsIm5iZiI6MTc3NTkzMDU3MSwicGF0aCI6Ii82NjgwMDg4My81NzY5ODMyMTEtZDVkOWJhMjYtMThlMC00M2IxLTg3MWEtYzIyMjVhYzRkY2FjLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNjA0MTElMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjYwNDExVDE4MDI1MVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTNlMDU0YmVlMmVjYWVjNTgyNDYzNjRmNTI5N2YwY2Y1OWQ4MjNkMGJmYmJkMjczYzEwYzdhZmIyNWM5ZGQ4ODQmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnJlc3BvbnNlLWNvbnRlbnQtdHlwZT1pbWFnZSUyRnBuZyJ9.ryGL3Tffw6SRTWHcHG0uEcctgrx1DHJbby5Z6Y3YaKY)

This project aims to develop a demo of a RAG implementation for our STI surveillance program using a Streamlit app. It will integrate guidelines from manuals and CDC with unique instructions. Built in a Docker container, I'll document my progress on GitHub, showcasing my learning journey in programming.

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         sti_surveillance_rag and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── sti_surveillance_rag   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes sti_surveillance_rag a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

