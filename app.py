import os
import time
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import Counter, Histogram, Gauge
from fastapi.responses import HTMLResponse

from metrics import (
    REQUEST_COUNTER, ERROR_COUNTER, TOKEN_COUNTER, REQUEST_LATENCY,
    COST_COUNTER, PROMPT_TOKEN_COUNTER, COMPLETION_TOKEN_COUNTER,
    USER_COST_COUNTER, CACHE_SAVINGS_GAUGE, OPENAI_REQUESTS_BY_USER
)

# Load environment variables


AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_API_KEY"]
DEPLOYMENT_NAME = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
API_VERSION = "2024-12-01-preview"
# FastAPI app
app = FastAPI(title="Azure OpenAI FastAPI Service with Metrics")

# Pricing (per 1K tokens)
PROMPT_RATE = 0.0015
COMPLETION_RATE = 0.002


@app.post("/ask")
async def ask(request: Request):
    payload = await request.json()
    question = payload.get("question")
    user = payload.get("user", "anonymous")  # Track cost by user/team

    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question' field")

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_KEY,
    }

    data = {
        "messages": [{"role": "user", "content": question}],
        "max_tokens": 500,
    }

    url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"

    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=data)
        latency = time.time() - start_time
        REQUEST_LATENCY.observe(latency)

        if response.status_code != 200:
            ERROR_COUNTER.inc()
            raise HTTPException(status_code=response.status_code, detail=response.text)

        resp_json = response.json()
        REQUEST_COUNTER.inc()
        OPENAI_REQUESTS_BY_USER.labels(user=user).inc()

        # Extract answer & usage
        answer = resp_json["choices"][0]["message"]["content"]
        usage = resp_json.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

        # Cost calculation
        prompt_cost = (prompt_tokens / 1000) * PROMPT_RATE
        completion_cost = (completion_tokens / 1000) * COMPLETION_RATE
        total_cost = prompt_cost + completion_cost

        # Update Prometheus metrics
        TOKEN_COUNTER.inc(total_tokens)
        PROMPT_TOKEN_COUNTER.inc(prompt_tokens)
        COMPLETION_TOKEN_COUNTER.inc(completion_tokens)
        COST_COUNTER.inc(total_cost)
        USER_COST_COUNTER.labels(user=user).inc(total_cost)

        # Simulated caching savings (e.g., cache hit ratio)
        CACHE_SAVINGS_GAUGE.set(0.18)  # 18% savings as per your metric

        return JSONResponse(
            content={
                "answer": answer,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                },
                "latency": round(latency, 3),
                "cost": round(total_cost, 6),
            }
        )

    except Exception as e:
        ERROR_COUNTER.inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>Ask OpenAI</title></head>
        <body style="font-family: Arial; margin: 20px;">
            <h2>Ask a Question</h2>
            <form id="askForm">
                <label>Question:</label><br>
                <textarea id="question" rows="4" cols="50"></textarea><br><br>
                <label>User:</label><br>
                <input type="text" id="user" value="anonymous"><br><br>
                <button type="submit">Ask</button>
            </form>
            <h3>Response:</h3>
            <pre id="response"></pre>

            <script>
            document.getElementById("askForm").onsubmit = async (e) => {
                e.preventDefault();
                const question = document.getElementById("question").value;
                const user = document.getElementById("user").value;

                const res = await fetch("/ask", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question, user })
                });

                const data = await res.json();
                document.getElementById("response").innerText = JSON.stringify(data, null, 2);
            }
            </script>
        </body>
    </html>
    """
