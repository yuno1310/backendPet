from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional

# --- Model cho Kịch bản 5 ---
class MedicalHistoryResponse(BaseModel):
    MedicalID: int
    CreatedDate: Optional[datetime]
    Diagnosis: Optional[str]
    Symptoms: Optional[str]

# --- Model cho Kịch bản 6 ---
class AnnualRevenueResponse(BaseModel):
    BranchName: str
    Year: int
    Revenue: Optional[Decimal] # Dùng Decimal vì tiền tệ trong SQL là DECIMAL