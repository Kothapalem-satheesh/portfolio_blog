from django.core.management.base import BaseCommand
from django.db import transaction

from apps.portfolio.models import Education, Profile, Project, Skill
from apps.portfolio.resume_defaults import (
    DEFAULT_EDUCATION,
    DEFAULT_PROFILE,
    DEFAULT_PROJECTS,
    DEFAULT_SKILLS,
)


class Command(BaseCommand):
    help = "Seed portfolio data using resume defaults."

    def add_arguments(self, parser):
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete existing portfolio data before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        replace = options["replace"]

        if replace:
            self.stdout.write("Removing existing portfolio records...")
            Education.objects.all().delete()
            Skill.objects.all().delete()
            Project.objects.all().delete()
            Profile.objects.all().delete()

        profile_data = DEFAULT_PROFILE.copy()
        profile_data.pop("hero_video", None)
        profile, created = Profile.objects.get_or_create(
            email=profile_data["email"],
            defaults=profile_data,
        )
        if not created:
            for field, value in profile_data.items():
                setattr(profile, field, value)
            profile.save()

        for idx, edu in enumerate(DEFAULT_EDUCATION):
            Education.objects.get_or_create(
                degree=edu["degree"],
                institution=edu["institution"],
                defaults={
                    "start_year": edu["start_year"],
                    "end_year": edu["end_year"],
                    "description": edu["description"],
                    "order": idx,
                },
            )

        for idx, skill in enumerate(DEFAULT_SKILLS):
            Skill.objects.update_or_create(
                name=skill["name"],
                defaults={
                    "category": "Core",
                    "level": skill["level"],
                    "order": idx,
                },
            )

        for idx, project in enumerate(DEFAULT_PROJECTS):
            Project.objects.update_or_create(
                title=project["title"],
                defaults={
                    "summary": project["summary"],
                    "tech_stack": project.get("tech_stack", ""),
                    "source_url": project.get("source_url", ""),
                    "featured": idx < 3,
                    "order": idx,
                },
            )

        self.stdout.write(self.style.SUCCESS("Resume defaults seeded successfully."))
