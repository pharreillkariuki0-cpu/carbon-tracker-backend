from django.contrib import admin
from .models import *

@admin.register(Footprint)
class FootprintAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_calculated', 'total_kg']
    list_filter = ['date_calculated']
    search_fields = ['user__username']

@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'co2_saved']
    list_filter = ['category']

@admin.register(ActionPlan)
class ActionPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'completed_at', 'is_active']

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty', 'points', 'is_active']

@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'completed', 'progress']

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'points']

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']

@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at', 'member_count']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at', 'like_count']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'published_at', 'is_published']

@admin.register(OffsetProject)
class OffsetProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'status', 'remaining_capacity']

@admin.register(OffsetPurchase)
class OffsetPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'amount_kg', 'amount_paid']

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'created_at', 'is_active']