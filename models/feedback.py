from typing import Optional
from sqlmodel import Field, SQLModel


class FeedbackBase(SQLModel):
    quality_rating: Optional[int] = None
    staff_attitude_rating: Optional[int] = None
    overall_satisfaction: Optional[int] = None
    comment: Optional[str] = None


class Feedback(FeedbackBase, table=True):
    __tablename__ = "Feedback"

    feedback_id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )
    visit_id: Optional[int] = Field(
        default=None, foreign_key="Visit.visit_id", unique=True
    )


class FeedbackCreate(FeedbackBase):
    visit_id: Optional[int] = None


class FeedbackRead(FeedbackBase):
    feedback_id: int
    visit_id: Optional[int]


class FeedbackUpdate(SQLModel):
    quality_rating: Optional[int] = None
    staff_attitude_rating: Optional[int] = None
    overall_satisfaction: Optional[int] = None
    comment: Optional[str] = None
