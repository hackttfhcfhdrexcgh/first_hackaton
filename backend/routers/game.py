# filepath: backend/routers/game.py
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models import SessionLocal, Partner, PlayerProgress, Achievement
from seed_data import hex_grid_minsk
from quest_engine import QuestEngine
from achievement_engine import AchievementEngine

router = APIRouter(prefix="/api")

DEMO_PLAYER = "demo_player_001"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TransactionIn(BaseModel):
    player_id: str = Field(default=DEMO_PLAYER)
    merchant_name: str
    mcc_code: str
    amount: float
    currency: str = "BYN"
    timestamp: str | None = None


@router.get("/hexes")
def get_hexes(db: Session = Depends(get_db)):
    grid = hex_grid_minsk()
    unlocked_ids = {
        pp.hex_id for pp in
        db.query(PlayerProgress).filter_by(player_id=DEMO_PLAYER).all()
    }
    partners = {p.hex_id: p for p in db.query(Partner).all()}

    next_hex = QuestEngine.get_next_unlocked_hex(db, DEMO_PLAYER)
    active_quest = None
    if next_hex:
        active_quest = QuestEngine.get_or_create_quest(db, DEMO_PLAYER, next_hex)

    hexes_out = []
    for h in grid:
        hid = h["hex_id"]
        is_unlocked = hid in unlocked_ids
        partner_obj = partners.get(hid)
        partner_data = None
        if partner_obj and is_unlocked:
            partner_data = {
                "name": partner_obj.name,
                "category": partner_obj.category,
                "cashback_percent": partner_obj.cashback_percent,
            }

        quest_data = None
        if active_quest and active_quest.hex_id == hid:
            percent = int(
                min(100, (active_quest.current_value / max(1, active_quest.target_value)) * 100)
            )
            quest_data = {
                "description": active_quest.description,
                "current": active_quest.current_value,
                "target": active_quest.target_value,
                "percent": percent,
            }

        hexes_out.append({
            "hex_id": hid,
            "ring": h["ring"],
            "center": {"lat": h["center_lat"], "lng": h["center_lng"]},
            "vertices": h["vertices"],
            "is_unlocked": is_unlocked,
            "partner": partner_data,
            "active_quest": quest_data,
        })

    ach_count = db.query(Achievement).filter_by(player_id=DEMO_PLAYER).count()

    return {
        "hexes": hexes_out,
        "stats": {
            "total": len(grid),
            "unlocked": len(unlocked_ids),
            "achievements_count": ach_count,
        },
    }


@router.post("/transaction")
def post_transaction(tx: TransactionIn, db: Session = Depends(get_db)):
    player_id = tx.player_id or DEMO_PLAYER

    target_hex = QuestEngine.get_next_unlocked_hex(db, player_id)
    if not target_hex:
        return {
            "quest_updated": False,
            "quest_completed": False,
            "hex_unlocked": None,
            "progress": None,
            "reward": None,
            "new_achievements": [],
            "next_quest": None,
        }

    quest = QuestEngine.get_or_create_quest(db, player_id, target_hex)
    tx_data = {"mcc_code": tx.mcc_code, "amount": tx.amount}
    updated, completed = QuestEngine.check_and_update(db, quest, tx_data)

    hex_unlocked = None
    reward = None
    new_achievements = []
    next_quest_data = None

    if completed:
        exists = db.query(PlayerProgress).filter_by(
            player_id=player_id, hex_id=target_hex
        ).first()
        if not exists:
            db.add(PlayerProgress(
                player_id=player_id,
                hex_id=target_hex,
                unlocked_at=datetime.utcnow(),
                quest_type=quest.type,
            ))
            db.commit()

        hex_unlocked = target_hex

        partner = db.query(Partner).filter_by(hex_id=target_hex).first()
        if partner:
            reward = {
                "type": "cashback",
                "value": partner.cashback_percent,
                "label": f"{partner.cashback_percent}% кэшбэк в {partner.name}",
            }

        ts = datetime.utcnow()
        if tx.timestamp:
            try:
                ts = datetime.fromisoformat(tx.timestamp.replace("Z", "+00:00"))
            except Exception:
                ts = datetime.utcnow()

        event = {
            "type": "hex_unlocked",
            "hex_id": target_hex,
            "timestamp": ts,
            "mcc": tx.mcc_code,
        }
        new_achievements = AchievementEngine.check_and_award(db, player_id, event)

        next_hex_id = QuestEngine.get_next_unlocked_hex(db, player_id)
        if next_hex_id:
            nq = QuestEngine.get_or_create_quest(db, player_id, next_hex_id)
            next_quest_data = {
                "hex_id": next_hex_id,
                "description": nq.description,
            }

    db.refresh(quest)
    percent = int(
        min(100, (quest.current_value / max(1, quest.target_value)) * 100)
    )
    progress = {
        "current": quest.current_value,
        "target": quest.target_value,
        "percent": percent,
        "description": quest.description,
    }

    return {
        "quest_updated": updated,
        "quest_completed": completed,
        "hex_unlocked": hex_unlocked,
        "progress": progress,
        "reward": reward,
        "new_achievements": new_achievements,
        "next_quest": next_quest_data,
    }


@router.get("/player/{player_id}/profile")
def get_profile(player_id: str, db: Session = Depends(get_db)):
    progress = db.query(PlayerProgress).filter_by(player_id=player_id).all()
    unlocked_ids = [p.hex_id for p in progress]

    achs = db.query(Achievement).filter_by(player_id=player_id).all()
    ach_list = [
        {
            "code": a.code,
            "name": a.name,
            "description": a.description,
            "unlocked_at": a.unlocked_at.isoformat(),
        }
        for a in achs
    ]

    next_hex = QuestEngine.get_next_unlocked_hex(db, player_id)
    active_quest = None
    if next_hex:
        q = QuestEngine.get_or_create_quest(db, player_id, next_hex)
        active_quest = {
            "hex_id": q.hex_id,
            "description": q.description,
            "current": q.current_value,
            "target": q.target_value,
        }

    return {
        "player_id": player_id,
        "unlocked_hexes": unlocked_ids,
        "unlocked_count": len(unlocked_ids),
        "total_hexes": 37,
        "achievements": ach_list,
        "active_quest": active_quest,
    }
