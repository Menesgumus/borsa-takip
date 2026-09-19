from pathlib import Path

path = Path('tests/conftest.py')
content = path.read_text(encoding='utf-8')

defaults = '''os.environ["ENVIRONMENT"] = "test"
os.environ["POSTGRES_DB"] = "borsa_takip_test"
os.environ.setdefault("POSTGRES_HOST", "127.0.0.1")
os.environ.setdefault("POSTGRES_PORT", "5434")
os.environ.setdefault("POSTGRES_USER", "qa_user")
os.environ.setdefault("POSTGRES_PASSWORD", "qa_password")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6381/0")
os.environ.setdefault("ENABLE_MOCK_MARKET_DATA", "true")'''

content = content.replace(
    'os.environ["ENVIRONMENT"] = "test"\nos.environ["POSTGRES_DB"] = "borsa_takip_test"',
    defaults
)

path.write_text(content, encoding='utf-8')
