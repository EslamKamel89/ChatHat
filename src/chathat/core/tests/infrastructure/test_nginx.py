import json
from http.client import HTTPConnection
from urllib.request import ProxyHandler, build_opener


def test_health_through_nginx() -> None:
    opener = build_opener(ProxyHandler({}))
    with opener.open("http://nginx/health", timeout=5) as response:
        assert response.status == 200
        assert response.headers.get_content_type() == "application/json"
        assert json.load(response) == {"status": "ok"}


def test_redirect_preserves_host_and_rejects_spoofed_protocol() -> None:
    connection = HTTPConnection("nginx", timeout=5)
    try:
        connection.request(
            "GET",
            "/health/",
            headers={
                "Host": "dashboard.example.test:8080",
                "X-Forwarded-Proto": "https",
                "X-Forwarded-Host": "attacker.example.test",
                "Forwarded": 'host=attacker.example.test;proto=https',
            },
        )
        with connection.getresponse() as response:
            assert response.status == 307
            assert response.getheader("Location") == (
                "http://dashboard.example.test:8080/health"
            )
            response.read()
    finally:
        connection.close()


def test_static_stylesheet_is_served_by_nginx() -> None:
    opener = build_opener(ProxyHandler({}))
    with opener.open("http://nginx/static/site.css", timeout=5) as response:
        assert response.status == 200
        assert response.headers.get_content_type() == "text/css"
        assert response.read().decode().strip() == (
            ":root {\n  color-scheme: light dark;\n}"
        )

    # The application has no static route: this asset belongs to Nginx.
    connection = HTTPConnection("127.0.0.1", 8000, timeout=5)
    try:
        connection.request("GET", "/static/site.css")
        with connection.getresponse() as response:
            assert response.status == 404
            response.read()
    finally:
        connection.close()


def test_nginx_rejects_body_larger_than_limit_before_upload() -> None:
    connection = HTTPConnection("nginx", timeout=5)
    try:
        # Nginx can reject a known oversized body from Content-Length alone.
        # Send only headers to avoid a broken pipe while uploading rejected data.
        connection.putrequest("POST", "/health")
        connection.putheader("Content-Type", "application/octet-stream")
        connection.putheader("Content-Length", str(10 * 1024 * 1024 + 1))
        connection.endheaders()
        with connection.getresponse() as response:
            assert response.status == 413
            assert response.getheader("Server", "").startswith("nginx/")
            response.read()
    finally:
        connection.close()
