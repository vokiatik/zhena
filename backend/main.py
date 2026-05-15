from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sweater.routes.chat import router as chat_router
from sweater.routes.auth import router as auth_router
from sweater.routes.picture_screening import router as picture_router
from sweater.routes.upload.file_uploading import router as upload_router
from sweater.routes.process.process import router as process_router
from sweater.routes.process.attribute import router as attribute_router
from sweater.routes.process.process_instances import router as process_instances_router
from sweater.routes.roles import router as roles_router
from sweater.routes.admin.table_editor import router as admin_router
from sweater.routes.image_proxy import router as image_proxy_router
from sweater.routes.yandex_disk import router as yandex_disk_router

from sweater.database.base_db import SessionLocal
from sweater.services.auth.role_service import seed_default_roles




app = FastAPI(title="Text Analyser API")

# Allow the Vite dev server origin (local + Docker)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://frontend:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(picture_router)
app.include_router(upload_router)
app.include_router(process_router)
app.include_router(attribute_router)
app.include_router(process_instances_router)
app.include_router(roles_router)
app.include_router(admin_router)
app.include_router(image_proxy_router)
app.include_router(yandex_disk_router)


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_default_roles(db)
    finally:
        db.close()



@app.get("/")
async def root():
    return {"message": "Text Analyser API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
