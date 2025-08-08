#!/usr/bin/env python3
'''
XMRT Ecosystem Bot Deployment Script
Handles deployment and management of multi-platform bots
'''

import asyncio
import logging
import signal
import sys
from multiplatform_bot_manager import bot_manager
from bot_config import BotConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xmrt_bots.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class BotDeployment:
    '''Handles bot deployment and lifecycle management'''
    
    def __init__(self):
        self.bot_manager = bot_manager
        self.running = False
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        '''Setup signal handlers for graceful shutdown'''
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        '''Handle shutdown signals'''
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
    
    async def deploy(self):
        '''Deploy all bots'''
        logger.info("Starting XMRT Ecosystem Bot Deployment")
        
        # Check platform configurations
        enabled_platforms = BotConfig.get_enabled_platforms()
        
        if not enabled_platforms:
            logger.error("No platforms enabled! Please configure platform tokens.")
            return False
        
        logger.info(f"Enabled platforms: {', '.join(enabled_platforms)}")
        
        try:
            # Start bot manager
            self.running = True
            await self.bot_manager.start_bots()
            
        except Exception as e:
            logger.error(f"Error during deployment: {e}")
            return False
        
        return True
    
    def shutdown(self):
        '''Shutdown all bots'''
        logger.info("Shutting down XMRT bots...")
        self.running = False
        self.bot_manager.stop_bots()
        logger.info("Shutdown complete")
    
    async def health_check(self):
        '''Perform health check on all bots'''
        while self.running:
            try:
                # Check bot status
                logger.info("Performing health check...")
                
                # Check each platform
                for platform in BotConfig.get_enabled_platforms():
                    client = self.bot_manager.clients.get(platform)
                    if client:
                        logger.info(f"{platform.capitalize()} bot: OK")
                    else:
                        logger.warning(f"{platform.capitalize()} bot: NOT RUNNING")
                
                # Wait for next check
                await asyncio.sleep(BotConfig.MONITORING_CONFIG['health_check_interval'])
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)
    
    async def run(self):
        '''Run the bot deployment'''
        try:
            # Deploy bots
            success = await self.deploy()
            
            if not success:
                logger.error("Deployment failed")
                return
            
            # Start health monitoring
            health_task = asyncio.create_task(self.health_check())
            
            # Keep running until shutdown
            while self.running:
                await asyncio.sleep(1)
            
            # Cancel health check
            health_task.cancel()
            
        except Exception as e:
            logger.error(f"Runtime error: {e}")
        finally:
            self.shutdown()

async def main():
    '''Main deployment function'''
    deployment = BotDeployment()
    await deployment.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)
