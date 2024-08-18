from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Chapter(BaseModel):
    name: str
    text: str
    rating: Optional[int] = 0

class Course(BaseModel):
    name: str
    date: datetime
    description: str
    domain: List[str]
    chapters: List[Chapter]
    rating: Optional[float] = 0

class CourseListResponse(BaseModel):
    courses: List[Course]

class CourseOverviewResponse(BaseModel):
    course: Course

class ChapterInfoResponse(BaseModel):
    chapter: Chapter

class RatingRequest(BaseModel):
    rating: float
