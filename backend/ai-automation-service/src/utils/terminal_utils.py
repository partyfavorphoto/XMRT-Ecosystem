"""
Terminal utilities for system access and diagnostics
"""

import asyncio
import subprocess
import logging

logger = logging.getLogger(__name__)

class TerminalUtils:
    def __init__(self):
        pass
    
    async def execute(self, command):
        """Execute terminal command and return output"""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return stdout.decode().strip()
            else:
                logger.warning(f"[Terminal] Command failed: {command}")
                return stderr.decode().strip()
                
        except Exception as e:
            logger.error(f"[Terminal] Execution error: {e}")
            return ""
    
    async def run_tests(self):
        """Run automated tests"""
        return await self.execute("python -m pytest tests/ -v")
    
    async def check_logs(self):
        """Check system logs for errors"""
        return await self.execute("tail -50 /var/log/*.log | grep -i error")
