from fastapi import APIRouter

router = APIRouter(prefix="/process", tags=["process"])

@router.get("/list")
def list_processes():