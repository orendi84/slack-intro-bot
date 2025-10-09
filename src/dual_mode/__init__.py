"""
Dual Mode Package

Provides dual-mode support for running intro extraction in both:
- Cursor IDE (request generation mode)
- Claude Code (direct execution mode with MCP tools)
"""

from .intro_extraction_api import (
    detect_execution_environment,
    generate_mcp_request,
    extract_intros_mcp_mode,
    extract_intros_auto
)

from .mcp_adapter import get_mcp_adapter

__all__ = [
    'detect_execution_environment',
    'generate_mcp_request',
    'extract_intros_mcp_mode',
    'extract_intros_auto',
    'get_mcp_adapter'
]

