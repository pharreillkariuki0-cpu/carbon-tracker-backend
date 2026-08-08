from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


# ============================================================
# USER SERIALIZERS
# ============================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


# ============================================================
# CORE SERIALIZERS
# ============================================================

class FootprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Footprint
        fields = '__all__'
        read_only_fields = ['id', 'user', 'date_calculated', 'transport_kg', 'food_kg', 'home_kg', 'shopping_kg', 'total_kg']


class TipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tip
        fields = '__all__'


# ============================================================
# FEATURE 1: ACTION PLANS
# ============================================================

class ActionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionItem
        fields = '__all__'


class ActionPlanSerializer(serializers.ModelSerializer):
    items = ActionItemSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = ActionPlan
        fields = ['id', 'user', 'created_at', 'updated_at', 'completed_at', 'is_active', 'items', 'progress']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_progress(self, obj):
        return obj.progress()


# ============================================================
# FEATURE 2: PROGRESS REPORTS
# ============================================================

class ProgressReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressReport
        fields = '__all__'


# ============================================================
# FEATURE 3: GAMIFICATION
# ============================================================

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'


class UserChallengeSerializer(serializers.ModelSerializer):
    challenge = ChallengeSerializer(read_only=True)
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = UserChallenge
        fields = ['id', 'challenge', 'started_at', 'completed_at', 'completed', 'progress', 'days_remaining']
    
    def get_days_remaining(self, obj):
        return obj.days_remaining()


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'earned_at', 'is_displayed']


class UserPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPoints
        fields = ['id', 'user', 'total', 'updated_at']


# ============================================================
# FEATURE 4: COMMUNITY
# ============================================================

class TeamSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'slug', 'created_by', 'created_at', 'is_public', 'invite_code', 'avatar', 'total_points', 'member_count', 'is_member']
    
    def get_member_count(self, obj):
        return obj.member_count()
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TeamMember
        fields = ['id', 'user', 'role', 'joined_at', 'points_contributed']


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'team', 'user', 'title', 'content', 'created_at', 'updated_at', 'likes', 'like_count', 'is_liked', 'comment_count', 'is_pinned']
    
    def get_like_count(self, obj):
        return obj.like_count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def get_comment_count(self, obj):
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at', 'updated_at']


# ============================================================
# FEATURE 6: AI RECOMMENDATIONS
# ============================================================

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'


# ============================================================
# FEATURE 7: CARBON PRICE
# ============================================================

class CarbonPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonPrice
        fields = '__all__'


# ============================================================
# FEATURE 8: BUSINESS ACCOUNTS
# ============================================================

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'


class EmployeeFootprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeFootprint
        fields = '__all__'


# ============================================================
# FEATURE 9: EDUCATIONAL CONTENT
# ============================================================

class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'category', 'category_name', 'content', 'summary', 'image', 'author', 'published_at', 'updated_at', 'is_published', 'views', 'read_time']


# ============================================================
# FEATURE 10: CARBON OFFSET
# ============================================================

class OffsetProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = OffsetProject
        fields = '__all__'


class OffsetPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OffsetPurchase
        fields = '__all__'


# ============================================================
# FEATURE 11: RESEARCH DATA
# ============================================================

class ResearchDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchDataset
        fields = '__all__'


# ============================================================
# FEATURE 12: API KEYS
# ============================================================

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['id', 'user', 'key', 'name', 'created_at', 'expires_at', 'is_active', 'rate_limit']
        read_only_fields = ['key']