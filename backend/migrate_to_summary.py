"""
Migration script to update database schema from classification to summary
Run this to migrate existing database
"""
import asyncio
from sqlalchemy import text
from app.database import get_db_engine

async def migrate():
    engine = get_db_engine()

    async with engine.begin() as conn:
        print("Starting migration...")

        # First, update the enum type to include 'completed'
        print("Adding 'completed' to enum...")
        try:
            await conn.execute(text("""
                ALTER TYPE documentstatus ADD VALUE IF NOT EXISTS 'completed'
            """))
        except Exception as e:
            print(f"Note: {e}")

        # Update status values BEFORE modifying enum
        print("Updating status values from 'classified' to 'completed'...")
        await conn.execute(text("""
            UPDATE documents
            SET status = 'completed'::text::documentstatus
            WHERE status::text = 'classified'
        """))

        # Add new columns
        print("Adding summary column...")
        await conn.execute(text("""
            ALTER TABLE documents
            ADD COLUMN IF NOT EXISTS summary TEXT
        """))

        print("Adding summary_completed_at column...")
        await conn.execute(text("""
            ALTER TABLE documents
            ADD COLUMN IF NOT EXISTS summary_completed_at TIMESTAMP WITH TIME ZONE
        """))

        # Drop old columns
        print("Dropping document_type column...")
        await conn.execute(text("""
            ALTER TABLE documents
            DROP COLUMN IF EXISTS document_type
        """))

        print("Dropping classification_confidence column...")
        await conn.execute(text("""
            ALTER TABLE documents
            DROP COLUMN IF EXISTS classification_confidence
        """))

        print("Dropping classified_at column...")
        await conn.execute(text("""
            ALTER TABLE documents
            DROP COLUMN IF EXISTS classified_at
        """))

        print("Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(migrate())
