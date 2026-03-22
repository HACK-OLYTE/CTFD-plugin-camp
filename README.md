# 🎯 CTFd Camps Plugin

> **v2.0** — Complete rewrite with security hardening, i18n support, and community contributions.

A CTFd plugin that creates an **adversarial camp system** (Blue vs Red) with automatic challenge filtering, quota management, and security logging.

---

## What's New in v2.0

### Security fixes
- **Cross-camp flag blocking** — teams can no longer submit flags for challenges from another camp; every attempt is logged
- **API hardening** — individual challenge API (`/api/v1/challenges/<id>`) now returns 403 for cross-camp access, not just the list endpoint
- **Empty list on no camp** — teams without a camp see an empty challenge list instead of all challenges
- **TOCTOU fix** — camp capacity is re-checked after the DB flush and before commit to prevent race conditions on simultaneous joins
- **Strict input validation** — only `"blue"` or `"red"` are accepted anywhere; any other value is rejected at every entry point

### Code quality
- N+1 query eliminated — challenge camps and team camps are now loaded in a single batch query per request
- `import json` and `import re` moved to module level (were repeated inside every hook call)
- Dead code removed (`enrich_challenge` context function, unused imports)
- All debug `print()` statements cleaned up

### Internationalisation
- New **i18n system** (`assets/i18n.js`) supporting English, French, Spanish and German
- Language auto-detected from cookie → browser preference → fallback to English
- All user-facing text uses `data-i18n` attributes — no hardcoded language in templates
- Admin UI left in English (admin-only, no translation needed)

### Full English translation
- All Python code, comments, docstrings and API messages translated to English
- All templates translated to English

---

## Features

### 🏕️ Camp System
- **2 adversarial camps**: Blue Camp (Defenders) 🔵 and Red Camp (Attackers) 🔴
- Assign challenges to a camp from the admin interface
- **Neutral challenges**: visible to all camps (no camp assigned)
- Team camp selection page at `/camps/select`
- Visual camp badge on the `/challenges` page

<br>

<img width="1177" height="803" alt="camp" src="https://github.com/user-attachments/assets/4f39ffc5-dc60-4a75-9067-68c187cc2160" />


### 🔒 Access Control
- **Change deadline**: lock camp changes after a configurable date
- **Change lock**: prevent any change once a camp is chosen
- **Per-camp quotas**: limit the number of teams per camp

### 🎨 Interface
- Works in dark and light mode
- **Colored dots** on challenge cards showing camp assignment (optional)
- **Public statistics**: show team count per camp on `/camps/select` (optional)
- Full admin interface at `/admin/camps`

<br>
<img width="1453" height="823" alt="Admin challenges" src="https://github.com/user-attachments/assets/25069ce9-0daf-4a87-8c6c-21d418584c66" />

### 🔐 Security
- **Automatic filtering**: teams see only their camp's challenges + neutral ones
- **API protection**: 403 Forbidden on every cross-camp access attempt (list, individual challenge, and flag submission)
- Server-side enforcement: restrictions cannot be bypassed by crafting raw requests
- **Security logs**: records unauthorized access attempts with team, challenge, IP, full request, and timestamp
- CTFd admins always see all challenges regardless of camp

---

## Installation

### 1. Clone the plugin

```bash
cd /opt/CTFd/CTFd/plugins
git clone https://github.com/HACK-OLYTE/Ctfd-plugin-camp.git ctfd-plugin-camp
```

### 2. File structure

```
CTFd/plugins/ctfd-plugin-camp/
├── __init__.py          # Plugin entry point, table creation, request hooks
├── blueprint.py         # Flask routes (admin + user), API, business logic
├── models.py            # SQLAlchemy models
├── config.json          # Plugin metadata
├── assets/
│   └── i18n.js          # Internationalisation (en, fr, es, de)
├── patches/
│   └── admin.py         # Admin template patches (camp columns, forms)
└── templates/
    ├── camps_admin.html  # Admin configuration page
    ├── camps_select.html # Team camp selection page
    └── camps_logs.html   # Security logs page
```

### 3. Restart CTFd

```bash
docker compose restart ctfd
# or
sudo systemctl restart ctfd
```

