import os
import json
import threading
import logging
from config import DB_FILE, CLANS_FILE, CHAT_SETTINGS_FILE, LOG_FILE, START_BALANCE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

db_lock = threading.Lock()

os.makedirs('data', exist_ok=True)
os.makedirs('logs', exist_ok=True)


def load_db():
    """Загрузка БД пользователей"""
    try:
        if not os.path.exists(DB_FILE):
            return {}
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"load_db error: {e}")
        return {}


def save_db(db):
    """Сохранение БД пользователей"""
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"save_db error: {e}")


def load_clans():
    """Загрузка БД кланов"""
    try:
        if not os.path.exists(CLANS_FILE):
            return {}
        with open(CLANS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"load_clans error: {e}")
        return {}


def save_clans(clans):
    """Сохранение БД кланов"""
    try:
        with open(CLANS_FILE, 'w', encoding='utf-8') as f:
            json.dump(clans, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"save_clans error: {e}")


def load_chat_settings():
    """Загрузка настроек чатов"""
    try:
        if not os.path.exists(CHAT_SETTINGS_FILE):
            return {}
        with open(CHAT_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"load_chat_settings error: {e}")
        return {}


def save_chat_settings(settings):
    """Сохранение настроек чатов"""
    try:
        with open(CHAT_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"save_chat_settings error: {e}")


def ensure_user(db, uid, name="User"):
    """Инициализация пользователя"""
    uid = str(uid)
    defaults = {
        "name": name if name != "User" else "User",
        "balance": START_BALANCE,
        "bank": 0,
        "last_daily": 0,
        "last_work": 0,
        "last_game": 0,
        "wins": 0,
        "losses": 0,
        "inventory": [],
        "spouse": None,
        "xp": 0,
        "level": 1,
        "karma": 0,
        "warns": 0,
        "muted_until": 0,
        "nickname": None,
        "clan": None,
        "achievements": [],
        "work_count": 0,
        "rp_count": 0,
        "children": [],
        "pet": None,
        "potion_until": 0,
        "ai_persona": "default",
    }
    
    if uid not in db:
        db[uid] = defaults
    else:
        for k, v in defaults.items():
            if k not in db[uid]:
                db[uid][k] = v
        if name != "User":
            db[uid]["name"] = name
    
    return db


def has_item(db, uid, item_key):
    """Проверка наличия предмета"""
    return item_key in db[str(uid)].get("inventory", [])


def add_xp(db, uid, amount, chat_id=None, bot=None):
    """Добавление XP и проверка уровня"""
    from utils.formatters import fmt_amount
    
    uid = str(uid)
    if uid not in db:
        return db
    
    db[uid]["xp"] = db[uid].get("xp", 0) + amount
    old_level = db[uid].get("level", 1)
    new_level = 1 + db[uid]["xp"] // 100
    
    if new_level > old_level:
        db[uid]["level"] = new_level
        if chat_id and bot:
            bonus = new_level * 1000
            db[uid]["balance"] = db[uid].get("balance", 0) + bonus
            name = db[uid].get("nickname") or db[uid].get("name", "?")
            try:
                bot.send_message(chat_id,
                    f"🎉 {name} достиг {new_level} уровня!\n+{fmt_amount(bonus)} ЛК бонус!")
            except:
                pass
    
    return db


def check_achievements(db, uid, chat_id, bot=None):
    """Проверка достижений"""
    from config import ACHIEVEMENTS
    
    uid = str(uid)
    if uid not in db:
        return db
    
    user = db[uid]
    for ach_key, ach in ACHIEVEMENTS.items():
        if ach_key not in user.get("achievements", []):
            try:
                if ach["condition"](user):
                    user["achievements"].append(ach_key)
                    if chat_id and bot:
                        try:
                            bot.send_message(chat_id,
                                f"🏅 ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!\n"
                                f"{ach['name']}\n{ach['desc']}\n\n"
                                f"🎉 {user.get('nickname') or user['name']} получил достижение!")
                        except:
                            pass
            except Exception as e:
                logger.error(f"check_achievements error: {e}")
    
    return db
