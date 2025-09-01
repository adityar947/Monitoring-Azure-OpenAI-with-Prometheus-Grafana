# 📊 Monitoring Azure OpenAI with Prometheus & Grafana

This project demonstrates how to set up monitoring for **Azure OpenAI** usage with **Prometheus** and **Grafana**.  
You’ll be able to track key metrics such as request count, response time, and errors while visualizing them in Grafana dashboards and triggering alerts via Prometheus Alertmanager.

---

## 🚀 Features

- Collect metrics from a FastAPI app exposing Prometheus endpoints.
- Predefined Prometheus alerting rules (alerts.yaml).
Grafana dashboard with:
- p95 Latency
- Error Rate
- Token Usage Split
- Cost per 1k Requests
- Top Users by Cost
- Caching Savings %
- Alerting via Alertmanager (Email/Slack supported).

---

## 🏗️ Architecture
[ FastAPI + Azure OpenAI ]
          │  (metrics: /metrics)
          ▼
     [ Prometheus ]
          │ (scrapes metrics + rules)
          ├──> [ Alertmanager ] → Email/Slack alerts
          ▼
     [ Grafana Dashboard ]

## 📋 Prerequisites

Docker installed on your system

Azure OpenAI service & FastAPI app exporting metrics

Prometheus & Grafana Docker images

---

## 📌 Project Overview

- **Application**: A sample FastAPI app integrated with Azure OpenAI (ChatGPT or embeddings).
- **Monitoring**: Prometheus scrapes metrics exposed by the app and tracks usage.
- **Visualization**: Grafana dashboards display key metrics in real-time.
- **Alerting**: Prometheus Alertmanager sends notifications when thresholds are breached.

---

## 🚀 Setup Instructions

### 1. Clone this Repository
```bash
git clone https://github.com/adityar947/Monitoring-Azure-OpenAI-with-Prometheus-Grafana.git
cd Monitoring-Azure-OpenAI-with-Prometheus-Grafana
```

### 2. Run the FastAPI App
The app exposes `/metrics` endpoint for Prometheus scraping.

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Test the API:
```bash
curl -X POST "http://localhost:8000/ask"      -H "Content-Type: application/json"      -d '{"question":"Hello AI","user":"TestUser"}'
```

### 3. Run Prometheus in Docker
```bash
docker run -d   --name prometheus   -p 9090:9090   -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml   prom/prometheus
```

### 4. Run Grafana in Docker
```bash
docker run -d  --name=grafana   -p 3000:3000   grafana/grafana
```

Login to Grafana → http://localhost:3000 or http://<ip-address>:3000 (default user: `admin`, password: `admin`).

---

## ⚙️ Configuration

### Prometheus Config (`prometheus.yml`)
```yaml
global:
  scrape_interval: 15s

rule_files:
  - "alerts.yml"

scrape_configs:
  - job_name: "fastapi-openai"
    static_configs:
      - targets: ["host.docker.internal:8000"]
```

### Alerts Config (`alerts.yml`)
```yaml
groups:
  - name: openai-alerts
    rules:
      - alert: HighRequestRate
        expr: rate(app_requests_total[1m]) > 20
        for: 1m
        labels:
          severity: warning
        annotations:
          description: "High request rate detected"
          summary: "The app is receiving too many requests"
```

Run Prometheus with alerts enabled:
```bash
docker run -d   --name prometheus   -p 9090:9090   -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml   -v $(pwd)/alerts.yml:/etc/prometheus/alerts.yml   prom/prometheus
```

---

## 📊 Grafana Dashboard

- Import the provided `grafana-dashboard.json` in Grafana.
- It includes panels for:
  - 95th Percentile Latency (Gauge)
  - Error Rate (Gauge)
  - Token Usage Split (Pie Chart)
  - Cost per 1k Requests (Stat)
  - Top 3 Users by Cost (Bar Chart)
  - Caching Savings % (Gauge)

---

## 🔍 Usage

Start FastAPI app (with /metrics endpoint).

Run Prometheus + Grafana containers.

Import the dashboard JSON into Grafana.

Check Prometheus UI at http://localhost:9090

Monitor metrics in Grafana at http://localhost:3000

---

## 🔔 Alerting

To enable notifications, configure **Prometheus Alertmanager** and connect it with Slack, Email, or Teams. Example:

```bash
docker run -d   --name alertmanager   -p 9093:9093   -v $(pwd)/alertmanager.yml:/etc/alertmanager/alertmanager.yml   prom/alertmanager
```

---

## 📦 Project Structure
```
.
├── app.py                 # FastAPI app with Azure OpenAI integration
├── metrics.py             # Metrics for FastAPI
├── prometheus.yml         # Prometheus config
├── alerts.yml             # Prometheus alert rules
├── fastapi-openai-dashboard.json # Grafana dashboard export
└── README.md              # Project documentation
```

---

## 📸 Screenshots

<img alt="Grafana Dasboard" src="https://github.com/adityar947/Monitoring-Azure-OpenAI-with-Prometheus-Grafana/blob/main/cover.png">

---

## 🤝 Contributing
- Pull requests welcome! For major changes, please open an issue first.

---

## 📝 License
This project is licensed under the MIT License.
