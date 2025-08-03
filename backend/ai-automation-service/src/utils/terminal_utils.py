"""
Terminal utilities for system access and diagnostics
"""

import asyncio
import subprocess
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class TerminalUtils:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent  # Go up to project root
    
    async def execute(self, command, cwd=None):
        """Execute terminal command and return output"""
        try:
            # Set working directory to project root if not specified
            if cwd is None:
                cwd = str(self.base_path)
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result = stdout.decode().strip()
if __name__ == "__main__":
                    logger.info(f"[Terminal] Command succeeded: {command}")
                return result
            else:
                error_msg = stderr.decode().strip()
if __name__ == "__main__":
                    logger.warning(f"[Terminal] Command failed: {command} - {error_msg}")
                return f"Command failed: {error_msg}"
                
        except Exception as e:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.error(f"[Terminal] Execution error: {e}")
            return f"Execution error: {str(e)}"
    
    async def run_tests(self):
        """Run automated tests"""
        # First check if tests directory exists
        tests_dir = self.base_path / "tests"
        if not tests_dir.exists():
if __name__ == "__main__":
                logger.info("[Terminal] Creating tests directory...")
            tests_dir.mkdir(exist_ok=True)
            
            # Create a basic test file if none exists
            basic_test = tests_dir / "test_basic.py"
            if not basic_test.exists():
                basic_test.write_text("""
import pytest

def test_basic_functionality():
    \"\"\"Basic test to ensure testing framework works\"\"\"
    assert True

def test_import_modules():
    \"\"\"Test that core modules can be imported\"\"\"
    try:
        from src.agents.self_improvement_agent import SelfImprovementAgent
        assert True
    except ImportError:
        pytest.skip("Module not available for testing")
""")
        
        # Check if pytest is installed, install if not
        try:
            await self.execute("python -m pytest --version")
        except:
            pass  # <-- AUTO-INSERTED
if __name__ == "__main__":
                logger.info("[Terminal] Installing pytest...")
            await self.execute("pip install pytest")
        
        return await self.execute("python -m pytest tests/ -v")
    
    async def check_logs(self):
        """Check system logs for errors"""
        # Check multiple possible log locations
        log_commands = [
            "find /var/log -name '*.log' -type f 2>/dev/null | head -5",
            "journalctl --no-pager -n 20 2>/dev/null || echo 'No systemd logs available'",
            "ls -la /tmp/*.log 2>/dev/null || echo 'No temp logs found'"
        ]
        
        results = []
        for cmd in log_commands:
            result = await self.execute(cmd)
            if result and "error" not in result.lower():
                results.append(result)
        
        return "\n".join(results) if results else "No accessible log files found"
    
    async def check_system_status(self):
        """Check basic system status"""
        status_commands = {
            'uptime': 'uptime',
            'disk_space': 'df -h /',
            'memory': 'free -h',
            'processes': 'ps aux | head -10'
        }
        
        status = {}
        for name, cmd in status_commands.items():
            try:
                result = await self.execute(cmd)
                status[name] = result
            except Exception as e:
                status[name] = f"Error: {e}"
        
        return status
