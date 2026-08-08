from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import *
from .serializers import *
from .calculations import calculate_footprint


# ============================================================
# AUTH VIEWS
# ============================================================

class RegisterViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            UserPoints.objects.get_or_create(user=user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })


# ============================================================
# CORE VIEWS
# ============================================================

class FootprintViewSet(viewsets.ModelViewSet):
    serializer_class = FootprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Footprint.objects.filter(user=self.request.user)

    def create(self, request):
        data = request.data
        results = calculate_footprint(data)
        
        footprint = Footprint.objects.create(
            user=request.user,
            commute_mode=data.get('commute_mode', 'car'),
            flights_per_year=int(data.get('flights_per_year', 0)),
            diet_type=data.get('diet_type', 'mixed'),
            electricity_bill=data.get('electricity_bill', 'medium'),
            shopping_frequency=data.get('shopping_frequency', 'few-months'),
            waste_amount=data.get('waste_amount', 'average'),
            transport_kg=results['transport_kg'],
            food_kg=results['food_kg'],
            home_kg=results['home_kg'],
            shopping_kg=results['shopping_kg'],
            total_kg=results['total_kg']
        )
        
        # Award Eco Warrior badge for first calculation
        if Footprint.objects.filter(user=request.user).count() == 1:
            badge = Badge.objects.filter(name='Eco Warrior').first()
            if badge:
                UserBadge.objects.get_or_create(user=request.user, badge=badge)
                points, _ = UserPoints.objects.get_or_create(user=request.user)
                points.total += badge.points
                points.save()
        
        serializer = self.get_serializer(footprint)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        footprints = Footprint.objects.filter(user=request.user)
        
        if not footprints.exists():
            return Response({
                'total_calculations': 0,
                'latest_total': 0,
                'average_total': 0,
                'improvement': 0,
            })
        
        latest = footprints.first()
        total = footprints.count()
        average = footprints.aggregate(Avg('total_kg'))['total_kg__avg']
        first = footprints.last()
        improvement = first.total_kg - latest.total_kg if total > 1 else 0
        
        return Response({
            'total_calculations': total,
            'latest_total': latest.total_kg,
            'average_total': round(average, 2),
            'improvement': round(improvement, 2)
        })


class TipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tip.objects.all()
    serializer_class = TipSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def personalized(self, request):
        latest = Footprint.objects.filter(user=request.user).first()
        
        if not latest:
            tips = Tip.objects.all()
        else:
            categories = {
                'transport': latest.transport_kg,
                'food': latest.food_kg,
                'home': latest.home_kg,
                'shopping': latest.shopping_kg
            }
            highest = max(categories, key=categories.get)
            tips = Tip.objects.filter(category=highest)
            if not tips:
                tips = Tip.objects.all()
        
        serializer = self.get_serializer(tips, many=True)
        return Response(serializer.data)


# ============================================================
# FEATURE 1: ACTION PLANS
# ============================================================

