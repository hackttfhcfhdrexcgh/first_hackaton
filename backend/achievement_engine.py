# filepath: backend/achievement_engine.py
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Achievement, PlayerProgress, Partner

CATEGORY_LABELS = {
    "restaurant": "ресторанов",
    "grocery": "супермаркетов",
    "fuel": "заправок",
    "other": "сервисов",
}


class AchievementEngine:

    @staticmethod
    def _award(session: Session, player_id: str, code: str, name: str,
               description: str, reward_label: str):
        existing = session.query(Achievement).filter_by(
            player_id=player_id, code=code
        ).first()
        if existing:
            return None
        ach = Achievement(
            player_id=player_id,
            code=code,
            name=name,
            description=description,
            unlocked_at=datetime.utcnow(),
        )
        session.add(ach)
        try:
            session.commit()
            session.refresh(ach)
        except IntegrityError:
            session.rollback()
            return None
        return {
            "code": ach.code,
            "name": ach.name,
            "description": ach.description,
            "reward_label": reward_label,
            "unlocked_at": ach.unlocked_at.isoformat(),
        }

    @classmethod
    def check_and_award(cls, session: Session, player_id: str, event: dict):
        new_achievements = []
        if event.get("type") != "hex_unlocked":
            return new_achievements

        unlocked_count = session.query(PlayerProgress).filter_by(
            player_id=player_id
        ).count()

        if unlocked_count >= 3:
            a = cls._award(
                session, player_id, "explorer_3",
                "Первые шаги",
                "Разблокируй 3 территории",
                "+50 бонусных баллов",
            )
            if a:
                new_achievements.append(a)

        if unlocked_count >= 10:
            a = cls._award(
                session, player_id, "explorer_10",
                "Картограф",
                "Разблокируй 10 территорий",
                "+200 бонусных баллов",
            )
            if a:
                new_achievements.append(a)

        unlocked_hex_ids = [
            pp.hex_id for pp in
            session.query(PlayerProgress).filter_by(player_id=player_id).all()
        ]
        if unlocked_hex_ids:
            partners = session.query(Partner).filter(
                Partner.hex_id.in_(unlocked_hex_ids)
            ).all()
            counts = {}
            for p in partners:
                counts[p.category] = counts.get(p.category, 0) + 1
            for category, cnt in counts.items():
                if cnt >= 3:
                    label = CATEGORY_LABELS.get(category, category)
                    a = cls._award(
                        session, player_id,
                        f"category_master_{category}",
                        f"Мастер {label}",
                        f"Разблокируй 3 гекса категории {label}",
                        "Двойной кэшбэк в категории 30 дней",
                    )
                    if a:
                        new_achievements.append(a)

        ts = event.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                ts = datetime.utcnow()
        elif ts is None:
            ts = datetime.utcnow()

        if ts.hour >= 22 or ts.hour < 5:
            a = cls._award(
                session, player_id, "night_owl",
                "Ночной исследователь",
                "Разблокируй территорию ночью",
                "+100 бонусных баллов",
            )
            if a:
                new_achievements.append(a)

        return new_achievements
