import html
import re

def strip_malicious_html(text: str) -> str:
    """
    Very basic HTML stripper. For robust sanitization, bleach should be used.
    Since we only need to extract 'facts' and plain text, we drop all HTML tags.
    """
    if not text:
        return ""
    # Remove HTML tags
    clean = re.compile('<.*?>')
    text_no_tags = re.sub(clean, '', text)
    # Unescape HTML entities (e.g., &amp; -> &)
    return html.unescape(text_no_tags).strip()

def sanitize_for_prompt_injection(text: str) -> str:
    """
    Prevent instruction injection.
    We drop system-like boundary markers that might trick an LLM later.
    """
    if not text:
        return ""
    # Remove strings that look like typical LLM boundaries
    bad_markers = [
        "System:", "Human:", "Assistant:",
        "<|endoftext|>", "<|im_start|>", "<|im_end|>",
        "Ignore all previous instructions",
        "Disregard prior prompts"
    ]
    sanitized = text
    for marker in bad_markers:
        # Case insensitive replace
        sanitized = re.sub(re.escape(marker), "", sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()
