from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ============================================================
# CORE MODELS
# ============================================================

class Footprint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_calculated = models.DateTimeField(auto_now_add=True)
    commute_mode = models.CharField(max_length=20)
    flights_per_year = models.IntegerField()
    diet_type = models.CharField(max_length=20)
    electricity_bill = models.CharField(max_length=10)
    shopping_frequency = models.CharField(max_length=20)
    waste_amount = models.CharField(max_length=10)
    transport_kg = models.FloatField()
    food_kg = models.FloatField()
    home_kg = models.FloatField()
    shopping_kg = models.FloatField()
    total_kg = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.date_calculated.strftime('%Y-%m-%d')}"


class Tip(models.Model):
    category = models.CharField(max_length=20)
    title = models.CharField(max_length=100)
    description = models.TextField()
    co2_saved = models.FloatField()
    icon = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.title


# ============================================================
# FEATURE 1: ACTION PLANS
# ============================================================

class ActionPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_plans')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s Action Plan"

    def progress(self):
        total = self.items.count()
        if total == 0:
            return 0
        completed = self.items.filter(status='completed').count()
        return int((completed / total) * 100)


class ActionItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    plan = models.ForeignKey(ActionPlan, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20)
    co2_saved = models.FloatField()
    week = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


# ============================================================
# FEATURE 2: PROGRESS REPORTS
# ============================================================

class ProgressReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_reports')
    week_start = models.DateField()
    week_end = models.DateField()
    total_co2 = models.FloatField()
    previous_co2 = models.FloatField(null=True, blank=True)
    improvement = models.FloatField(null=True, blank=True)
    actions_completed = models.IntegerField(default=0)
    challenges_completed = models.IntegerField(default=0)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - Week {self.week_start}"


# ============================================================
# FEATURE 3: GAMIFICATION
# ============================================================

class Challenge(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20)
    duration_days = models.IntegerField(default=7)
    co2_saved_estimate = models.FloatField()
    icon = models.CharField(max_length=50, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    points = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_challenges')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    progress = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'challenge']

    def __str__(self):
        return f"{self.user.username} - {self.challenge.name}"

    def days_remaining(self):
        if self.completed:
            return 0
        elapsed = (timezone.now() - self.started_at).days
        remaining = self.challenge.duration_days - elapsed
        return max(0, remaining)


class Badge(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    category = models.CharField(max_length=20)
    requirement = models.CharField(max_length=100)
    points = models.IntegerField(default=50)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    is_displayed = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'badge']

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    total = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.total} points"


# ============================================================
# FEATURE 4: COMMUNITY
# ============================================================

class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    invite_code = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.CharField(max_length=200, blank=True, null=True)
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()


class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    points_contributed = models.IntegerField(default=0)

    class Meta:
        unique_together = ['team', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.team.name}"


class Post(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    is_pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def like_count(self):
        return self.likes.count()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username}"


# ============================================================
# FEATURE 6: AI RECOMMENDATIONS
# ============================================================

class Recommendation(models.Model):
    TYPE_CHOICES = [
        ('product', 'Product'),
        ('service', 'Service'),
        ('provider', 'Provider'),
        ('tip', 'Tip'),
    ]
    
    category = models.CharField(max_length=20)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    co2_saved = models.FloatField()
    cost_saved = models.FloatField(null=True, blank=True)
    url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ============================================================
# FEATURE 7: CARBON PRICE
# ============================================================

class CarbonPrice(models.Model):
    price_per_kg = models.FloatField()
    currency = models.CharField(max_length=3, default='USD')
    source = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"${self.price_per_kg}/{self.currency}"


# ============================================================
# FEATURE 8: BUSINESS ACCOUNTS
# ============================================================

class Business(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    employee_count = models.IntegerField()
    subscription_tier = models.CharField(max_length=20, default='free')
    subscription_expires = models.DateTimeField(null=True, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name


class EmployeeFootprint(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    footprint = models.ForeignKey(Footprint, on_delete=models.CASCADE)
    recorded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.employee.username} - {self.business.company_name}"


# ============================================================
# FEATURE 9: EDUCATIONAL CONTENT
# ============================================================

class ArticleCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE)
    content = models.TextField()
    summary = models.TextField(blank=True)
    image = models.CharField(max_length=200, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    read_time = models.IntegerField(default=5)

    def __str__(self):
        return self.title


# ============================================================
# FEATURE 10: CARBON OFFSET
# ============================================================

class OffsetProject(models.Model):
    TYPE_CHOICES = [
        ('tree_planting', 'Tree Planting'),
        ('renewable_energy', 'Renewable Energy'),
        ('carbon_capture', 'Carbon Capture'),
        ('forest_conservation', 'Forest Conservation'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('pending', 'Pending'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    location = models.CharField(max_length=100)
    cost_per_kg = models.FloatField()
    total_capacity = models.FloatField()
    remaining_capacity = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    image = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class OffsetPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(OffsetProject, on_delete=models.CASCADE)
    amount_kg = models.FloatField()
    amount_paid = models.FloatField()
    purchased_at = models.DateTimeField(auto_now_add=True)
    receipt_url = models.URLField(blank=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.project.name}"


# ============================================================
# FEATURE 11: RESEARCH DATA
# ============================================================

class ResearchDataset(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    data = models.JSONField()
    generated_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# ============================================================
# FEATURE 12: API KEYS
# ============================================================

class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    rate_limit = models.IntegerField(default=1000)

    def __str__(self):
        return f"{self.user.username} - {self.name}"