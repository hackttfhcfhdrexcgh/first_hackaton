# filepath: backend/quest_engine.py
from datetime import datetime
from sqlalchemy.orm import Session
from models import Quest, PlayerProgress


class QuestEngine:
    QUEST_PROGRESSION = {
        0: {"type": "single_transaction", "target": 1, "mcc": None,
            "description": "Сделай любую покупку картой MTBank"},
        1: {"type": "category_count", "target": 2, "mcc": "5812",
            "description": "Оплати 2 раза в ресторанах"},
        2: {"type": "category_count", "target": 2, "mcc": "5812",
            "description": "Ещё 2 покупки в кафе или ресторанах"},
        3: {"type": "category_count", "target": 3, "mcc": "5411",
            "description": "Купи продукты 3 раза"},
        4: {"type": "cumulative_amount", "target": 20, "mcc": None,
            "description": "Потрать суммарно 20 BYN"},
        5: {"type": "category_count", "target": 2, "mcc": "5411",
            "description": "2 покупки в супермаркетах"},
        6: {"type": "cumulative_amount", "target": 30, "mcc": None,
            "description": "Потрать суммарно 30 BYN"},
        7: {"type": "mcc_specific", "target": 2, "mcc": "5541",
            "description": "Заправься 2 раза"},
        8: {"type": "category_count", "target": 4, "mcc": "5812",
            "description": "4 похода в рестораны"},
        9: {"type": "cumulative_amount", "target": 50, "mcc": None,
            "description": "Потрать суммарно 50 BYN"},
        10: {"type": "category_count", "target": 3, "mcc": "5411",
             "description": "3 покупки в супермаркетах"},
        11: {"type": "mcc_specific", "target": 3, "mcc": "5541",
             "description": "Заправься 3 раза"},
        12: {"type": "cumulative_amount", "target": 70, "mcc": None,
             "description": "Потрать суммарно 70 BYN"},
        13: {"type": "category_count", "target": 5, "mcc": "5812",
             "description": "5 походов в рестораны"},
        14: {"type": "cumulative_amount", "target": 100, "mcc": None,
             "description": "Потрать суммарно 100 BYN"},
        15: {"type": "mcc_specific", "target": 4, "mcc": "5541",
             "description": "Заправься 4 раза"},
        16: {"type": "category_count", "target": 4, "mcc": "5411",
             "description": "4 покупки в супермаркетах"},
        17: {"type": "cumulative_amount", "target": 130, "mcc": None,
             "description": "Потрать суммарно 130 BYN"},
        18: {"type": "category_count", "target": 6, "mcc": "5812",
             "description": "6 походов в рестораны"},
        19: {"type": "cumulative_amount", "target": 160, "mcc": None,
             "description": "Потрать суммарно 160 BYN"},
        20: {"type": "mcc_specific", "target": 5, "mcc": "5541",
             "description": "Заправься 5 раз"},
        21: {"type": "category_count", "target": 5, "mcc": "5411",
             "description": "5 покупок в супермаркетах"},
        22: {"type": "cumulative_amount", "target": 200, "mcc": None,
             "description": "Потрать суммарно 200 BYN"},
        23: {"type": "category_count", "target": 7, "mcc": "5812",
             "description": "7 походов в рестораны"},
        24: {"type": "cumulative_amount", "target": 250, "mcc": None,
             "description": "Потрать суммарно 250 BYN"},
        25: {"type": "mcc_specific", "target": 6, "mcc": "5541",
             "description": "Заправься 6 раз"},
        26: {"type": "category_count", "target": 6, "mcc": "5411",
             "description": "6 покупок в супермаркетах"},
        27: {"type": "cumulative_amount", "target": 300, "mcc": None,
             "description": "Потрать суммарно 300 BYN"},
        28: {"type": "category_count", "target": 8, "mcc": "5812",
             "description": "8 походов в рестораны"},
        29: {"type": "cumulative_amount", "target": 350, "mcc": None,
             "description": "Потрать суммарно 350 BYN"},
        30: {"type": "mcc_specific", "target": 7, "mcc": "5541",
             "description": "Заправься 7 раз"},
        31: {"type": "category_count", "target": 7, "mcc": "5411",
             "description": "7 покупок в супермаркетах"},
        32: {"type": "cumulative_amount", "target": 400, "mcc": None,
             "description": "Потрать суммарно 400 BYN"},
        33: {"type": "category_count", "target": 9, "mcc": "5812",
             "description": "9 походов в рестораны"},
        34: {"type": "cumulative_amount", "target": 500, "mcc": None,
             "description": "Потрать суммарно 500 BYN"},
        35: {"type": "mcc_specific", "target": 8, "mcc": "5541",
             "description": "Заправься 8 раз"},
        36: {"type": "cumulative_amount", "target": 600, "mcc": None,
             "description": "Потрать суммарно 600 BYN — ты легенда!"},
    }

    @classmethod
    def _progression_for_hex(cls, hex_id: str):
        try:
            idx = int(hex_id.replace("hex_", "")) - 1
        except ValueError:
            idx = 0
        return cls.QUEST_PROGRESSION.get(idx, cls.QUEST_PROGRESSION[0])

    @classmethod
    def get_or_create_quest(cls, session: Session, player_id: str, hex_id: str) -> Quest:
        quest = session.query(Quest).filter_by(
            player_id=player_id, hex_id=hex_id, is_completed=False
        ).first()
        if quest:
            return quest

        spec = cls._progression_for_hex(hex_id)
        quest = Quest(
            player_id=player_id,
            hex_id=hex_id,
            type=spec["type"],
            description=spec["description"],
            target_value=spec["target"],
            current_value=0,
            mcc_filter=spec["mcc"],
            is_completed=False,
            created_at=datetime.utcnow(),
        )
        session.add(quest)
        session.commit()
        session.refresh(quest)
        return quest

    @classmethod
    def check_and_update(cls, session: Session, quest: Quest, transaction_data: dict):
        if quest.is_completed:
            return (False, True)

        mcc = transaction_data.get("mcc_code")
        amount = float(transaction_data.get("amount", 0))
        updated = False

        if quest.type == "single_transaction":
            quest.current_value += 1
            updated = True
        elif quest.type == "category_count":
            if mcc == quest.mcc_filter:
                quest.current_value += 1
                updated = True
        elif quest.type == "cumulative_amount":
            quest.current_value += int(amount)
            updated = True
        elif quest.type == "mcc_specific":
            if mcc == quest.mcc_filter:
                quest.current_value += 1
                updated = True

        completed = False
        if quest.current_value >= quest.target_value:
            quest.is_completed = True
            completed = True

        session.commit()
        session.refresh(quest)
        return (updated, completed)

    @classmethod
    def get_next_unlocked_hex(cls, session: Session, player_id: str):
        unlocked = {
            pp.hex_id for pp in
            session.query(PlayerProgress).filter_by(player_id=player_id).all()
        }
        for i in range(1, 38):
            hid = f"hex_{i:03d}"
            if hid not in unlocked:
                return hid
        return None
