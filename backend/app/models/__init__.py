"""ORM models package."""

from app.models.academic_profile import AcademicProfile
from app.models.assessment import AssessmentResponse, AssessmentSession
from app.models.interest_profile import InterestProfile
from app.models.recommendation import RecommendationSet, TopicBookmark, TopicFeedback
from app.models.user import User

__all__ = [
    "AcademicProfile",
    "AssessmentResponse",
    "AssessmentSession",
    "InterestProfile",
    "RecommendationSet",
    "TopicBookmark",
    "TopicFeedback",
    "User",
]
