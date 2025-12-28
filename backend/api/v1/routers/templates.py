from fastapi import APIRouter

router = APIRouter(tags=["Templates"])

@router.get("/template")
def get_templates():
    return {"message": "Get all templates"}

@router.post("/template")
def create_template():
    return {"message": "Create template"}

@router.put("/template")
def update_template():
    return {"message": "Update template"}

@router.delete("/template")
def delete_template():
    return {"message": "Delete template"}
