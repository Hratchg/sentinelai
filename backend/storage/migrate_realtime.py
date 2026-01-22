"""
Database migration script for real-time surveillance features.

Creates new tables:
- persons: Face recognition and identity tracking
- person_events: Event log for person actions
- gesture_templates: Learned gesture templates
- event_clips: Video clips for important events
"""

import asyncio
from backend.storage.database import engine, Base
from backend.storage.models import Person, PersonEvent, GestureTemplate, EventClip, Job


async def run_migration():
    """Create all database tables"""
    print("Running real-time surveillance migration...")

    async with engine.begin() as conn:
        # Create all tables defined in models
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Migration complete!")
    print("\nCreated tables:")
    print("  - persons (face recognition)")
    print("  - person_events (event logging)")
    print("  - gesture_templates (learned gestures)")
    print("  - event_clips (video storage)")


if __name__ == "__main__":
    asyncio.run(run_migration())
