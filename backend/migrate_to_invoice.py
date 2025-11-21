"""
Migration script to replace summary with invoice_data
"""
import asyncio
from sqlalchemy import text
from app.database import async_session


async def migrate():
    async with async_session() as session:
        async with session.begin():
            print("🔄 Starting migration to invoice extraction schema...")

            # Add new invoice columns
            print("Adding invoice_data column...")
            await session.execute(text(
                "ALTER TABLE documents ADD COLUMN IF NOT EXISTS invoice_data JSON"
            ))

            print("Adding invoice_extracted_at column...")
            await session.execute(text(
                "ALTER TABLE documents ADD COLUMN IF NOT EXISTS invoice_extracted_at TIMESTAMP WITH TIME ZONE"
            ))

            # Drop old summary columns
            print("Dropping old summary column...")
            await session.execute(text(
                "ALTER TABLE documents DROP COLUMN IF EXISTS summary"
            ))

            print("Dropping old summary_completed_at column...")
            await session.execute(text(
                "ALTER TABLE documents DROP COLUMN IF EXISTS summary_completed_at"
            ))

            print("✅ Migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(migrate())
