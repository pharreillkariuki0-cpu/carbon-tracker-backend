from django.core.management.base import BaseCommand
from api.models import *

class Command(BaseCommand):
    help = 'Seed all data'

    def handle(self, *args, **kwargs):
        
        # ============================================================
        # TIPS
        # ============================================================
        tips = [
            {'category': 'transport', 'title': 'Use Public Transit', 'description': 'Take the bus or train 3 days a week instead of driving alone.', 'co2_saved': 400, 'icon': '🚌'},
            {'category': 'transport', 'title': 'Bike to Work', 'description': 'Replace 2 car trips per week with cycling.', 'co2_saved': 300, 'icon': '🚲'},
            {'category': 'food', 'title': 'Meatless Mondays', 'description': 'Skip meat one day per week.', 'co2_saved': 350, 'icon': '🌱'},
            {'category': 'home', 'title': 'Switch to LED Bulbs', 'description': 'Replace all bulbs with energy-efficient LEDs.', 'co2_saved': 150, 'icon': '💡'},
            {'category': 'shopping', 'title': 'Buy Second-hand', 'description': 'Shop at thrift stores instead of buying new.', 'co2_saved': 200, 'icon': '👕'},
        ]
        for tip_data in tips:
            Tip.objects.get_or_create(title=tip_data['title'], defaults=tip_data)
        self.stdout.write(self.style.SUCCESS('✅ Tips seeded!'))

        # ============================================================
        # CHALLENGES
        # ============================================================
        challenges = [
            {'name': '7-Day Car-Free Challenge', 'description': 'Don\'t use your car for 7 days.', 'category': 'transport', 'duration_days': 7, 'co2_saved_estimate': 25, 'icon': '🚶', 'difficulty': 'easy', 'points': 100},
            {'name': 'Meatless Week Challenge', 'description': 'Go completely meatless for 7 days.', 'category': 'food', 'duration_days': 7, 'co2_saved_estimate': 35, 'icon': '🌱', 'difficulty': 'medium', 'points': 150},
            {'name': 'Zero Waste Week', 'description': 'Produce zero landfill waste for 7 days.', 'category': 'shopping', 'duration_days': 7, 'co2_saved_estimate': 20, 'icon': '♻️', 'difficulty': 'hard', 'points': 200},
            {'name': '30-Day Plastic-Free Challenge', 'description': 'Avoid all single-use plastics for 30 days.', 'category': 'shopping', 'duration_days': 30, 'co2_saved_estimate': 50, 'icon': '🚫', 'difficulty': 'hard', 'points': 300},
            {'name': 'Energy Saving Month', 'description': 'Reduce your electricity usage by 20% for 30 days.', 'category': 'home', 'duration_days': 30, 'co2_saved_estimate': 40, 'icon': '⚡', 'difficulty': 'medium', 'points': 250},
        ]
        for challenge_data in challenges:
            Challenge.objects.get_or_create(name=challenge_data['name'], defaults=challenge_data)
        self.stdout.write(self.style.SUCCESS('✅ Challenges seeded!'))

        # ============================================================
        # BADGES
        # ============================================================
        badges = [
            {'name': 'Eco Warrior', 'description': 'Complete your first carbon calculation', 'icon': '🛡️', 'category': 'carbon', 'requirement': 'Complete 1 footprint calculation', 'points': 50},
            {'name': 'Carbon Cutter', 'description': 'Reduce your footprint by 1000kg', 'icon': '✂️', 'category': 'carbon', 'requirement': 'Reduce footprint by 1000kg CO₂', 'points': 100},
            {'name': 'Green Leader', 'description': 'Complete 5 challenges', 'icon': '🏆', 'category': 'consistency', 'requirement': 'Complete 5 challenges', 'points': 150},
            {'name': 'Consistency Champion', 'description': 'Track your footprint for 30 days straight', 'icon': '📅', 'category': 'consistency', 'requirement': 'Track footprint for 30 consecutive days', 'points': 200},
            {'name': 'Community Hero', 'description': 'Recruit 5 friends to join', 'icon': '👥', 'category': 'community', 'requirement': 'Recruit 5 new users', 'points': 100},
            {'name': 'Carbon Neutral', 'description': 'Offset 1000kg of CO₂', 'icon': '🌍', 'category': 'carbon', 'requirement': 'Offset 1000kg CO₂', 'points': 200},
            {'name': 'Action Taker', 'description': 'Complete all 4 weeks of an action plan', 'icon': '✅', 'category': 'consistency', 'requirement': 'Complete a full action plan', 'points': 150},
        ]
        for badge_data in badges:
            Badge.objects.get_or_create(name=badge_data['name'], defaults=badge_data)
        self.stdout.write(self.style.SUCCESS('✅ Badges seeded!'))

        # ============================================================
        # ARTICLE CATEGORIES
        # ============================================================
        categories = [
            {'name': 'Climate Basics', 'slug': 'climate-basics', 'description': 'Understanding climate change', 'icon': '🌍'},
            {'name': 'Sustainable Living', 'slug': 'sustainable-living', 'description': 'Everyday sustainable actions', 'icon': '🌱'},
            {'name': 'Renewable Energy', 'slug': 'renewable-energy', 'description': 'Clean energy solutions', 'icon': '☀️'},
            {'name': 'Food & Agriculture', 'slug': 'food-agriculture', 'description': 'Sustainable eating', 'icon': '🍽️'},
            {'name': 'Transportation', 'slug': 'transportation', 'description': 'Green commuting', 'icon': '🚲'},
        ]
        for category_data in categories:
            ArticleCategory.objects.get_or_create(slug=category_data['slug'], defaults=category_data)
        self.stdout.write(self.style.SUCCESS('✅ Article categories seeded!'))

        # ============================================================
        # RECOMMENDATIONS
        # ============================================================
        recommendations = [
            {'category': 'home', 'type': 'product', 'title': 'Solar Panel Installation', 'description': 'Install solar panels to generate clean energy.', 'co2_saved': 1000, 'cost_saved': 500, 'url': 'https://example.com/solar', 'is_featured': True},
            {'category': 'transport', 'type': 'service', 'title': 'Public Transit Pass', 'description': 'Monthly public transit pass to reduce car usage.', 'co2_saved': 400, 'cost_saved': 200, 'url': 'https://example.com/transit', 'is_featured': True},
            {'category': 'food', 'type': 'provider', 'title': 'Local Farmers Market', 'description': 'Buy locally grown produce to reduce food miles.', 'co2_saved': 200, 'cost_saved': 50, 'url': 'https://example.com/farmers', 'is_featured': True},
        ]
        for rec_data in recommendations:
            Recommendation.objects.get_or_create(title=rec_data['title'], defaults=rec_data)
        self.stdout.write(self.style.SUCCESS('✅ Recommendations seeded!'))

        # ============================================================
        # OFFSET PROJECTS
        # ============================================================
        offset_projects = [
            {'name': 'Amazon Rainforest Conservation', 'description': 'Protect 1000 acres of rainforest', 'type': 'forest_conservation', 'location': 'Brazil', 'cost_per_kg': 0.10, 'total_capacity': 50000, 'remaining_capacity': 50000, 'status': 'active'},
            {'name': 'Kenya Tree Planting Initiative', 'description': 'Plant trees in the Great Rift Valley', 'type': 'tree_planting', 'location': 'Kenya', 'cost_per_kg': 0.08, 'total_capacity': 30000, 'remaining_capacity': 30000, 'status': 'active'},
            {'name': 'Solar Energy Project', 'description': 'Install solar panels in rural communities', 'type': 'renewable_energy', 'location': 'India', 'cost_per_kg': 0.12, 'total_capacity': 40000, 'remaining_capacity': 40000, 'status': 'active'},
        ]
        for project_data in offset_projects:
            OffsetProject.objects.get_or_create(name=project_data['name'], defaults=project_data)
        self.stdout.write(self.style.SUCCESS('✅ Offset projects seeded!'))

        self.stdout.write(self.style.SUCCESS('🎉 All data seeded successfully!'))