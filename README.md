# E-Commerce Microservices Platform

A robust, scalable e-commerce platform built using microservices architecture with Python FastAPI.

## 🌟 Features

- **Customer Management**
  - User profiles and authentication
  - Wallet system for transactions
  - Customer analytics

- **Inventory Management**
  - Product catalog
  - Stock tracking
  - Category management

- **Sales Processing**
  - Order management
  - Transaction handling
  - Purchase history

- **Reviews System**
  - Product reviews
  - Rating system
  - Moderation capabilities

- **Analytics Service**
  - Sales metrics
  - Customer insights
  - Inventory analytics

## 🏗️ Architecture

The platform consists of several microservices:

```python:docker-compose.yml
startLine: 3
startLine: 72
```

Each service is containerized and can be scaled independently. The system uses:

- PostgreSQL for persistent storage
- Redis for caching
- HAProxy for load balancing
- Prometheus & Grafana for monitoring

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- PostgreSQL 13+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ecommerce-microservices.git
cd ecommerce-microservices
```

2. Create environment files:
```bash
cp .env.example .env
```

3. Start the services:
```bash
docker-compose up -d
```

The services will be available at:
- Customer Service: `http://localhost:8000`
- Inventory Service: `http://localhost:8001`
- Sales Service: `http://localhost:8002`
- Auth Service: `http://localhost:8003`
- Analytics Service: `http://localhost:8004`
- Monitoring (Grafana): `http://localhost:3000`

## 🔧 Configuration

### Database Setup

The database initialization scripts are located in:


```1:7:database/init/01_create_databases.sql
-- Create databases
CREATE DATABASE customer_db;
CREATE DATABASE inventory_db;
CREATE DATABASE sales_db;
CREATE DATABASE reviews_db;
CREATE DATABASE analytics_db;
CREATE DATABASE auth_db;
```


### Load Balancing

HAProxy configuration:


```15:29:haproxy.cfg
frontend http_front
    bind *:80
    stats uri /haproxy?stats
    
    # ACLs for service routing
    acl customer_path path_beg /customers
    acl inventory_path path_beg /items
    acl sales_path path_beg /sales
    acl auth_path path_beg /auth

    # Route to appropriate backends
    use_backend customer_servers if customer_path
    use_backend inventory_servers if inventory_path
    use_backend sales_servers if sales_path
    use_backend auth_servers if auth_path
```


## 📊 Monitoring

The platform includes comprehensive monitoring:

- **Prometheus Metrics**: Basic metrics configuration in:

```1:19:prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'customer_service'
    static_configs:
      - targets: ['customer_service:8000']

  - job_name: 'sales_service'
    static_configs:
      - targets: ['sales_service:8000']

  - job_name: 'inventory_service'
    static_configs:
      - targets: ['inventory_service:8000']

  - job_name: 'analytics_service'
    static_configs:
      - targets: ['analytics_service:8000']
```


- **Profiling Tools**: Available in:

```1:33:utils/profiling.py
from functools import wraps
import cProfile
import pstats
import io
import time
from memory_profiler import profile as memory_profile
import coverage

def performance_profile(output_file=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            try:
                return profiler.runcall(func, *args, **kwargs)
            finally:
                if output_file:
                    profiler.dump_stats(output_file)
                else:
                    # Print profiling stats
                    s = io.StringIO()
                    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
                    stats.print_stats()
                    print(s.getvalue())
        return wrapper
    return decorator

def track_memory_usage(func):
    @wraps(func)
    @memory_profile
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```


## 🧪 Testing

Run the test suite:

```bash
pytest
```

Key test files:
- Customer Service Tests: `tests/test_customer_service.py`
- Inventory Service Tests: `tests/test_inventory_service.py`
- Sales Service Tests: `tests/test_sales_service.py`
- Reviews Service Tests: `tests/test_reviews_service.py`

## 📚 Documentation

Full API documentation is available in Sphinx format. To build:

```bash
cd docs
make html
```

View the documentation at `docs/_build/html/index.html`

## 🛡️ Error Handling

The platform includes a centralized error handling system:


```1:18:utils/error_handlers.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .exceptions import BaseServiceException

def setup_error_handlers(app: FastAPI):
    @app.exception_handler(BaseServiceException)
    async def service_exception_handler(request: Request, exc: BaseServiceException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.detail,
                    "service": exc.service,
                    "additional_info": exc.additional_info
                }
            }
        )
```


## 🔐 Security

- JWT-based authentication
- Role-based access control
- Secure password hashing
- Rate limiting

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
