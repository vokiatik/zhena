from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sweater.routes.chat import router as chat_router
from sweater.routes.auth import router as auth_router
from sweater.routes.picture_screening import router as picture_router
from sweater.routes.file_uploading import router as upload_router
from sweater.routes.process.process import router as process_router
from sweater.routes.process.attribute import router as attribute_router
from sweater.routes.process.reference import router as reference_router




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
app.include_router(reference_router)



@app.get("/")
async def root():
    return {"message": "Text Analyser API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
