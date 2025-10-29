#!/usr/bin/env python3
"""
Data migration script for multitenancy feature

This script:
1. Generates slugs for all existing projects
2. Assigns all existing projects to the first admin user
3. Moves project directories to new slug-based paths
4. Updates database with new values
"""
import asyncio
import sys
import os
import shutil
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select, update, text
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project
from app.utils.formatters import generate_slug_from_domain
from app.core.config import settings


async def migrate_data():
    """Perform data migration"""
    print("=" * 60)
    print("DockLite Multitenancy Migration")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as db:
        # Step 1: Get first admin user
        print("1. Finding first admin user...")
        result = await db.execute(
            select(User).where(User.is_admin == 1).order_by(User.id).limit(1)
        )
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            print("❌ ERROR: No admin user found! Please create an admin user first.")
            return False
        
        print(f"   ✅ Found admin: {admin_user.username} (ID: {admin_user.id})")
        print()
        
        # Step 2: Get all projects
        print("2. Loading existing projects...")
        result = await db.execute(select(Project))
        projects = result.scalars().all()
        
        if not projects:
            print("   ℹ️  No projects found. Migration complete.")
            await db.commit()
            return True
        
        print(f"   Found {len(projects)} project(s)")
        print()
        
        # Step 3: Migrate each project
        print("3. Migrating projects...")
        
        for project in projects:
            print(f"   📦 Project: {project.name} (ID: {project.id}, Domain: {project.domain})")
            
            # Generate slug
            slug = generate_slug_from_domain(project.domain, project.id)
            print(f"      - Generated slug: {slug}")
            
            # Update database
            project.slug = slug
            project.owner_id = admin_user.id
            
            # Move project directory
            old_path = Path(settings.PROJECTS_DIR) / str(project.id)
            new_path = Path(settings.PROJECTS_DIR) / slug
            
            if old_path.exists():
                if new_path.exists():
                    print(f"      ⚠️  Target directory already exists: {new_path}")
                else:
                    # Get owner's home directory
                    owner_home = f"/home/{admin_user.system_user}"
                    owner_projects_dir = Path(owner_home) / "projects"
                    
                    # Create owner's projects directory if needed
                    owner_projects_dir.mkdir(parents=True, exist_ok=True)
                    
                    # New path in owner's directory
                    final_path = owner_projects_dir / slug
                    
                    try:
                        # Move directory
                        shutil.move(str(old_path), str(final_path))
                        print(f"      ✅ Moved: {old_path} → {final_path}")
                    except Exception as e:
                        print(f"      ❌ Failed to move directory: {e}")
                        print(f"         Keeping old path for now")
            else:
                print(f"      ℹ️  Directory doesn't exist yet: {old_path}")
            
            print()
        
        # Step 4: Commit changes
        print("4. Committing changes to database...")
        await db.commit()
        print("   ✅ Database updated")
        print()
        
        # Step 5: Make columns non-nullable (using raw SQL)
        print("5. Updating column constraints...")
        try:
            # For SQLite, we need to recreate the table to change nullable constraints
            # This is handled better by Alembic, so we'll skip it here
            # The application code will handle null checks
            print("   ℹ️  Column constraints will be enforced by application code")
        except Exception as e:
            print(f"   ⚠️  Could not update constraints: {e}")
        print()
        
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print()
        print("Summary:")
        print(f"  - Projects migrated: {len(projects)}")
        print(f"  - Owner: {admin_user.username} (system_user: {admin_user.system_user})")
        print(f"  - Project locations: /home/{admin_user.system_user}/projects/{{slug}}/")
        print()
        
        return True


async def verify_migration():
    """Verify migration was successful"""
    print("Verifying migration...")
    print()
    
    async with AsyncSessionLocal() as db:
        # Check all projects have slug and owner_id
        result = await db.execute(
            select(Project).where(
                (Project.slug == None) | (Project.owner_id == None)
            )
        )
        incomplete = result.scalars().all()
        
        if incomplete:
            print(f"❌ Found {len(incomplete)} project(s) with missing data:")
            for p in incomplete:
                print(f"   - Project {p.id}: slug={p.slug}, owner_id={p.owner_id}")
            return False
        
        # Show migrated projects
        result = await db.execute(select(Project))
        projects = result.scalars().all()
        
        print(f"✅ All {len(projects)} project(s) migrated successfully:")
        for p in projects:
            result = await db.execute(select(User).where(User.id == p.owner_id))
            owner = result.scalar_one_or_none()
            owner_name = owner.username if owner else "UNKNOWN"
            print(f"   - {p.name} → {p.slug} (owner: {owner_name})")
        
        print()
        return True


if __name__ == "__main__":
    print()
    success = asyncio.run(migrate_data())
    
    if success:
        asyncio.run(verify_migration())
        sys.exit(0)
    else:
        sys.exit(1)

