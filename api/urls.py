from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

# Core
router.register(r'footprints', FootprintViewSet, basename='footprint')
router.register(r'tips', TipViewSet, basename='tip')
router.register(r'register', RegisterViewSet, basename='register')

# Feature 1: Action Plans
router.register(r'action-plans', ActionPlanViewSet, basename='actionplan')

# Feature 2: Progress Reports
router.register(r'progress-reports', ProgressReportViewSet, basename='progressreport')

# Feature 3: Gamification
router.register(r'challenges', ChallengeViewSet, basename='challenge')
router.register(r'my-challenges', UserChallengeViewSet, basename='mychallenge')
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'my-badges', UserBadgeViewSet, basename='mybadge')
router.register(r'my-points', UserPointsViewSet, basename='mypoints')

# Feature 4: Community
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

# Feature 6: AI Recommendations
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

# Feature 7: Carbon Price
router.register(r'carbon-price', CarbonPriceViewSet, basename='carbonprice')

# Feature 8: Business Accounts
router.register(r'business', BusinessViewSet, basename='business')
router.register(r'employee-footprints', EmployeeFootprintViewSet, basename='employeefootprint')

# Feature 9: Educational Content
router.register(r'article-categories', ArticleCategoryViewSet, basename='articlecategory')
router.register(r'articles', ArticleViewSet, basename='article')

# Feature 10: Carbon Offset
router.register(r'offset-projects', OffsetProjectViewSet, basename='offsetproject')
router.register(r'offset-purchases', OffsetPurchaseViewSet, basename='offsetpurchase')

# Feature 11: Research Data
router.register(r'research-datasets', ResearchDatasetViewSet, basename='researchdataset')

# Feature 12: API Keys
router.register(r'api-keys', APIKeyViewSet, basename='apikey')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
]