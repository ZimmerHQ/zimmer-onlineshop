"""
Usage forwarder service for Zimmer platform integration.
Handles forwarding usage data to the Zimmer platform API.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from app.core.settings import PLATFORM_API_URL, SERVICE_TOKEN, HTTP_TIMEOUT

logger = logging.getLogger(__name__)

class UsageForwarder:
    """Service for forwarding usage data to the Zimmer platform."""
    
    def __init__(self):
        self.platform_url = PLATFORM_API_URL
        self.service_token = SERVICE_TOKEN
    
    async def forward_usage_to_platform(self, usage: Dict[str, Any]) -> None:
        """
        Forward usage data to the Zimmer platform.
        
        Args:
            usage: Usage data dictionary to forward
            
        Note:
            Swallows network errors but logs them for debugging.
        """
        if not self.platform_url or not self.service_token:
            logger.debug("Platform API URL or service token not configured, skipping forward")
            return
        
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                headers = {
                    "X-Zimmer-Service-Token": self.service_token,
                    "Content-Type": "application/json"
                }
                
                response = await client.post(
                    f"{self.platform_url}/api/automations/usage",
                    json=usage,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully forwarded usage to platform: {usage}")
                else:
                    logger.warning(
                        f"Platform API returned status {response.status_code}: {response.text}"
                    )
                    
        except httpx.TimeoutException:
            logger.error("Timeout while forwarding usage to platform")
        except httpx.ConnectError:
            logger.error("Connection error while forwarding usage to platform")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error while forwarding usage to platform: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while forwarding usage to platform: {e}")
    
    def is_configured(self) -> bool:
        """
        Check if the forwarder is properly configured.
        
        Returns:
            True if both platform URL and service token are configured
        """
        return bool(self.platform_url and self.service_token)

# Global instance
usage_forwarder = UsageForwarder()

