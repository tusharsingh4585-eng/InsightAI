from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import Base, engine, get_db
from app.models import Dataset
from app.services import analyze_csv

Base.metadata.create_all(bind=engine)

router = APIRouter()

@router.post("/datasets/analyze")
async def analyze_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported in this starter version.")

    raw = await file.read()
    if len(raw) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        result = analyze_csv(raw)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not analyze CSV: {exc}")

    dataset = Dataset(
        filename=file.filename,
        rows=result["rows"],
        columns=result["columns"],
        revenue_total=result["revenue_total"],
        profit_total=result["profit_total"],
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return {
        "dataset_id": dataset.id,
        "summary": {
            "rows": result["rows"],
            "columns": result["columns"],
            "revenue_total": result["revenue_total"],
            "profit_total": result["profit_total"],
            "profit_margin": result["profit_margin"],
            "columns_list": result["columns_list"],
        },
        "insights": result["insights"],
        "trend": result["trend"],
    }

@router.get("/datasets")
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(Dataset).order_by(Dataset.id.desc()).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "rows": d.rows,
            "columns": d.columns,
            "revenue_total": d.revenue_total,
            "profit_total": d.profit_total,
        }
        for d in datasets
    ]
