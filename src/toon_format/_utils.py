# Copyright (c) 2025 TOON Format Organization
# SPDX-License-Identifier: MIT
"""Shared internal helpers for TOON encoding.

This module contains small helpers that keep encoded strings unambiguous, including
reserved literal detection and string escaping.
"""

from .constants import (
    BACKSLASH,
    CARRIAGE_RETURN,
    DOUBLE_QUOTE,
    FALSE_LITERAL,
    NEWLINE,
    NULL_LITERAL,
    TAB,
    TRUE_LITERAL,
)


def is_boolean_or_null_literal(token: str) -> bool:
    """Check if a token is a boolean or null literal (`true`, `false`, `null`).

    Args:
        token: The token to check

    Returns:
        True if the token is a boolean or null literal

    Examples:
        >>> is_boolean_or_null_literal("true")
        True
        >>> is_boolean_or_null_literal("null")
        True
        >>> is_boolean_or_null_literal("hello")
        False
    """
    return token == TRUE_LITERAL or token == FALSE_LITERAL or token == NULL_LITERAL


def escape_string(value: str) -> str:
    """Escape special characters in a string for encoding.

    Handles backslashes, quotes, newlines, carriage returns, and tabs.
    Per Section 7.1 of the TOON specification.

    Args:
        value: The string to escape

    Returns:
        The escaped string

    Examples:
        >>> escape_string('hello\\nworld')
        'hello\\\\nworld'
        >>> escape_string('say "hello"')
        'say \\\\"hello\\\\"'
    """
    return (
        value.replace(BACKSLASH, BACKSLASH + BACKSLASH)
        .replace(DOUBLE_QUOTE, BACKSLASH + DOUBLE_QUOTE)
        .replace(NEWLINE, BACKSLASH + "n")
        .replace(CARRIAGE_RETURN, BACKSLASH + "r")
        .replace(TAB, BACKSLASH + "t")
    )
