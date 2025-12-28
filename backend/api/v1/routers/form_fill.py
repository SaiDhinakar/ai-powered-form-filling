from fastapi import APIRouter

router = APIRouter(tags=["Form Fill"])

@router.post("/form-fill")
def form_fill():
    return {"message": "Form fill endpoint"}
