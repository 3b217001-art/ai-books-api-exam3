import sqlite3  # 導入 SQLite3 資料庫模組
# import pprint  # 用於除錯時美化輸出格式，目前未使用

# 定義資料庫檔案名稱
DB_NAME = "bokelai.db"

def get_db_connection() -> sqlite3.Connection:
    """建立並返回一個資料庫連接，並啟用 Row factory"""
    try:
        # 建立與資料庫的連接
        conn = sqlite3.connect(DB_NAME)
        # 設定 row_factory 為 Row，使查詢結果可以用字典方式存取
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        # 如果連接失敗，印出錯誤訊息並往上拋出例外
        print(f"連接資料庫失敗：{e}")
        raise
# 查全部書籍 預設 0~10 筆
def get_all_books(skip: int = 0, limit: int = 10) -> list[dict]:
    """取得所有書籍（支援 skip & limit 分頁）"""
    conn = get_db_connection()
    cursor = conn.cursor()
#  LIMIT：一次拿幾筆， OFFSET：跳過幾筆
    cursor.execute(
        "SELECT * FROM books ORDER BY id LIMIT ? OFFSET ?;",
        (limit, skip)
    )

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# 根據 ID 查書  

def get_book_by_id(book_id: int) -> dict | None:
    """用 ID 查詢書籍"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE id = ?;", (book_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# 新增書籍，回傳新增的書籍 id
def create_book(
    title: str,
    author: str,
    publisher: str | None,
    price: int,
    publish_date: str | None,
    isbn: str | None,
    cover_url: str | None,
) -> int:
    """新增一本書，回傳新增的書籍 id"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO books
        (title, author, publisher, price, publish_date, isbn, cover_url)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (title, author, publisher, price, publish_date, isbn, cover_url),
    )
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

#  更新書籍
def update_book(
    book_id: int,
    title: str,
    author: str,
    publisher: str | None,
    price: int,
    publish_date: str | None,
    isbn: str | None,
    cover_url: str | None,
) -> bool:
    """完整更新一本書，有回傳是否成功更新"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE books
        SET title=?, author=?, publisher=?, price=?, publish_date=?, isbn=?, cover_url=?
        WHERE id = ?;
        """,
        (title, author, publisher, price, publish_date, isbn, cover_url, book_id),
    )
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    return changed

# 刪除書籍
def delete_book(book_id: int) -> bool:
    """刪除書籍（根據 id）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?;", (book_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# 批量存入書籍資料
def save_books_to_db(books: list[dict[str, str | int]]) -> int:
    """
    將書籍列表批量存入資料庫，使用 INSERT OR IGNORE 避免重複。

    Args:
        books (list[dict]): 從爬蟲獲取的書籍資料列表。

    Returns:
        int: 成功插入資料庫的新紀錄數量。
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 取得插入前的記錄數量
            cursor.execute("SELECT COUNT(*) FROM llm_books")
            count_before = cursor.fetchone()[0]

            # 將書籍資料轉換為元組列表，準備批量插入
            books_to_insert = [
                (book["title"], book["author"], book["price"], book["link"])
                for book in books
            ]

            # Debug 用：印出要插入的資料
            # pprint.pprint(books_to_insert)

            # 使用 INSERT OR IGNORE 批量插入資料
            # 當遇到重複的 title 時會自動跳過
            cursor.executemany(
                """
                INSERT OR IGNORE INTO llm_books (title, author, price, link)
                VALUES (?, ?, ?, ?)
            """,
                books_to_insert,
            )
            # 提交變更
            conn.commit()

            # 取得插入後的記錄數量
            cursor.execute("SELECT COUNT(*) FROM llm_books")
            count_after = cursor.fetchone()[0]

            # 返回新增的記錄數量
            return count_after - count_before
    except sqlite3.Error as e:
        print(f"儲存資料失敗：{e}")
        raise


def search_books_by_keyword(column: str, keyword: str) -> list[sqlite3.Row]:
    """
    根據指定的欄位和關鍵字(模糊查詢)來查詢書籍。

    Args:
        column (str): 要查詢的欄位名稱 ('title' 或 'author')。
        keyword (str): 用於模糊比對的關鍵字。

    Returns:
        list[sqlite3.Row]: 查詢結果的列表。
    """
    try:
        # 檢查查詢欄位是否有效
        if column not in ["title", "author"]:
            raise ValueError("查詢欄位只能是 'title' 或 'author'")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 使用參數化查詢來防止 SQL 注入
            # LIKE 運算符配合 % 實現模糊查詢
            query = f"SELECT * FROM llm_books WHERE {column} LIKE ?"
            cursor.execute(query, (f"%{keyword}%",))
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"查詢資料失敗：{e}")
        raise