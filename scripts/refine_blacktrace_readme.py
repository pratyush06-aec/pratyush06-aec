from pathlib import Path

readme_path = Path("README.md")
text = readme_path.read_text(encoding="utf-8")

start_marker = "<!-- BLACKTRACE PHASE 4C ASSETS START -->"
end_marker = "<!-- BLACKTRACE PHASE 4C ASSETS END -->"

# 1. Extract and remove the original grouped asset block.
if text.count(start_marker) != 1 or text.count(end_marker) != 1:
    raise SystemExit("ERROR: Expected exactly one pair of Phase 4C markers.")

start = text.index(start_marker)
end = text.index(end_marker) + len(end_marker)

text = text[:start] + text[end:]
text = text.lstrip("\n")

# 2. Define the individual image components.
case_header = '''<p align="center">
  <img
    src="./assets/blacktrace/dossiers/case-file-header.svg"
    alt="BLACKTRACE classified investigator dossier"
    width="100%"
  />
</p>

'''

evidence_markers = '''

<p align="center">
  <img
    src="./assets/blacktrace/effects/evidence-markers.svg"
    alt="BLACKTRACE evidence register"
    width="100%"
  />
</p>
'''

surveillance_overlay = '''

<p align="center">
  <img
    src="./assets/blacktrace/effects/surveillance-overlay.svg"
    alt="BLACKTRACE surveillance network interface"
    width="100%"
  />
</p>

'''

classified_divider = '''<p align="center">
  <img
    src="./assets/blacktrace/motion/classified-divider.svg"
    alt="BLACKTRACE classified section divider"
    width="100%"
  />
</p>'''

# 3. Place case header immediately before Investigator Profile.
profile_heading = '<h2 align="center">01 // INVESTIGATOR PROFILE</h2>'
if text.count(profile_heading) != 1:
    raise SystemExit("ERROR: Investigator Profile heading must occur exactly once.")

text = text.replace(profile_heading, case_header + profile_heading, 1)

# 4. Place evidence markers after the Active Investigations introduction.
investigation_intro = '''<p align="center">
  <i>Every project starts with a problem worth investigating.</i>
</p>'''

if text.count(investigation_intro) != 1:
    raise SystemExit("ERROR: Active Investigations introduction not found exactly once.")

text = text.replace(
    investigation_intro,
    investigation_intro + evidence_markers,
    1
)

# 5. Place surveillance overlay after the Tech Arsenal content.
repository_heading = '''<h2 align="center">
  04A // REPOSITORY INTELLIGENCE
</h2>'''

if text.count(repository_heading) != 1:
    raise SystemExit("ERROR: Repository Intelligence heading not found exactly once.")

before_repository = text.split(repository_heading, 1)[0]

tech_heading = '<h2 align="center">03 // TECH ARSENAL</h2>'
tech_position = before_repository.find(tech_heading)

if tech_position < 0:
    raise SystemExit("ERROR: Tech Arsenal heading not found.")

# Insert before the final horizontal separator preceding Repository Intelligence.
separator_position = before_repository.rfind("---")
if separator_position < tech_position:
    raise SystemExit("ERROR: Could not locate the Tech Arsenal section ending.")

text = (
    before_repository[:separator_position]
    + surveillance_overlay
    + before_repository[separator_position:]
    + repository_heading
    + text.split(repository_heading, 1)[1]
)

# 6. Replace the old footer divider with the new classified divider.
old_divider = '<img src="./assets/case-divider.svg" width="100%" />'

if text.count(old_divider) != 1:
    raise SystemExit("ERROR: Expected exactly one existing footer divider.")

text = text.replace(old_divider, classified_divider, 1)

# 7. Remove any extra leading blank lines and save.
text = text.lstrip("\n")
readme_path.write_text(text, encoding="utf-8", newline="\n")

# 8. Validate the final placements.
expected = {
    "case header": "./assets/blacktrace/dossiers/case-file-header.svg",
    "evidence markers": "./assets/blacktrace/effects/evidence-markers.svg",
    "surveillance overlay": "./assets/blacktrace/effects/surveillance-overlay.svg",
    "classified divider": "./assets/blacktrace/motion/classified-divider.svg",
}

for label, path in expected.items():
    if text.count(path) != 1:
        raise SystemExit(f"ERROR: {label} reference count is not exactly one.")

if "./assets/blacktrace/motion/blacktrace-investigation.gif" in text:
    raise SystemExit("ERROR: Investigation GIF should not be in the README yet.")

print("SUCCESS: README assets repositioned.")
for label, path in expected.items():
    print(f"[OK] {label}: {path}")

print("[OK] Investigation GIF retained outside README.")
