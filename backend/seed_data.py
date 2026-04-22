# filepath: backend/seed_data.py
from math import cos, sin, radians, sqrt
from sqlalchemy.orm import Session
from models import Partner, PlayerProgress, Quest
from datetime import datetime

DEMO_PLAYER = "demo_player_001"


def hex_grid_minsk():
    """Плотная pointy-top гекс-сетка вокруг центра Минска.

    Радиус гекса R задан в градусах широты. Т.к. 1° долготы на широте φ
    короче 1° широты в 1/cos(φ) раз, все долготные смещения делим на cos(φ).
    Для pointy-top соседние центры: dx = R*√3, dy = R*1.5, сдвиг рядов R*√3/2.
    """
    center_lat, center_lng = 53.9045, 27.5615
    R = 0.0027
    lat_scale = 1.0 / cos(radians(center_lat))  # расширение долготы

    hexes = []
    idx = 1

    def make_hex(cx_lat, cy_lng, ring):
        nonlocal idx
        vertices = []
        # pointy-top: углы 30°, 90°, 150°, 210°, 270°, 330°
        for k in range(6):
            angle = radians(60 * k + 30)
            vx = cx_lat + R * sin(angle)
            vy = cy_lng + R * cos(angle) * lat_scale
            vertices.append([vx, vy])
        h = {
            "hex_id": f"hex_{idx:03d}",
            "ring": ring,
            "center_lat": cx_lat,
            "center_lng": cy_lng,
            "vertices": vertices,
        }
        idx += 1
        return h

    # axial-координаты, radius колец в гексах
    grid_radius = 22
    sqrt3 = sqrt(3)
    for q in range(-grid_radius, grid_radius + 1):
        r1 = max(-grid_radius, -q - grid_radius)
        r2 = min(grid_radius, -q + grid_radius)
        for r in range(r1, r2 + 1):
            # pointy-top axial -> offset от центра
            d_lat = R * 1.5 * r
            d_lng = R * sqrt3 * (q + r / 2) * lat_scale
            cx = center_lat + d_lat
            cy = center_lng + d_lng
            ring = max(abs(q), abs(r), abs(-q - r))
            hexes.append(make_hex(cx, cy, ring))

    return hexes


def center_hex_id():
    """hex_id гекса с axial-координатами (0,0) — геометрический центр сетки."""
    for h in hex_grid_minsk():
        if abs(h["center_lat"] - 53.9045) < 1e-9 and abs(h["center_lng"] - 27.5615) < 1e-9:
            return h["hex_id"]
    return hex_grid_minsk()[0]["hex_id"]


def neighbor_hex_id(of_hex_id):
    """hex_id ближайшего соседа к указанному гексу."""
    grid = hex_grid_minsk()
    target = next((h for h in grid if h["hex_id"] == of_hex_id), None)
    if not target:
        return grid[0]["hex_id"]
    best, best_d = None, float("inf")
    for h in grid:
        if h["hex_id"] == of_hex_id:
            continue
        d = (h["center_lat"] - target["center_lat"]) ** 2 + (h["center_lng"] - target["center_lng"]) ** 2
        if d < best_d:
            best, best_d = h["hex_id"], d
    return best


