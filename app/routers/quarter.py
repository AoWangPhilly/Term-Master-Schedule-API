from typing import List

from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/quarters",
    tags=["Quarters"]
)


@router.get("/{term}", response_model=List[schemas.Quarter])
def get_quarter(term: int, db: Session = Depends(get_db)):
    quarter = db.query(models.Quarter).filter(models.Quarter.term == term).all()
    if not quarter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"There's no term with {term}")
    return quarter
