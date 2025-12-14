# main.py
from fastapi import FastAPI, HTTPException, Query 
# Query(/posts?page=2):選填。用來過濾、搜尋、分頁
from models import BookCreate, BookResponse
# 引入資料庫模組
import database

# 建立 FastAPI 應用實例

app = FastAPI(title="AI Books API")

#  定義路由 (Route) 與 HTTP 方法 (GET)
@app.get("/", response_model=dict)
def root():
    #  回傳資料 (FastAPI 會自動轉成 JSON 格式)
    return {"message": "/AI/Books/API"}

# 取得書籍列表清單（GET /books）
@app.get("/books", response_model=list[BookResponse]) 
def get_books(
    # 跳過幾筆，GET http://127.0.0.1:8000/books?skip=0&limit=5
    skip: int = Query(0, ge=0),
    # 取幾筆
    limit: int = Query(10, ge=1)
):
    """分頁取書籍"""
    books = database.get_all_books(skip=skip, limit=limit)
    return books

# 取得單一本書
# http://127.0.0.1:8000/books/2 
@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    """取得單一本書"""
    #  去資料庫撈書籍資料
    book = database.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="找不到要的 Book")
    return book

#  新增書籍 POST
@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate):
    """新增一本書"""
    # 寫進資料庫，拿到新書的 id
    new_id = database.create_book(
        book.title, book.author, book.publisher,
        book.price, book.publish_date, book.isbn, book.cover_url
    )
    new_book = database.get_book_by_id(new_id)
    # 回傳完整新書（含 id、created_at）
    return new_book

#  更新書籍（PUT /books/{book_id}）
@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookCreate):
    """完整更新一本書"""
    #  避免更新不存在的資料
    exists = database.get_book_by_id(book_id)
    if not exists:
        raise HTTPException(status_code=404, detail="找不到要更新的 Book ")

    updated = database.update_book(
        book_id, book.title, book.author, book.publisher,
        book.price, book.publish_date, book.isbn, book.cover_url
    )

    if not updated:
        raise HTTPException(status_code=404, detail="找不到要更新 Book")
    return database.get_book_by_id(book_id)

#  刪除書籍（DELETE /books/{book_id}）
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    """刪除書籍"""
    success = database.delete_book(book_id)
    if not success:
        # 拋出 HTTP 404 異常
        raise HTTPException(status_code=404, detail="找不到要刪除的 Book")
    return None