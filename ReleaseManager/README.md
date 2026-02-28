# Release Manager

This directory contains tools and documentation for automating release notes generation and distribution.

## 🛠️ Automation Plan: Generate Release Notes from Jira

The goal is to provide a simple command (`generate release notes`) that:

1. **Prompts for the version name.**
   - The user runs the script and is asked: "What is the version name?"

2. **Constructs a JQL query file.**
   - Using the supplied version the script builds the JQL (e.g. `project = XYZ AND fixVersion = "<version>" ORDER BY issuetype, priority`).
   - Rather than calling Jira directly, the query is written to a file named `<version>.jql` and placed in a `jql/` folder.  You can then copy/paste this query into Jira manually.

3. **CSV export (manual).**
   - After running the JQL in Jira yourself, download the CSV and move it into `release-manifests/`.
   - The file should be named `<version>-release-manifest.csv` so the script can locate it later.

4. **Renders Markdown release notes.**
   - A template (living in `release-notes/`) will define the layout.
   - The script reads the matching manifest CSV, fills the template, and writes `release-note-<version>.md` in the `release-notes` folder.

5. **Posts to Slack.**
   - Convert the generated markdown to Slack message blocks or use attachments.
   - Send the notes to one or more configured Slack channels via webhook URLs or a bot token.

6. **Enhancements & flags.**
   - Support for `--dry-run`, custom templates, channel lists, and integration with CI pipelines.

---

Refer to this README for setup details and additional documentation as the automation evolves.

## 🧩 Usage

Release versions are expected to follow one of these patterns:

```
YYYY-MM-DD — Feature
YYYY-MM-DD — Maintenance
```

(Spaces and the en‑dash are preserved in filenames.)

## 🧩 Usage

A helper script lives at `generate_release_notes.py`.

```bash
# make executable if necessary
chmod +x ReleaseManager/generate_release_notes.py

# run interactively
cd ReleaseManager && ./generate_release_notes.py

# or supply the version on the command line
./generate_release_notes.py "2026-03-03 - Maintenance"
```

The version string is used to create `jql/<version>.jql` and to locate a
CSV manifest named `<version>-release-manifest.csv` under
`release-manifests/`.  When a manifest exists the script will also render a
Markdown file `release-notes/release-note-<version>.md`.

If a template file `release-notes/template.md` is present it will be used to
format the release notes.  The template supports `{{version}}` and a simple
`{{#issues}}…{{/issues}}` block with placeholders `{{key}}`,
`{{issuetype}}`, and `{{summary}}`.

(See the earlier section on manual CSV export.)
