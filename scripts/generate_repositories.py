
#!/usr/bin/env python3

"""
BLACKTRACE Repository Intelligence
-----------------------------------
Fetches metadata for selected GitHub repositories
and generates a custom-designed SVG dashboard.

Dependencies: Python standard library only.
"""

import argparse
import html
import json
import os
import sys
import time

from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# ============================================================
# CONFIGURATION
# ============================================================

GITHUB_USERNAME = "pratyush06-aec"

FEATURED_REPOSITORIES = [
    "flora_carbon_ai",
    "my-courier",
    "Nobodristhi",
    "AAVYA-HeredityAI-for_women_health_risk_prediction",
    "callmi",
]

CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 700

CARD_WIDTH = 344
CARD_HEIGHT = 210

API_BASE = "https://api.github.com/repos"


# ============================================================
# GITHUB API CLIENT
# ============================================================

def fetch_repository(repository_name):
    """Fetch metadata for one public GitHub repository."""

    url = f"{API_BASE}/{GITHUB_USERNAME}/{repository_name}"

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "BLACKTRACE-Repository-Intelligence",
    }

    # Optional authentication.
    # Never hardcode a token in this script.
    token = (
        os.getenv("GITHUB_TOKEN")
        or os.getenv("PROFILE_METRICS")
    )

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers, method="GET")

    for attempt in range(3):

        try:
            with urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))

                print(f"[SUCCESS] Retrieved: {repository_name}")

                return payload

        except HTTPError as error:

            if error.code == 404:
                raise RuntimeError(
                    f"Repository not found or inaccessible: "
                    f"{GITHUB_USERNAME}/{repository_name}"
                ) from error

            if error.code in (403, 429):
                remaining = error.headers.get(
                    "X-RateLimit-Remaining", "unknown"
                )

                reset = error.headers.get(
                    "X-RateLimit-Reset", "unknown"
                )

                raise RuntimeError(
                    f"GitHub API rate limit or permission error "
                    f"for {repository_name}. "
                    f"Remaining: {remaining}, reset: {reset}"
                ) from error

            if error.code >= 500 and attempt < 2:
                time.sleep(2 ** attempt)
                continue

            raise RuntimeError(
                f"GitHub API returned HTTP {error.code} "
                f"for {repository_name}"
            ) from error

        except (URLError, TimeoutError) as error:

            if attempt < 2:
                print(
                    f"[RETRY] Network error for {repository_name}: "
                    f"{error}"
                )
                time.sleep(2 ** attempt)
                continue

            raise RuntimeError(
                f"Unable to contact GitHub API for {repository_name}"
            ) from error

        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise RuntimeError(
                f"Invalid JSON response for {repository_name}"
            ) from error

    raise RuntimeError(
        f"Failed to retrieve {repository_name}"
    )


# ============================================================
# DATA PROCESSING
# ============================================================

def format_number(number):
    """Convert large numbers into readable labels."""

    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"

    if number >= 1_000:
        return f"{number / 1_000:.1f}k"

    return str(number)


def format_date(timestamp):
    """Format GitHub's ISO timestamp."""

    if not timestamp:
        return "Unknown"

    try:
        parsed = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        return parsed.strftime("%d %b %Y")

    except ValueError:
        return "Unknown"


def collect_repositories():
    """Fetch all configured repositories."""

    repositories = []

    print("\nBLACKTRACE // REPOSITORY INTELLIGENCE")
    print("=" * 55)

    for name in FEATURED_REPOSITORIES:

        data = fetch_repository(name)

        repositories.append({
            "name": data.get("name", name),
            "description": (
                data.get("description")
                or "No repository description available."
            ),
            "language": data.get("language") or "Multiple",
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "visibility": data.get("visibility", "public"),
            "updated": format_date(data.get("updated_at")),
            "url": data.get(
                "html_url",
                f"https://github.com/{GITHUB_USERNAME}/{name}"
            ),
        })

    print("=" * 55)
    print(f"[SUCCESS] Retrieved {len(repositories)} repositories.")

    return repositories


# ============================================================
# SVG UTILITIES
# ============================================================

def escape(value):
    """Escape dynamic text before inserting it into SVG."""

    return html.escape(str(value), quote=True)


