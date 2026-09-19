from pathlib import Path

fx_path = Path('tests/services/test_fx_service.py')
content = fx_path.read_text(encoding='utf-8')
content = content.replace('mock_result = AsyncMock()', 'from unittest.mock import MagicMock\n        mock_result = MagicMock()')
fx_path.write_text(content, encoding='utf-8')