### 4. Verify the installation

On startup you should see in the logs:
```
[CTFd Camps] Plugin loaded successfully!
```

Tables are created automatically on first run.

---

## Usage

### Admin Configuration

1. **Go to** `/admin/camps`

2. **Available options**:
   - ☑ **Allow camp change** — let teams switch camp after initial selection
   - ☑ **Show team count per camp publicly** — display stats on `/camps/select`
   - ☑ **Show camp badges on challenges** — colored dots 🔵/🔴 on challenge cards
   - ☑ **Limit teams per camp** — set a max quota per camp
   - 📅 **Change deadline** — block all changes after this date/time

3. **Assign camps to challenges**:
   - During challenge creation or editing, select a camp from the dropdown
   - The "Camp" column is visible in `/admin/challenges`
   - Leave empty = neutral challenge (visible to both camps)

4. **Assign camps to teams** (optional):
   - The "Camp" column is visible in `/admin/teams`
   - Teams can also choose their own camp at `/camps/select`

<br>

<img width="961" height="828" alt="settings" src="https://github.com/user-attachments/assets/2b70df81-1bd0-4bad-84c2-4157db0e3743" />


### Team Side

1. **Choose a camp** at `/camps/select`
   - Shows available camps with descriptions
   - Buttons are greyed out if the camp is full or changes are locked
   - Confirmation dialog before joining

2. **Access challenges** at `/challenges`
   - Colored badge showing the current camp
   - "Change camp" button shown when allowed
   - Only challenges matching the team's camp + neutral challenges are visible

3. **Restrictions**:
   - Automatic redirect to `/camps/select` if no camp has been chosen
   - Cross-camp challenge access returns 403 Forbidden
   - Flag submission for another camp's challenge is blocked and logged

<br>

<img width="1431" height="822" alt="chall" src="https://github.com/user-attachments/assets/4dea19c2-e3f2-4c8c-81cb-820f294d4667" />

### Security Logs

Go to `/admin/camps/logs` to view all unauthorized access attempts.

Each log entry contains:
- Team name and ID
- Targeted challenge name and ID
- Team camp vs challenge camp
- Full HTTP request (method + URL + IP)
- Timestamp

<br>

<img width="1291" height="872" alt="Security" src="https://github.com/user-attachments/assets/0fcbc88f-f1f7-4673-b549-a84ca3a55503" />


---

## Database

| Table | Description |
|---|---|
| `challenge_camps` | Maps a challenge to a camp (`blue` / `red`) |
| `team_camps` | Maps a team to a camp (`blue` / `red`) |
| `camp_access_logs` | Logs of all unauthorized cross-camp access attempts |

Tables are created automatically at startup if they don't exist. No migration needed when upgrading from v1.

---

## Internationalisation

The player-facing UI (`/camps/select` and the challenge page badge) is fully translated. Language is detected automatically in this order:

1. `lang` / `locale` / `language` cookie
2. Browser preference (`navigator.languages`)
3. Fallback: **English**

Supported languages: 🇬🇧 English · 🇫🇷 French · 🇪🇸 Spanish · 🇩🇪 German

To add a language, add a new entry to the `translations` object in `assets/i18n.js`.

---

## Acknowledgements

A big thank you to **[@degun-osint](https://github.com/degun-osint)** for contributing four pull requests that significantly improved this plugin:

- **Security** — blocking cross-camp flag submissions and returning proper 403 responses on unauthorized challenge access
- **Robustness** — empty challenge list when no camp is assigned (instead of leaking all challenges)
- **Race condition fix** — TOCTOU protection on camp capacity checks
- **Performance** — eliminating N+1 queries by batch-loading camp assignments

All four PRs were reviewed, merged, and integrated into v2.0. Contributions like these make open-source CTF tooling better for everyone.

---

## Contributing

Contributions are welcome!

- Report bugs via [issues](https://github.com/HACK-OLYTE/Ctfd-plugin-camp/issues)
- Propose new features or open a pull request
- Contact us at [hackolyte.fr/contact](https://hackolyte.fr/contact/)

---

## License

This plugin is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
Please do not remove the footer from the HTML templates without prior authorisation from the Hack'olyte association.