def wrap_text(value, max_chars=43, max_lines=2):
    """Wrap description text into a fixed number of lines."""

    words = str(value).split()
    lines = []
    current = ""

    for word in words:

        candidate = f"{current} {word}".strip()

        if len(candidate) <= max_chars:
            current = candidate

        else:
            if current:
                lines.append(current)

            current = word

        if len(lines) >= max_lines:
            break

    if current and len(lines) < max_lines:
        lines.append(current)

    if len(words) and lines:
        joined = " ".join(lines)

        if len(joined) < len(str(value).split()) and False:
            pass

    if not lines:
        lines = ["No description available."]

    # Prevent excessively long individual words.
    lines = [
        line if len(line) <= max_chars
        else line[:max_chars - 3] + "..."
        for line in lines
    ]

    return lines


def svg_text(x, y, value, size=14, color="#E5E7EB",
             weight=400, extra=""):

    return (
        f'<text x="{x}" y="{y}" '
        f'font-family="Segoe UI, Arial, sans-serif" '
        f'font-size="{size}" '
        f'font-weight="{weight}" '
        f'fill="{color}" {extra}>'
        f'{escape(value)}</text>'
    )


# ============================================================
# SVG REPOSITORY CARD
# ============================================================

def generate_card(repository, x, y, index):

    name = repository["name"].replace("_", " ").upper()
    description = wrap_text(repository["description"])

    language = repository["language"]
    stars = format_number(repository["stars"])
    forks = format_number(repository["forks"])
    updated = repository["updated"]

    url = escape(repository["url"])

    elements = []

    # Clickable card
    elements.append(
        f'<a href="{url}" target="_blank">'
    )

    # Card background
    elements.append(
        f'''
        <rect x="{x}" y="{y}"
              width="{CARD_WIDTH}"
              height="{CARD_HEIGHT}"
              rx="13"
              fill="#111820"
              stroke="#343D48"
              stroke-width="1.2"/>
        '''
    )

    # Accent bar
    elements.append(
        f'''
        <rect x="{x}" y="{y}"
              width="4" height="{CARD_HEIGHT}"
              rx="2" fill="#E63946"/>
        '''
    )

    # Repository index
    elements.append(
        svg_text(
            x + 20, y + 29,
            f"PROJECT // {index:02d}",
            10, "#E63946", 700,
            'letter-spacing="2"'
        )
    )

    # Repository name
    elements.append(
        svg_text(
            x + 20, y + 65,
            name[:30],
            19, "#F8FAFC", 700
        )
    )

    # Description
    for line_number, line in enumerate(description):

        elements.append(
            svg_text(
                x + 20,
                y + 95 + line_number * 21,
                line,
                12,
                "#A5AFBB"
            )
        )

    # Language label
    badge_width = max(
        70,
        min(180, len(language[:20]) * 7 + 18)
    )

    elements.append(
        f'''
        <rect x="{x + 20}" y="{y + 132}"
              width="{badge_width}" height="24"
              rx="5"
              fill="#242D38"/>
        '''
    )

    elements.append(
        svg_text(
            x + 30, y + 149,
            language[:20],
            11, "#E5E7EB", 600
        )
    )

    # Repository statistics
    elements.append(
        svg_text(
            x + 20, y + 184,
            f"STARS  {stars}",
            12, "#F8FAFC", 600
        )
    )

    elements.append(
        svg_text(
            x + 130, y + 184,
            f"FORKS  {forks}",
            12, "#F8FAFC", 600
        )
    )

    # Last update
    elements.append(
        svg_text(
            x + 20, y + 202,
            f"UPDATED  {updated}",
            9, "#778391", 400
        )
    )

    elements.append("</a>")

    return "\n".join(elements)


# ============================================================
# MAIN SVG GENERATOR
# ============================================================

