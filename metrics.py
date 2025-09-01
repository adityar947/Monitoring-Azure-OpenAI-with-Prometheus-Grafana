from prometheus_client import Counter, Histogram, Gauge

# Basic request metrics
REQUEST_COUNTER = Counter("openai_requests_total", "Total number of OpenAI requests")
ERROR_COUNTER = Counter("openai_errors_total", "Total number of OpenAI request errors")
TOKEN_COUNTER = Counter("openai_tokens_total", "Total tokens used")
PROMPT_TOKEN_COUNTER = Counter("openai_prompt_tokens_total", "Prompt tokens used")
COMPLETION_TOKEN_COUNTER = Counter("openai_completion_tokens_total", "Completion tokens used")
COST_COUNTER = Counter("openai_cost_total", "Total estimated cost in USD")

# Request latency histogram
REQUEST_LATENCY = Histogram(
    "openai_request_latency_seconds",
    "Latency of OpenAI requests",
    buckets=[0.5, 1, 2, 3, 5, 10],
)

# Per-user/team cost tracking
USER_COST_COUNTER = Counter("openai_user_cost_total", "Total cost per user/team", ["user"])

# Cache savings gauge
CACHE_SAVINGS_GAUGE = Gauge("openai_cache_savings_ratio", "Fraction of tokens saved due to caching")

# Request Success Ratio Gauge
OPENAI_SUCCESS_RATIO = Gauge(
    "openai_success_ratio",
    "Ratio of successful to total requests"
)

# Rate Limit Counter
OPENAI_RATE_LIMITED = Counter(
    "openai_rate_limited_total",
    "Number of requests rejected due to rate limits"
)

# Requests per User
OPENAI_REQUESTS_BY_USER = Counter(
    "openai_requests_by_user_total",
    "Number of requests grouped by user/team",
    ["user"]
)

openai_response_latency_seconds = Histogram(
    "openai_response_latency_seconds",
    "Latency of OpenAI API responses in seconds",
    buckets=[0.1, 0.5, 1, 2, 5, 10]  # you can tune this
)
