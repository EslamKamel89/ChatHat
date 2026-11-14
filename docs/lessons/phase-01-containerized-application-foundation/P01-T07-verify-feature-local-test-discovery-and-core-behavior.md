# P01-T07 · Verify feature-local test discovery and core behavior

Verify P01-I07 by running the existing five tests from both the core feature and the repository root, then demonstrate the installed application entry point. [Implementation plan](../../chathat-implementation-plan.md#p01-t07--test-verify-feature-local-test-discovery-and-core-behavior)

P01-I07 is recorded as complete. Health now lives in `core/routes/health.py`, its response schema in `core/schemas/health.py`, and the tests in `core/tests/test_app.py`. Lifespan lives in `core/application/lifespan.py`, a recorded difference from the specification's `core/lifespan.py` path. The factory imports the implemented path. The phase notes record a passing focused run after schema extraction. This lesson verifies the whole refactor together. [Phase notes](../../progress-documentation/phase-01-notes.md#p01-i07--organize-the-application-foundation-by-feature) · [Specification §2.2](../../chathat-spec.md#22-feature-packages)

## Contract and strategy

These are in-process API tests. They exercise the real factory, router, response serialization, and lifespan through `TestClient`. Each function gets a fresh app from the function-scoped `app` fixture. Entering the client context runs startup, and leaving it runs shutdown.

Open `src/chathat/core/tests/test_app.py` and review the existing tests in this order.

| Test | What its assertions prove |
| --- | --- |
| `test_health_returns_ok_after_startup` | The factory registers health and the running app returns HTTP 200, JSON content type, and exactly `{"status":"ok"}`. |
| `test_unregistered_path_returns_404` | An unknown path receives HTTP 404. |
| `test_health_returns_unavailable_without_startup` | Skipping client lifespan yields HTTP 503 with exactly `{"detail":"Application unavailable"}`. |
| `test_lifespan_changes_only_its_own_app` | Factory calls return distinct apps, starting one leaves the other inactive, and shutdown clears the started app's flag. |
| `test_startup_error_propagates` | A startup exception reaches the caller before the client context can enter successfully. |

The unavailable test uses `closing(TestClient(app))`. This closes the HTTP client without invoking its lifespan context. In the startup failure test, `monkeypatch` replaces `main.lifespan` before `create_app()` runs. The factory resolves that imported name at call time. Pytest restores the original name after the test.

There are no tenant-owned resources or external services in this increment. The tests need only the existing development dependencies. Compose is introduced in P01-I02.

## 1. Check discovery

From the repository root, run these commands.

```sh
uv run --locked pytest --collect-only -q src/chathat/core/tests
uv run --locked pytest --collect-only -q
```

Expect both commands to collect the same five test functions under `src/chathat/core/tests/test_app.py`. Collection checks the new package location and imports before execution. A count of zero suggests a path or discovery configuration problem. Import errors suggest an outdated source import or an environment that cannot import the installed `chathat` package.

## 2. Run the focused and full suites

```sh
uv run --locked pytest -q src/chathat/core/tests
uv run --locked pytest -q
```

Expect **5 passed** from each command in the current checkout. The focused command demonstrates that core owns a runnable suite. The root command demonstrates that normal project-wide execution finds that suite.

If a test fails, trace the failure to its contract in the table above. For a startup failure test that unexpectedly enters the client context, inspect the name used in `create_app()` and the patch target together. For a 503 response in the success test, check that the request executes inside the client context.

## 3. Demonstrate the installed app

Start Uvicorn from the repository root.

```sh
uv run --locked uvicorn chathat.main:create_app --factory --lifespan on --host 127.0.0.1 --port 8000
```

In another terminal, request health.

```sh
curl -i http://127.0.0.1:8000/health
```

Expect successful startup and HTTP 200 with `{"status":"ok"}`. Stop Uvicorn with Ctrl+C and check that application shutdown completes. This exercises the installed entry point through a real ASGI server. If port 8000 is occupied, choose a free port in both commands.

## Completion evidence

Record the focused and full pytest results and the Uvicorn demonstration in the phase notes. Propose marking P01-T07 complete once those checks pass, and refresh the source map with P01-I02 as the next lesson. Commands in this walkthrough are supplied for execution and their results remain pending for this lesson. [Phase notes](../../progress-documentation/phase-01-notes.md) · [Tracker](../../progress-documentation/phase_1.md) · [Source map](../../../src/chathat/README.md)

Next is **P01-I02 — Dockerfile and development Compose foundation**.
