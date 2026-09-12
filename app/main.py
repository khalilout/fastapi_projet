from fastapi import FastAPI

from app.routes import offre, users, auth, candidature, stats

from app.middlewares.request_id import RequestIDMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.core.errors import AppException, app_exception_handler


app = FastAPI(title="StageFlow")

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)

app.add_exception_handler(AppException, app_exception_handler)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(offre.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(candidature.router)
app.include_router(stats.router)