class ActionPlanViewSet(viewsets.ModelViewSet):
    serializer_class = ActionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ActionPlan.objects.filter(user=self.request.user)

    def create(self, request):
        user = request.user
        latest_footprint = Footprint.objects.filter(user=user).first()
        
        if not latest_footprint:
            return Response(
                {'error': 'Please calculate your footprint first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        categories = {
            'transport': latest_footprint.transport_kg,
            'food': latest_footprint.food_kg,
            'home': latest_footprint.home_kg,
            'shopping': latest_footprint.shopping_kg
        }
        highest = max(categories, key=categories.get)
        tips = Tip.objects.filter(category=highest)[:4]
        
        plan = ActionPlan.objects.create(user=user, is_active=True)
        
        week = 1
        for tip in tips:
            ActionItem.objects.create(
                plan=plan,
                title=tip.title,
                description=tip.description,
                category=tip.category,
                co2_saved=tip.co2_saved,
                week=week,
                order=week
            )
            week += 1
        
        serializer = self.get_serializer(plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def complete_item(self, request, pk=None):
        plan = self.get_object()
        item_id = request.data.get('item_id')
        
        try:
            item = ActionItem.objects.get(id=item_id, plan=plan)
            item.status = 'completed'
            item.completed_at = timezone.now()
            item.save()
            
            if plan.items.filter(status__in=['pending', 'in_progress']).count() == 0:
                plan.completed_at = timezone.now()
                plan.is_active = False
                plan.save()
                
                badge = Badge.objects.filter(name='Action Taker').first()
                if badge:
                    UserBadge.objects.get_or_create(user=request.user, badge=badge)
                    points, _ = UserPoints.objects.get_or_create(user=request.user)
                    points.total += badge.points
                    points.save()
            
            return Response({'status': 'completed'})
        except ActionItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)


# ============================================================
# FEATURE 2: PROGRESS REPORTS
# ============================================================

class ProgressReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProgressReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProgressReport.objects.filter(user=self.request.user).order_by('-week_start')

    @action(detail=False, methods=['get'])
    def latest(self, request):
        report = ProgressReport.objects.filter(user=request.user).order_by('-week_start').first()
        if report:
            serializer = self.get_serializer(report)
            return Response(serializer.data)
        return Response({'message': 'No reports yet'}, status=status.HTTP_404_NOT_FOUND)


# ============================================================
# FEATURE 3: GAMIFICATION
# ============================================================

class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Challenge.objects.filter(is_active=True)
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        challenge = self.get_object()
        user_challenge, created = UserChallenge.objects.get_or_create(
            user=request.user,
            challenge=challenge,
            defaults={'progress': 0}
        )
        
        if not created and not user_challenge.completed:
            return Response(
                {'error': 'Already joined this challenge'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserChallengeSerializer(user_challenge)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        challenge = self.get_object()
        progress = request.data.get('progress', 0)
        
        try:
            user_challenge = UserChallenge.objects.get(
                user=request.user,
                challenge=challenge,
                completed=False
            )
            user_challenge.progress = min(progress, 100)
            
            if user_challenge.progress >= 100:
                user_challenge.completed = True
                user_challenge.completed_at = timezone.now()
                
                points, _ = UserPoints.objects.get_or_create(user=request.user)
                points.total += challenge.points
                points.save()
                
                completed_count = UserChallenge.objects.filter(
                    user=request.user,
                    completed=True
                ).count()
                
                if completed_count >= 5:
                    badge = Badge.objects.filter(name='Green Leader').first()
                    if badge:
                        UserBadge.objects.get_or_create(user=request.user, badge=badge)
                        points.total += badge.points
                        points.save()
            
            user_challenge.save()
            serializer = UserChallengeSerializer(user_challenge)
            return Response(serializer.data)
        except UserChallenge.DoesNotExist:
            return Response(
                {'error': 'Challenge not found or already completed'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserChallenge.objects.filter(user=self.request.user)


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user)


class UserPointsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserPointsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPoints.objects.filter(user=self.request.user)


# ============================================================
# FEATURE 4: COMMUNITY
# ============================================================

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Team.objects.filter(is_public=True)

    def create(self, request):
        data = request.data
        data['created_by'] = request.user.id
        
        import re
        slug = re.sub(r'[^a-zA-Z0-9-]', '-', data['name'].lower())
        data['slug'] = slug
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            team = serializer.save(created_by=request.user)
            team.members.add(request.user)
            TeamMember.objects.create(team=team, user=request.user, role='admin')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        team = self.get_object()
        if team.members.filter(id=request.user.id).exists():
            return Response({'error': 'Already a member'}, status=status.HTTP_400_BAD_REQUEST)
        
        team.members.add(request.user)
        TeamMember.objects.create(team=team, user=request.user, role='member')
        
        points, _ = UserPoints.objects.get_or_create(user=request.user)
        team.total_points += points.total
        team.save()
        
        return Response({'message': 'Joined team successfully'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        team = self.get_object()
        if not team.members.filter(id=request.user.id).exists():
            return Response({'error': 'Not a member'}, status=status.HTTP_400_BAD_REQUEST)
        
        team.members.remove(request.user)
        TeamMember.objects.filter(team=team, user=request.user).delete()
        return Response({'message': 'Left team successfully'})

    @action(detail=False, methods=['get'])
    def my_teams(self, request):
        teams = Team.objects.filter(members=request.user)
        serializer = self.get_serializer(teams, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        team = self.get_object()
        members = TeamMember.objects.filter(team=team).order_by('-points_contributed')[:10]
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        team_id = self.request.query_params.get('team')
        if team_id:
            return Post.objects.filter(team_id=team_id)
        return Post.objects.all()

    def create(self, request):
        data = request.data
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            return Response({'message': 'Unliked'})
        else:
            post.likes.add(request.user)
            return Response({'message': 'Liked'})


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.request.query_params.get('post')
        if post_id:
            return Comment.objects.filter(post_id=post_id)
        return Comment.objects.none()

    def create(self, request):
        data = request.data
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# FEATURE 6: AI RECOMMENDATIONS
# ============================================================

class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def personalized(self, request):
        latest = Footprint.objects.filter(user=request.user).first()
        
        if not latest:
            recommendations = Recommendation.objects.filter(is_featured=True)
        else:
            categories = {
                'transport': latest.transport_kg,
                'food': latest.food_kg,
                'home': latest.home_kg,
                'shopping': latest.shopping_kg
            }
            highest = max(categories, key=categories.get)
            recommendations = Recommendation.objects.filter(category=highest)
            if not recommendations:
                recommendations = Recommendation.objects.filter(is_featured=True)
        
        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)


# ============================================================
# FEATURE 7: CARBON PRICE
# ============================================================

class CarbonPriceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CarbonPrice.objects.all()
    serializer_class = CarbonPriceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def latest(self, request):
        price = CarbonPrice.objects.order_by('-updated_at').first()
        if price:
            serializer = self.get_serializer(price)
            return Response(serializer.data)
        return Response({'error': 'No price data available'}, status=status.HTTP_404_NOT_FOUND)


# ============================================================
# FEATURE 8: BUSINESS ACCOUNTS
# ============================================================

class BusinessViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Business.objects.filter(user=self.request.user)

    def create(self, request):
        data = request.data
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        business = Business.objects.filter(user=request.user).first()
        if not business:
            return Response({'error': 'No business found'}, status=status.HTTP_404_NOT_FOUND)
        
        employee_count = EmployeeFootprint.objects.filter(business=business).count()
        total_footprint = EmployeeFootprint.objects.filter(business=business).aggregate(
            total=Sum('footprint__total_kg')
        )['total'] or 0
        
        return Response({
            'employee_count': employee_count,
            'total_footprint': total_footprint,
            'average_footprint': total_footprint / employee_count if employee_count > 0 else 0
        })


class EmployeeFootprintViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeFootprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        business = Business.objects.filter(user=self.request.user).first()
        if business:
            return EmployeeFootprint.objects.filter(business=business)
        return EmployeeFootprint.objects.none()


# ============================================================
# FEATURE 9: EDUCATIONAL CONTENT
# ============================================================

class ArticleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArticleCategory.objects.all()
    serializer_class = ArticleCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.filter(is_published=True)
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        article = self.get_object()
        article.views += 1
        article.save()
        return Response({'views': article.views})

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_slug = request.query_params.get('category')
        if category_slug:
            articles = Article.objects.filter(category__slug=category_slug, is_published=True)
            serializer = self.get_serializer(articles, many=True)
            return Response(serializer.data)
        return Response({'error': 'Category slug required'}, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# FEATURE 10: CARBON OFFSET
# ============================================================

class OffsetProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OffsetProject.objects.filter(status='active')
    serializer_class = OffsetProjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class OffsetPurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = OffsetPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OffsetPurchase.objects.filter(user=self.request.user)

    def create(self, request):
        data = request.data
        data['user'] = request.user.id
        
        project = OffsetProject.objects.get(id=data['project'])
        amount_kg = float(data.get('amount_kg', 0))
        amount_paid = amount_kg * project.cost_per_kg
        
        if project.remaining_capacity < amount_kg:
            return Response(
                {'error': 'Not enough capacity available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data['amount_paid'] = amount_paid
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            project.remaining_capacity -= amount_kg
            project.save()
            serializer.save(user=request.user)
            
            # Award badge for offsetting
            if amount_kg >= 1000:
                badge = Badge.objects.filter(name='Carbon Neutral').first()
                if badge:
                    UserBadge.objects.get_or_create(user=request.user, badge=badge)
                    points, _ = UserPoints.objects.get_or_create(user=request.user)
                    points.total += badge.points
                    points.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# FEATURE 11: RESEARCH DATA
# ============================================================

class ResearchDatasetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResearchDataset.objects.filter(is_public=True)
    serializer_class = ResearchDatasetSerializer
    permission_classes = [permissions.AllowAny]


# ============================================================
# FEATURE 12: API KEYS
# ============================================================

class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def create(self, request):
        data = request.data
        data['user'] = request.user.id
        import secrets
        data['key'] = secrets.token_urlsafe(32)
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)