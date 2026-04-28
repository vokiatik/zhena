from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from sweater.schemas.process.process_schema import CreateProcess, UpdateProcess
from sweater.services.process.process_service import get_list_of_processes, get_process_by_id, create_process_, delete_process_, update_process_, get_process_types
from sweater.database.references_db import get_reference_db
from sweater.middleware.role_middleware import require_roles

router = APIRouter(prefix="/process", tags=["process"])

@router.get("/types")
def list_process_types(
    user: dict = Depends(require_roles("admin")), 
    db: Session = Depends(get_reference_db)
):
    return get_process_types(db)

@router.get("/list")
def list_processes(
    user: dict = Depends(require_roles("admin")), 
    db: Session = Depends(get_reference_db)
):
    processes = get_list_of_processes(db)
    return {"success": True, "data": processes}

@router.get("/{process_id}")
def get_process(
    process_id: str, 
    user: dict = Depends(require_roles("admin")), 
    db: Session = Depends(get_reference_db)
):
    process = get_process_by_id(db, process_id)
    if process:
        return {"success": True, "data": process}
    else:
        return {"success": False, "error": "Process not found"}
    
@router.post("/create")
def create_process(
    body: CreateProcess, 
    user: dict = Depends(require_roles("admin")), 
    db: Session = Depends(get_reference_db)
):
    print("Received create process request with body:", body)
    if not body.title or not body.description:
        return {"success": False, "error": "Title and description are required"}
    new_process = create_process_(db, body)
    return {"success": True, "data": new_process}

@router.delete("/delete/{process_id}")
def delete_process(
    process_id: str, 
    user: dict = Depends(require_roles("admin")), 
    db: Session = Depends(get_reference_db)
):
    process = delete_process_(db, process_id)
    if process:
        return {"success": True, "data": process}
    else:
        return {"success": False, "error": "Process not found"}
    
@router.put("/update/{process_id}")
def update_process(
    process_id: str, 
    updated_process: UpdateProcess, 
    user: dict = Depends(require_roles("admin")), 
    db: Session = Depends(get_reference_db)
):
    process = update_process_(db, process_id, updated_process)
    if process:
        return {"success": True, "data": process}
    else:
        return {"success": False, "error": "Process not found"}
    
