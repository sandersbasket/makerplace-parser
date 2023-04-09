import sqlite3

class Database:
    def __init__(self, db_file):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file, check_same_thread = False)
        except sqlite3.Error as e:
            print(e)

    def add_address(self, address: int, balance: int, social_links: dict) -> None:
        sql = '''INSERT INTO users(address, balance, social_links) VALUES(?,?,?)'''
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(sql, (address, balance, str(social_links)))

    def is_address_exists(self, address: int) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE address = ?", (address,))
        rows = cur.fetchall()
        if len(rows) > 0:
            return True
        return False

    def add_index_page(self, index_page: int) -> None:
        sql = '''INSERT INTO index_pages("index") VALUES(?)'''
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(sql, (index_page,))

    def get_last_index_page(self) -> int:
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM index_pages ORDER BY "index" DESC LIMIT 1')
        row = cur.fetchone()
        if row:
            return row[0]
        return None