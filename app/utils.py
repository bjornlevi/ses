import markdown2
import bleach


def render_markdown(text: str) -> str:
    """
    Render Markdown content to safe HTML, allowing basic formatting while stripping scripts.
    """
    allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
        "p",
        "pre",
        "code",
        "blockquote",
        "hr",
        "br",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "li",
        "strong",
        "em",
        "table",
        "thead",
        "tbody",
        "tr",
        "th",
        "td",
    ]
    html = markdown2.markdown(text, extras=["fenced-code-blocks", "tables"])
    return bleach.clean(html, tags=allowed_tags, strip=True)
