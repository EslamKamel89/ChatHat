# Application setup

This package contains code that configures and manages the FastAPI application instance. The application factory in `src/chathat/main.py` connects these components.

| Module        | Responsibility                                                                                       |
| ------------- | ---------------------------------------------------------------------------------------------------- |
| `lifespan.py` | Manages startup and shutdown. Sets `app.state.started` during startup and clears it during shutdown. |

As application setup grows, add modules here for middleware registration, exception handlers, and other instance configuration.

Feature routes, schemas, models, services, and tests belong in their respective feature directories.
