"""Calendar stub for feature/1_mcp

This small module provides a minimal HTML stub function to be replaced by the real component.
"""

def render_calendar_stub():
    """Return a minimal HTML fragment for the calendar placeholder."""
    return (
        '<div class="mcp-calendar-stub" aria-label="Calendar placeholder">'
        '<p>Calendar component (stub) — implement in feature/1_mcp</p>'
        '</div>'
    )


if __name__ == "__main__":
    print(render_calendar_stub())
