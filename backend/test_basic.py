"""Basic test to verify pytest setup"""
import pytest

def test_basic_functionality():
    """Test basic Python functionality"""
    assert 1 + 1 == 2
    assert "hello" == "hello"
    assert len([1, 2, 3]) == 3

def test_imports():
    """Test that basic imports work"""
    import json
    import os
    import sys
    assert json.dumps({"test": "value"}) == '{"test": "value"}'
    assert os.path.exists(".")
    assert sys.version_info.major >= 3

@pytest.mark.asyncio
async def test_async_functionality():
    """Test async functionality"""
    import asyncio
    await asyncio.sleep(0.001)
    assert True