def generate_svg(repositories):

    if len(repositories) != len(FEATURED_REPOSITORIES):
        raise RuntimeError(
            "Repository count mismatch. "
            "Refusing to generate an incomplete dashboard."
        )

    elements = []

    elements.append(
        f'''
        <svg xmlns="http://www.w3.org/2000/svg"
             xmlns:xlink="http://www.w3.org/1999/xlink"
             width="{CANVAS_WIDTH}"
             height="{CANVAS_HEIGHT}"
             viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}"
             role="img"
             aria-labelledby="title description">

        <title id="title">
            BLACKTRACE Repository Intelligence
        </title>

        <desc id="description">
            Featured GitHub repositories belonging to
            {escape(GITHUB_USERNAME)}.
        </desc>

        <defs>
            <linearGradient id="background"
                            x1="0" y1="0"
                            x2="1" y2="1">
                <stop offset="0%" stop-color="#080C12"/>
                <stop offset="100%" stop-color="#111923"/>
            </linearGradient>

            <pattern id="grid"
                     width="32" height="32"
                     patternUnits="userSpaceOnUse">
                <path d="M 32 0 L 0 0 0 32"
                      fill="none"
                      stroke="#26313D"
                      stroke-width="0.5"
                      opacity="0.35"/>
            </pattern>
        </defs>

        <rect width="100%" height="100%"
              fill="url(#background)"/>

        <rect width="100%" height="100%"
              fill="url(#grid)"/>

        '''
    )

    # Header
    elements.append(
        svg_text(
            60, 65,
            "BLACKTRACE",
            34, "#F8FAFC", 800,
            'letter-spacing="3"'
        )
    )

    elements.append(
        svg_text(
            60, 94,
            "INTELLIGENCE DIVISION // 04A",
            12, "#E63946", 700,
            'letter-spacing="3"'
        )
    )

    elements.append(
        svg_text(
            60, 126,
            "CLASSIFIED PROJECT REGISTRY // FEATURED INVESTIGATIONS",
            11, "#A5AFBB", 400,
            'letter-spacing="1"'
        )
    )

    # Status
    elements.append(
        f'''
        <circle cx="1075" cy="60" r="5"
                fill="#22C55E"/>
        '''
    )

    elements.append(
        svg_text(
            1090, 64,
            "ONLINE",
            11, "#22C55E", 700
        )
    )

    elements.append(
        svg_text(
            1090, 88,
            f"{len(repositories):02d} PROJECTS",
            10, "#778391", 500
        )
    )

    # Separator
    elements.append(
        '''
        <line x1="60" y1="155"
              x2="1140" y2="155"
              stroke="#394451"
              stroke-width="1"/>
        '''
    )

    # Repository card positioning
    positions = [
        (60, 185),
        (428, 185),
        (796, 185),
        (244, 415),
        (612, 415),
    ]

    for index, repository in enumerate(repositories):

        x, y = positions[index]

        elements.append(
            generate_card(
                repository,
                x,
                y,
                index + 1
            )
        )

    # Footer
    elements.append(
        '''
        <line x1="60" y1="652"
              x2="1140" y2="652"
              stroke="#394451"
              stroke-width="1"/>
        '''
    )

    generated_at = datetime.now(timezone.utc).strftime(
        "%d %b %Y // %H:%M UTC"
    )

    elements.append(
        svg_text(
            60, 679,
            "BLACKTRACE // REPOSITORY INTELLIGENCE",
            10, "#778391", 600,
            'letter-spacing="1"'
        )
    )

    elements.append(
        svg_text(
            1140, 679,
            generated_at,
            10, "#778391", 400,
            'text-anchor="end"'
        )
    )

    elements.append("</svg>")

    return "\n".join(elements)


# ============================================================
# EXECUTION
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Generate BLACKTRACE repository intelligence SVG."
    )

    parser.add_argument(
        "--output",
        default="assets/blacktrace-repositories.svg",
        help="Output SVG path."
    )

    args = parser.parse_args()

    try:

        repositories = collect_repositories()

        svg_content = generate_svg(repositories)

        output_path = Path(args.output)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Atomic output: do not leave a partially written SVG.
        temporary_path = output_path.with_suffix(
            output_path.suffix + ".tmp"
        )

        temporary_path.write_text(
            svg_content,
            encoding="utf-8"
        )

        temporary_path.replace(output_path)

        print("\n" + "=" * 55)
        print("[SUCCESS] BLACKTRACE SVG GENERATED")
        print(f"[OUTPUT] {output_path.resolve()}")
        print(f"[SIZE] {output_path.stat().st_size:,} bytes")
        print("=" * 55)

    except Exception as error:

        print(f"\n[ERROR] {error}", file=sys.stderr)

        sys.exit(1)


if __name__ == "__main__":
    main()
