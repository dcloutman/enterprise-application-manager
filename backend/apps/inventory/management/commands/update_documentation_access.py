from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.inventory.models import UserProfile


class Command(BaseCommand):
    help = 'Update documentation access for existing users based on their roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )

        # Get all users
        users = User.objects.all()
        updated_count = 0
        created_count = 0

        for user in users:
            try:
                profile = user.profile
                old_access = profile.has_documentation_access
                
                # Apply documentation access rules based on role
                if profile.role == 'application_admin':
                    # Application admins always have access (non-revokable)
                    new_access = True
                elif profile.role == 'systems_manager':
                    # Systems managers get access by default but it's revokable
                    new_access = True
                else:
                    # Other roles don't get automatic access
                    new_access = profile.has_documentation_access  # Keep existing setting
                
                if old_access != new_access:
                    if not dry_run:
                        profile.has_documentation_access = new_access
                        profile.save()
                    
                    updated_count += 1
                    self.stdout.write(
                        f"{'Would update' if dry_run else 'Updated'} {user.username} "
                        f"({profile.get_role_display()}): {old_access} -> {new_access}"
                    )
                else:
                    self.stdout.write(
                        f"No change needed for {user.username} "
                        f"({profile.get_role_display()}): {old_access}"
                    )
                    
            except UserProfile.DoesNotExist:
                # Create missing profile with appropriate documentation access
                if user.is_superuser:
                    role = 'application_admin'
                    doc_access = True
                else:
                    role = 'business_user'
                    doc_access = False
                
                if not dry_run:
                    UserProfile.objects.create(
                        user=user,
                        role=role,
                        has_documentation_access=doc_access
                    )
                
                created_count += 1
                self.stdout.write(
                    f"{'Would create' if dry_run else 'Created'} profile for {user.username} "
                    f"with role {role} and documentation access: {doc_access}"
                )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'Would update' if dry_run else 'Updated'} {updated_count} existing profiles"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"{'Would create' if dry_run else 'Created'} {created_count} new profiles"
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\nRun without --dry-run to apply these changes'
                )
            )
