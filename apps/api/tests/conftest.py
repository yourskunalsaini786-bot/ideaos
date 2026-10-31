import os

# Set test database before any application or config modules are imported
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_ideaos.db"
os.environ["ENVIRONMENT"] = "development"
