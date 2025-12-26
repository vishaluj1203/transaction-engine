import asyncio
from datetime import datetime
from typing import List
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, database

app = FastAPI(title="WFG Transaction Webhook Service")

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "status": "HEALTHY",
        "current_time": datetime.utcnow().isoformat() + "Z"
    }

async def process_transaction_task(transaction_id: str):
    """
    Simulates external API processing with a 30-second delay.
    """
    await asyncio.sleep(30)
    
    db = database.SessionLocal()
    try:
        transaction = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()
        if transaction:
            transaction.status = "PROCESSED"
            transaction.processed_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()

@app.post("/v1/webhooks/transactions", status_code=status.HTTP_202_ACCEPTED, tags=["Webhooks"])
async def receive_transaction_webhook(
    payload: schemas.TransactionWebhook,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db)
):
    # Idempotency Check
    existing_transaction = db.query(models.Transaction).filter(
        models.Transaction.transaction_id == payload.transaction_id
    ).first()
    
    if existing_transaction:
        # If already exists, we acknowledge but don't re-process
        return {"message": "Webhook received (already exists)"}

    # Create new transaction record
    new_transaction = models.Transaction(
        transaction_id=payload.transaction_id,
        source_account=payload.source_account,
        destination_account=payload.destination_account,
        amount=payload.amount,
        currency=payload.currency,
        status="PROCESSING"
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    # Queue background task
    background_tasks.add_task(process_transaction_task, payload.transaction_id)

    return {"message": "Transaction accepted for processing"}

@app.get("/v1/transactions/{transaction_id}", response_model=List[schemas.TransactionResponse], tags=["Transactions"])
def get_transaction_status(transaction_id: str, db: Session = Depends(database.get_db)):
    transactions = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).all()
    if not transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transactions
