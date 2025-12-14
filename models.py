# models.py
# 參考資料 https://lewoudar.medium.com/fastapi-and-pagination-d27ad52983a

from pydantic import BaseModel, Field
class BookCreate(BaseModel):
    title: str = Field(..., example="My FastAPI Book")
    author: str = Field(..., example="Author Name")
    publisher: str | None = None 
    # 使用 str | None
    price: int = Field(..., gt=0, example=700)  
    # price 必須 > 0
    publish_date: str | None = None 
    isbn: str | None = None 
    cover_url: str | None = None 


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    publisher: str | None = None 
    price: int
    publish_date: str | None = None 
    isbn: str | None = None 
    # 使用 str | None
    cover_url: str | None = None 
    # 使用 str | None