import asyncio
import logging
import subprocess
import sys

from app.scripts.seed_bist100 import seed_bist100

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bootstrap")

def run_migrations():
    logger.info("Running database migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        logger.error(f"Migration failed:\n{result.stderr}")
        sys.exit(1)
    logger.info("Migrations completed successfully.")

async def run_seeds():
    logger.info("Seeding BIST100 instruments...")
    await seed_bist100()
    logger.info("Seeding completed.")

def main():
    run_migrations()
    asyncio.run(run_seeds())
    logger.info("Bootstrap finished. System ready.")

if __name__ == "__main__":
    main()
