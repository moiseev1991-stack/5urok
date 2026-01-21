import sqlite3
from pathlib import Path
from datetime import datetime
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Подключение к базе данных
db_path = Path(__file__).parent / 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "="*70)
print(" " * 20 + "БАЗА ДАННЫХ - ПЕРЕРАБОТКА БАТАРЕЕК")
print("="*70)

# ========== ВСЕ ТАБЛИЦЫ ==========
print("\n[ТАБЛИЦЫ В БАЗЕ ДАННЫХ]")
print("-" * 70)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()
for i, table in enumerate(tables, 1):
    # Получаем количество записей в каждой таблице
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
    count = cursor.fetchone()[0]
    print(f"  {i}. {table[0]:<35} ({count} записей)")

# ========== ПОЛЬЗОВАТЕЛИ ==========
print("\n" + "="*70)
print("[ПОЛЬЗОВАТЕЛИ]")
print("="*70)
cursor.execute("""
    SELECT id, username, email, date_joined, last_login, is_superuser 
    FROM auth_user 
    ORDER BY date_joined;
""")
users = cursor.fetchall()

if users:
    print(f"\n{'ID':<5} {'Username':<20} {'Email':<25} {'Дата регистрации':<20} {'Последний вход':<20}")
    print("-" * 95)
    for user in users:
        user_id = user[0]
        username = user[1]
        email = user[2] or "не указан"
        date_joined = user[3][:10] if user[3] else "N/A"
        last_login = user[4][:16] if user[4] else "никогда"
        is_superuser = "[Admin]" if user[5] else ""
        
        print(f"{user_id:<5} {username:<20} {email:<25} {date_joined:<20} {last_login:<20} {is_superuser}")
    
    print(f"\n[OK] Всего пользователей: {len(users)}")
else:
    print("\n  [X] Пользователей пока нет")

# ========== СДАННЫЕ БАТАРЕЙКИ ==========
print("\n" + "="*70)
print("[СДАННЫЕ БАТАРЕЙКИ]")
print("="*70)
cursor.execute("""
    SELECT 
        bs.id, 
        u.username, 
        bs.quantity, 
        bs.date_submitted, 
        bs.created_at 
    FROM batteries_batterysubmission bs
    JOIN auth_user u ON bs.user_id = u.id
    ORDER BY bs.date_submitted DESC;
""")
batteries = cursor.fetchall()

if batteries:
    print(f"\n{'ID':<5} {'Пользователь':<20} {'Количество':<12} {'Дата сдачи':<20} {'Дата создания записи':<22}")
    print("-" * 85)
    
    for battery in batteries:
        battery_id = battery[0]
        username = battery[1]
        quantity = battery[2]
        date_submitted = battery[3][:16] if battery[3] else "N/A"
        created_at = battery[4][:16] if battery[4] else "N/A"
        
        print(f"{battery_id:<5} {username:<20} {quantity:<12} {date_submitted:<20} {created_at:<22}")
    
    print(f"\n[OK] Всего записей о сдаче: {len(batteries)}")
else:
    print("\n  [X] Записей о сданных батарейках пока нет")

# ========== СТАТИСТИКА ПО ПОЛЬЗОВАТЕЛЯМ ==========
print("\n" + "="*70)
print("[СТАТИСТИКА ПО ПОЛЬЗОВАТЕЛЯМ]")
print("="*70)

cursor.execute("""
    SELECT 
        u.username,
        COUNT(bs.id) as submission_count,
        COALESCE(SUM(bs.quantity), 0) as total_batteries
    FROM auth_user u
    LEFT JOIN batteries_batterysubmission bs ON u.id = bs.user_id
    GROUP BY u.id, u.username
    ORDER BY total_batteries DESC;
""")
user_stats = cursor.fetchall()

if user_stats:
    print(f"\n{'Пользователь':<20} {'Количество сдач':<18} {'Всего батареек':<18}")
    print("-" * 60)
    for stat in user_stats:
        username = stat[0]
        submission_count = stat[1]
        total_batteries = stat[2]
        print(f"{username:<20} {submission_count:<18} {total_batteries:<18}")
else:
    print("\n  [X] Данных нет")

# ========== ОБЩАЯ СТАТИСТИКА ==========
print("\n" + "="*70)
print("[ОБЩАЯ СТАТИСТИКА]")
print("="*70)

cursor.execute("SELECT COUNT(*) FROM auth_user;")
total_users = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM batteries_batterysubmission;")
total_submissions = cursor.fetchone()[0]

cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM batteries_batterysubmission;")
total_batteries = cursor.fetchone()[0]

print(f"\n  Всего пользователей:        {total_users}")
print(f"  Всего записей о сдаче:      {total_submissions}")
print(f"  Всего батареек сдано:       {total_batteries}")

if total_users > 0:
    avg_per_user = total_batteries / total_users if total_users > 0 else 0
    print(f"  Среднее на пользователя:    {avg_per_user:.1f}")

conn.close()

print("\n" + "="*70)
print("[OK] Просмотр завершен!")
print("="*70 + "\n")
