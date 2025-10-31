"""
Stub OPC-UA Server for Simulator Integration

Temporarily disabled during multi-tenancy migration
"""

import logging
from typing import Dict, Optional
from database import MultiTenantDatabase

logger = logging.getLogger(__name__)


class OPCUAServer:
    """Stub OPC-UA server - temporarily disabled during multi-tenancy migration"""

    def __init__(self, database: MultiTenantDatabase, endpoint: str = "opc.tcp://0.0.0.0:4840/virtplc/"):
        self.db = database
        self.endpoint = endpoint
        logger.warning("OPC-UA server is temporarily disabled during multi-tenancy migration")
