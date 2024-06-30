
import sqlite3

class DbContext:
    def __init__(self, db_name="a7.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS airdrops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            link TEXT NOT NULL
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            referrals INTEGER DEFAULT 0
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            referrer_id INTEGER,
            referred_id INTEGER,
            FOREIGN KEY (referrer_id) REFERENCES users(user_id),
            FOREIGN KEY (referred_id) REFERENCES users(user_id)
        )
        ''')
        self.conn.commit()

    def add_user(self, user_id, name):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)', (user_id, name))
        self.conn.commit()

    def update_referral(self, referrer_id, referred_id, referred_name, referrer_name):
        self.add_user(referrer_id, referrer_name)
        self.add_user(referred_id, referred_name)
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM referrals WHERE referred_id = ?', (referred_id,))
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)', (referrer_id, referred_id))
            cursor.execute('UPDATE users SET referrals = referrals + 1 WHERE user_id = ?', (referrer_id,))
            self.conn.commit()
            return True
        return False

    def get_leaderboard(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT name, referrals FROM users ORDER BY referrals DESC LIMIT 10')
        return cursor.fetchall()
    
    def add_airdrop(self, name, link):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO airdrops (name, link) VALUES (?, ?)', (name, link))
        self.conn.commit()

    def get_airdrops(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, link FROM airdrops')
        rows = cursor.fetchall()
        return rows

    def edit_airdrop(self, id, name, link):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE airdrops SET name = ?, link = ? WHERE id = ?', (name, link, id))
        self.conn.commit()

    def delete_airdrop(self, id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM airdrops WHERE id = ?', (id,))
        self.conn.commit()

# Initialize the database context
db = DbContext()
