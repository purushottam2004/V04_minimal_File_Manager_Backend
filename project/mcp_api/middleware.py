"""
Middleware for IP-based authentication for MCP API endpoints.
This middleware checks if the request comes from an allowed IP address.
"""

import logging
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(settings.MCP_LOGGER)


class MCPIPAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate MCP API requests based on IP address.
    
    This middleware checks if the request comes from an allowed IP address
    before allowing access to MCP API endpoints.
    """
    
    def process_request(self, request) -> None:
        """
        Process the request and check IP authentication for MCP API endpoints.
        
        Args:
            request: The HTTP request object
            
        Returns:
            None if authentication passes, JsonResponse with error if it fails
        """
        # Debug logging
        if settings.DEBUG:
            logger.debug(f"MCP Middleware: Processing request from {request.META.get('REMOTE_ADDR', 'unknown')}")
            logger.debug(f"MCP Middleware: Request path: {request.path}")
        
        # Only apply to MCP API endpoints
        if not request.path.startswith('/mcp_api/'):
            if settings.DEBUG:
                logger.debug("MCP Middleware: Not an MCP API endpoint, skipping authentication")
            return None
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Log the request
        logger.info(f"MCP API request from IP: {client_ip} to endpoint: {request.path}")
        
        # Check if IP is allowed
        if client_ip not in settings.MCP_ALLOWED_IPS:
            logger.warning(f"MCP API access denied for IP: {client_ip}")
            return JsonResponse({
                'error': 'Access denied',
                'message': 'Your IP address is not authorized to access MCP API endpoints',
                'ip': client_ip
            }, status=403)
        
        # Debug logging for successful authentication
        if settings.DEBUG:
            logger.debug(f"MCP Middleware: IP {client_ip} authenticated successfully")
        
        return None
    
    def _get_client_ip(self, request) -> str:
        """
        Get the client IP address from the request.
        
        Args:
            request: The HTTP request object
            
        Returns:
            str: The client IP address
        """
        # Try to get IP from various headers (for proxy scenarios)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Get the first IP in the list
            client_ip = x_forwarded_for.split(',')[0].strip()
            if settings.DEBUG:
                logger.debug(f"MCP Middleware: Got IP from X-Forwarded-For: {client_ip}")
            return client_ip
        
        # Fallback to REMOTE_ADDR
        client_ip = request.META.get('REMOTE_ADDR', 'unknown')
        if settings.DEBUG:
            logger.debug(f"MCP Middleware: Got IP from REMOTE_ADDR: {client_ip}")
        return client_ip 