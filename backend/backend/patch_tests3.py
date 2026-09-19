from pathlib import Path

fx_path = Path('tests/services/test_fx_service.py')
fx_content = fx_path.read_text(encoding='utf-8')
fx_content = fx_content.replace(
'''        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [mock_inst]
        db.execute.return_value = mock_result''',
'''        from unittest.mock import MagicMock
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_inst]
        db.execute.return_value = mock_result'''
)
fx_path.write_text(fx_content, encoding='utf-8')