PARTNERS_DATA = [
    ("hex_001", "Лидо", "restaurant", "5812", 53.9045, 27.5615, 3.5),
    ("hex_002", "Васильки", "restaurant", "5812", 53.9102, 27.5498, 4.0),
    ("hex_003", "Раковский Бровар", "restaurant", "5812", 53.9056, 27.5412, 5.0),
    ("hex_004", "Гусь и Клюква", "restaurant", "5812", 53.9132, 27.5701, 3.0),
    ("hex_005", "Тесто", "restaurant", "5812", 53.8978, 27.5689, 4.5),
    ("hex_006", "Хачапури и Вино", "restaurant", "5812", 53.9021, 27.5789, 3.5),
    ("hex_007", "Луна", "restaurant", "5812", 53.9167, 27.5567, 4.0),
    ("hex_008", "Буфет", "restaurant", "5812", 53.8934, 27.5523, 3.0),
    ("hex_009", "Zлата", "restaurant", "5812", 53.9189, 27.5389, 4.5),
    ("hex_010", "Menza", "restaurant", "5812", 53.8912, 27.5812, 3.5),
    ("hex_011", "Евроопт", "grocery", "5411", 53.9234, 27.5445, 2.0),
    ("hex_012", "Корона", "grocery", "5411", 53.8867, 27.5634, 2.5),
    ("hex_013", "Рублёвский", "grocery", "5411", 53.9278, 27.5878, 2.0),
    ("hex_014", "Виталюр", "grocery", "5411", 53.8823, 27.5334, 3.0),
    ("hex_015", "Алми", "grocery", "5411", 53.9321, 27.5712, 2.5),
    ("hex_016", "Гиппо", "grocery", "5411", 53.8789, 27.5923, 2.0),
    ("hex_017", "Bigzz", "grocery", "5411", 53.9345, 27.5234, 3.0),
    ("hex_018", "Санта", "grocery", "5411", 53.8756, 27.5423, 2.5),
    ("hex_019", "Простор", "grocery", "5411", 53.9389, 27.5956, 2.0),
    ("hex_020", "Дионис", "grocery", "5411", 53.8712, 27.5789, 2.5),
    ("hex_021", "А-100 №1", "fuel", "5541", 53.9412, 27.5123, 4.0),
    ("hex_022", "Газпромнефть", "fuel", "5541", 53.8678, 27.6034, 5.0),
    ("hex_023", "Лукойл", "fuel", "5541", 53.9456, 27.6089, 4.5),
    ("hex_024", "Белоруснефть", "fuel", "5541", 53.8634, 27.5067, 5.0),
    ("hex_025", "А-100 №2", "fuel", "5541", 53.9489, 27.5089, 4.0),
    ("hex_026", "Shell", "fuel", "5541", 53.8589, 27.6134, 6.0),
    ("hex_027", "BP", "fuel", "5541", 53.9523, 27.6145, 5.5),
    ("hex_028", "Neste", "fuel", "5541", 53.8545, 27.5012, 5.0),
    ("hex_029", "Wolt", "other", "5999", 53.9567, 27.5278, 7.0),
    ("hex_030", "LetsBike", "other", "5999", 53.8501, 27.5867, 5.0),
    ("hex_031", "Папараць-Кветка", "other", "5999", 53.9601, 27.5834, 4.0),
    ("hex_032", "Соседи", "other", "5999", 53.8467, 27.5378, 3.5),
    ("hex_033", "Скарбніца", "other", "5999", 53.9634, 27.5178, 4.5),
    ("hex_034", "Стар Бургер", "other", "5999", 53.8423, 27.6178, 5.0),
    ("hex_035", "Суши Wok", "other", "5999", 53.9678, 27.6189, 5.5),
    ("hex_036", "Дикая Пицца", "other", "5999", 53.8389, 27.4967, 4.5),
    ("hex_037", "Якитория", "other", "5999", 53.9712, 27.4923, 6.0),
]


def seed_partners(session: Session):
    existing = session.query(Partner).count()
    if existing >= len(PARTNERS_DATA):
        _ensure_demo_start(session)
        return

    for hex_id, name, cat, mcc, lat, lng, cb in PARTNERS_DATA:
        exists = session.query(Partner).filter_by(hex_id=hex_id).first()
        if exists:
            continue
        session.add(Partner(
            hex_id=hex_id, name=name, category=cat, mcc_code=mcc,
            lat=lat, lng=lng, cashback_percent=cb,
        ))
    session.commit()
    _ensure_demo_start(session)


def _ensure_demo_start(session: Session):
    start_hex = center_hex_id()
    next_hex = neighbor_hex_id(start_hex)

    pp = session.query(PlayerProgress).filter_by(
        player_id=DEMO_PLAYER, hex_id=start_hex
    ).first()
    if not pp:
        session.add(PlayerProgress(
            player_id=DEMO_PLAYER,
            hex_id=start_hex,
            unlocked_at=datetime.utcnow(),
            quest_type="single_transaction",
        ))
        session.commit()

    q = session.query(Quest).filter_by(
        player_id=DEMO_PLAYER, hex_id=next_hex, is_completed=False
    ).first()
    if not q:
        from quest_engine import QuestEngine
        QuestEngine.get_or_create_quest(session, DEMO_PLAYER, next_hex)
