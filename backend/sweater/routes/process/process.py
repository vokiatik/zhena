from fastapi import APIRouter
from fastapi.params import Depends
from requests import Session

from sweater.schemas.process.process_schema import UpdateProcess
from sweater.services.process.process_service import get_list_of_processes, get_process_by_id, create_process_, delete_process_, update_process_
from sweater.database.base_db import get_db
from sweater.database.references_db import get_reference_db

router = APIRouter(prefix="/process", tags=["process"])

@router.get("/list")
def list_processes(db: Session = Depends(get_reference_db)):
    processes = get_list_of_processes(db)
    return {"success": True, "data": processes}

@router.get("/{process_id}")
def get_process(process_id: str, db: Session = Depends(get_reference_db)):
    process = get_process_by_id(db, process_id)
    if process:
        return {"success": True, "data": process}
    else:
        return {"success": False, "error": "Process not found"}
    
@router.post("/create")
def create_process(title:str, description: str, db: Session = Depends(get_reference_db)):
    new_process = create_process_(db, title, description, responsible_user_id=None)
    return {"success": True, "data": new_process}

@router.delete("/delete/{process_id}")
def delete_process(process_id: str, db: Session = Depends(get_reference_db)):
    process = delete_process_(db, process_id)
    if process:
        return {"success": True, "data": process}
    else:
        return {"success": False, "error": "Process not found"}
    
@router.put("/update/{process_id}")
def update_process(process_id: str, updated_process: UpdateProcess, db: Session = Depends(get_reference_db)):
    process = update_process_(db, process_id, title=updated_process.title, description=updated_process.description, responsible_user_id=None)
    if process:
        return {"success": True, "data": process}
    else:
        return {"success": False, "error": "Process not found"}
    
