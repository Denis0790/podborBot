import aiosqlite

DB_NAME = "telegram.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                name TEXT PRIMARY KEY,
                vin TEXT,
                year TEXT
            )
        """)
        await db.commit()


async def save_user_data(name, vin, year):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR REPLACE INTO users (name, vin, year)
            VALUES (?, ?, ?)
        """, (name, vin, year))
        await db.commit()


async def get_user_data(name):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT vin, year FROM users WHERE name = ?", (name,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0], row[1]
            return None

