import re

def slugify_title(title: str, max_length: int = 60) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug, flags=re.UNICODE)
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")")
    return slug[:max_length].strip("-")