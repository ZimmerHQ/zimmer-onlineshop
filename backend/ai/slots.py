from typing import Optional
from pydantic import BaseModel, Field

class SlotFrame(BaseModel):
    product_code: Optional[str] = Field(None, description="کد محصول مثل A0001 اگر کاربر اشاره کرد")
    quantity: Optional[int] = Field(None, description="تعداد درخواستی (اگر گفت مثلا ۲ تا)")
    size: Optional[str] = Field(None, description="سایز یا اندازه (مثلا M, L, 43)")
    color: Optional[str] = Field(None, description="رنگ (مثلا مشکی، سفید)")
    confirm: Optional[bool] = Field(None, description="آیا کاربر تایید نهایی را اعلام کرد یا نه")
