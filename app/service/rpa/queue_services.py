from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from models import Queue, QueueItem
from schemas.queues import QueueItemCreate, RPAStatus
from sqlalchemy.orm import Session


class QueueService:
    @staticmethod
    def create_queue(queue_name: str, queue_description: str, db: Session):
        if db.query(Queue).filter(Queue.name == queue_name).first():
            raise HTTPException(status_code=400, detail="Queue with this name already exists")
        new_queue = Queue(name=queue_name, description=queue_description, created_at=datetime.utcnow())
        db.add(new_queue)
        db.commit()
        db.refresh(new_queue)
        return new_queue

    @staticmethod
    def add_item(queue_name: str, item_data: QueueItemCreate, db: Session):
        queue = db.query(Queue).filter_by(name=queue_name).first()
        if not queue:
            raise HTTPException(status_code=404, detail="Queue not found")
        new_item = QueueItem(
            queue_id=queue.id,
            payload=item_data.payload,
            priority=item_data.priority,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

    @staticmethod
    def get_pending_items(queue_name: str, db: Session):
        queue = db.query(Queue).filter_by(name=queue_name).first()
        if not queue:
            raise HTTPException(status_code=404, detail="Queue not found")
        items = (
            db.query(QueueItem)
            .filter_by(queue_id=queue.id, status=RPAStatus.PENDING)
            .order_by(QueueItem.priority.desc(), QueueItem.created_at)
            .all()
        )
        return items

    @staticmethod
    def get_next_item(queue_name: str, worker_id: str, db: Session):
        queue = db.query(Queue).filter_by(name=queue_name).first()

        if not queue:
            raise Exception(f"Fila '{queue_name}' não encontrada")

        if not queue.is_active:
            raise Exception(f"Fila '{queue_name}' está pausada")

        item = (
            db.query(QueueItem)
            .filter_by(queue_id=queue.id, status="pending")
            .order_by(QueueItem.priority.desc(), QueueItem.created_at)
            .with_for_update(skip_locked=True)
            .first()
        )

        if item:
            item.status = RPAStatus.RUNNING
            item.locked_by = worker_id
            db.commit()
            db.refresh(item)

        return item

    @staticmethod
    def mark_success(item_id: UUID, db: Session):
        item = db.query(QueueItem).filter_by(id=item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        item.status = RPAStatus.SUCCESS
        item.updated_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def mark_fail(item_id: UUID, error: str, db: Session):
        item = db.query(QueueItem).filter_by(id=item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        item.attempts += 1
        item.error = error
        item.updated_at = datetime.utcnow()
        if item.attempts >= item.max_attempts:
            item.status = RPAStatus.FAILED
        else:
            item.status = RPAStatus.PENDING
            item.locked_by = None
            item.locked_at = None
        db.commit()

    @staticmethod
    def toggle_queue_status(queue_name: str, db: Session):
        queue = db.query(Queue).filter_by(name=queue_name).first()

        if not queue:
            return None

        queue.is_active = not queue.is_active
        db.commit()
        db.refresh(queue)

        return queue
