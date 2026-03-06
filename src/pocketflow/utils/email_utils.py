import os
import imaplib
import email
import smtplib
import logging
import re
from typing import Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from .logging import get_logger

logger = get_logger("email_utils")

def extract_email(sender: str) -> str:
    """
    Extract email address from sender string.
    
    Args:
        sender: String containing email address (e.g., "John Doe <john@example.com>" or "john@example.com")
        
    Returns:
        Extracted email address or original string if no email found
    """
    # Try to extract email from angle brackets format: "Name <email@domain.com>"
    match = re.search(r'<([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})>', sender)
    if match:
        return match.group(1)
    
    # Try to extract standalone email address
    match = re.search(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', sender)
    if match:
        return match.group(1)
    
    # Return original string if no email found
    return sender


def normalize_message_id(message_id: Optional[str]) -> Optional[str]:
    """
    Normalize Message-ID to ensure it's in proper RFC format with angle brackets.
    
    Args:
        message_id: Message-ID string (may or may not have angle brackets)
        
    Returns:
        Normalized Message-ID with angle brackets, or None if input is None/empty
    """
    if not message_id:
        return None
    
    # Strip whitespace
    message_id = message_id.strip()
    
    if not message_id:
        return None
    
    # If already has angle brackets, return as-is
    if message_id.startswith('<') and message_id.endswith('>'):
        return message_id
    
    # Add angle brackets if missing
    return f"<{message_id}>"


def build_threading_headers(
    original_message_id: Optional[str] = None,
    original_in_reply_to: Optional[str] = None,
    original_references: Optional[str] = None,
    thread_id: Optional[str] = None,
    email_id: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Build deterministic threading headers (In-Reply-To and References) for email replies.
    
    This function ensures consistent threading behavior across all email send operations.
    Threading is done by email ID when message_id is not available.
    
    Priority order for In-Reply-To:
    1. original_message_id (if present and valid) - highest priority
    2. email_id (converted to Message-ID format: <email-{id}@pocketflow.local>)
    3. original_in_reply_to (if present and valid)
    4. thread_id (fallback)
    
    For References:
    - If original_references exists: append in_reply_to if not already present
    - If original_message_id exists: use it with in_reply_to
    - If email_id was used for threading: use the generated Message-ID format
    - Otherwise: use in_reply_to
    
    Args:
        original_message_id: Message-ID from the original email
        original_in_reply_to: In-Reply-To header from the original email
        original_references: References header from the original email
        thread_id: Thread ID from the original email
        email_id: Email ID from the original email (used for threading when message_id unavailable)
        
    Returns:
        Tuple of (in_reply_to, references) - both normalized and ready to use
    """
    # Normalize Message-ID first
    normalized_message_id = normalize_message_id(original_message_id)
    normalized_in_reply_to = normalize_message_id(original_in_reply_to)
    
    # Determine In-Reply-To using deterministic priority
    # Priority: message_id > email_id > in_reply_to > thread_id
    # We prioritize message_id because In-Reply-To should point to the immediate parent
    # If message_id is not available, use email_id to create a Message-ID format for threading
    in_reply_to = None
    if normalized_message_id:
        # Always use the original message_id as In-Reply-To (the immediate parent)
        in_reply_to = normalized_message_id
    elif email_id:
        # Use email_id to create a Message-ID format for threading
        # Format: <email-{email_id}@pocketflow.local>
        in_reply_to = f"<email-{email_id}@pocketflow.local>"
        logger.info(f"Using email_id {email_id} to create threading header: {in_reply_to}")
    elif normalized_in_reply_to:
        # Fallback: use in_reply_to if message_id and email_id are not available
        in_reply_to = normalized_in_reply_to
    elif thread_id:
        # Normalize thread_id if it looks like a Message-ID
        in_reply_to = normalize_message_id(thread_id)
    
    # Build References header deterministically
    # References should contain all message IDs in the thread chain
    references = None
    if in_reply_to:
        # We always need to include the message we're replying to in References
        if original_references:
            # Append in_reply_to to existing references if not already present
            refs_clean = original_references.strip()
            in_reply_to_clean = in_reply_to.strip()
            # Check if in_reply_to is already in references to avoid duplicates
            if in_reply_to_clean not in refs_clean:
                references = f"{refs_clean} {in_reply_to_clean}"
            else:
                references = refs_clean
        elif normalized_message_id:
            # First reply - include the original message_id in references
            # If in_reply_to is the same as message_id, just use one
            if in_reply_to == normalized_message_id:
                references = normalized_message_id
            else:
                references = f"{normalized_message_id} {in_reply_to}"
        elif email_id and in_reply_to.startswith(f"<email-{email_id}@"):
            # If we're using email_id for threading, use it as references
            references = in_reply_to
        else:
            # Fallback: use in_reply_to as references
            references = in_reply_to
    
    # Log for debugging
    logger.debug(f"Threading headers built - In-Reply-To: {in_reply_to}, References: {references}")
    logger.debug(f"  Original message_id: {original_message_id} -> normalized: {normalized_message_id}")
    logger.debug(f"  Original in_reply_to: {original_in_reply_to} -> normalized: {normalized_in_reply_to}")
    logger.debug(f"  Original references: {original_references}")
    
    return (in_reply_to, references)
