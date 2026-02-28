#!/usr/bin/env python3
"""Simple utility to create a Jira JQL file and render release notes.

Usage:
    ./generate_release_notes.py [version]

If no version argument is provided the user is prompted.  After providing a
version string the script will:

1. Write a JQL query to `jql/<version>.jql` which you can paste into Jira.
2. Look for a CSV named `<version>-release-manifest.csv` in
   `release-manifests/` and, if found, convert it to markdown notes.

The generated release note is written to
`release-notes/release-note-<version>.md`.

The CSV may be produced by running the JQL in Jira and downloading the
export manually (per the README planning notes).
"""

import csv
import os
import sys
import urllib.request
import urllib.error
import json

JQL_DIR = "jql"
MANIFEST_DIR = "release-manifests"
NOTES_DIR = "release-notes"


def get_version() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    return input("What is the version name? ").strip()


def write_jql(version: str) -> None:
    """Create a JQL file for the given release version."""
    query = f'project = XYZ AND fixVersion = "{version}" ORDER BY issuetype, priority'
    os.makedirs(JQL_DIR, exist_ok=True)
    path = os.path.join(JQL_DIR, f"{version}.jql")
    with open(path, "w") as fp:
        fp.write(query + "\n")
    print(f"Wrote JQL query to {path}")


def post_to_slack(message: str) -> None:
    """Send the given text to any webhook URLs listed in SLACK_WEBHOOK_URLS.

    The environment variable may contain multiple comma-separated URLs.
    This is a very small helper to satisfy the *post to Slack* step; if you
    prefer a more robust library feel free to replace it.
    """
    urls = os.environ.get("SLACK_WEBHOOK_URLS", "").strip()
    if not urls:
        return
    for url in urls.split(","):
        url = url.strip()
        if not url:
            continue
        payload = json.dumps({"text": message}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status != 200:
                    print(f"Slack webhook returned {resp.status}")
        except urllib.error.URLError as e:
            print(f"Failed to post to Slack: {e}")


def generate_release_notes(version: str) -> None:
    """Read the CSV manifest and render a markdown release note."""
    manifest_name = f"{version}-release-manifest.csv"
    manifest_path = os.path.join(MANIFEST_DIR, manifest_name)

    if not os.path.exists(manifest_path):
        print(f"Manifest not found ({manifest_path}), skipping note generation.")
        return

    os.makedirs(NOTES_DIR, exist_ok=True)
    output_path = os.path.join(NOTES_DIR, f"release-note-{version}.md")

    with open(manifest_path, newline="") as fp:
        reader = csv.DictReader(fp)
        rows = list(reader)

    note_text = None
    template_path = os.path.join(NOTES_DIR, "template.md")
    if os.path.exists(template_path):
        tpl = open(template_path).read()
        note_text = tpl.replace("{{version}}", version)

        # handle simple issue loop
        start_tag = "{{#issues}}"
        end_tag = "{{/issues}}"
        start = note_text.find(start_tag)
        end = note_text.find(end_tag)
        if start != -1 and end != -1 and end > start:
            block = note_text[start + len(start_tag) : end]
            rendered = ""
            for row in rows:
                line = block
                replacements = {
                    "{{key}}": row.get("Key", ""),
                    "{{summary}}": row.get("Summary", ""),
                    "{{issuetype}}": row.get("Issue Type", row.get("IssueType", "")),
                }
                for ph, val in replacements.items():
                    line = line.replace(ph, val)
                rendered += line
            note_text = note_text[:start] + rendered + note_text[end + len(end_tag) :]
    else:
        lines = [f"# Release Notes for {version}", ""]
        for row in rows:
            key = row.get("Key", "")
            summary = row.get("Summary", "")
            issuetype = row.get("Issue Type", row.get("IssueType", ""))
            lines.append(f"- **{key}** ({issuetype}) {summary}")
        note_text = "\n".join(lines)

    # write out the note
    with open(output_path, "w") as fp:
        fp.write(note_text)

    print(f"Generated release notes at {output_path}")

    # attempt to post on Slack if configured
    post_to_slack(note_text)



if __name__ == "__main__":
    ver = get_version()
    if not ver:
        sys.exit("No version provided, exiting.")
    write_jql(ver)
    generate_release_notes(ver)
