from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from sweater.schemas.process.process_schema import CreateProcess, UpdateProcess
from sweater.services.process.process_service import get_list_of_processes, get_process_by_id, create_process_, delete_process_, update_process_
from sweater.services.process.attributes_service import get_available_tables
from sweater.database.references_db import get_reference_db
from sweater.routes.auth import get_current_user
from sweater.middleware.role_middleware import require_roles

router = APIRouter(prefix="/process", tags=["process"])

@router.get("/tables")
def list_available_tables(user: dict = Depends(require_roles("admin"))):
    return get_available_tables()

@router.get("/list")
def list_processes(user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    processes = get_list_of_processes(db)
    return {"success": True, "data": processes}

@router.get("/{process_id}")
def get_process(process_id: str, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    process = get_process_by_id(db, process_id)
    if process:
        return {"success": True, "data": process}
    else:
        return {"success": False, "error": "Process not found"}
    
@router.post("/create")
def create_process(v: CreateProcess, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    if not v.title or not v.description:
        return {"success": False, "error": "Title and description are required"}
    new_process = create_process_(db, v)
    return {"success": True, "data": new_process}

@router.delete("/delete/{process_id}")
def delete_process(process_id: str, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    process = delete_process_(db, process_id)
    if process:
        return {"success": True, "data": process}
    else:
        return {"success": False, "error": "Process not found"}
    
@router.put("/update/{process_id}")
def update_process(process_id: str, updated_process: UpdateProcess, user: dict = Depends(require_roles("admin")), db: Session = Depends(get_reference_db)):
    process = update_process_(db, process_id, updated_process)
    if process:
        return {"success": True, "data": process}
    else:
        return {"success": False, "error": "Process not found"}
    
