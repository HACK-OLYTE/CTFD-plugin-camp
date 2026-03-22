from CTFd.plugins import override_template
import os
import re


def _get_template(app, template_name, theme='admin'):
    """
    Fetches the content of a CTFd template, either already overridden or from the filesystem.
    Uses app.root_path to dynamically resolve the path instead of a hardcoded one.
    """
    if template_name in app.overridden_templates:
        return app.overridden_templates[template_name]

    # app.root_path points to the CTFd package directory (e.g. /opt/CTFd/CTFd)
    template_path = os.path.join(app.root_path, 'themes', theme, 'templates')

    # Extract the sub-path from the template name (e.g. "admin/challenges/challenges.html" → "challenges/challenges.html")
    if template_name.startswith('admin/'):
        sub_path = template_name[len('admin/'):]
    else:
        sub_path = template_name

    full_path = os.path.join(template_path, sub_path)
    with open(full_path, 'r') as f:
        return f.read()


def patch_admin_challenges_listing(app):
    """
    Adds a "Camp" column to the admin challenge list.
    Patch: admin/challenges/challenges.html
    """
    original = _get_template(app, 'admin/challenges/challenges.html', theme='admin')

    # Add the "Camp" column header (before "Category")
    match_header = re.search(r'<th class="sort-col"><b>Category</b></th>', original)
    if match_header:
        pos = match_header.start()
        original = original[:pos] + '<th class="sort-col"><b>Camp</b></th>' + original[pos:]

    # Add the "Camp" column in table rows (before "Category")
    match_column = re.search(r'<td>{{ challenge.category }}</td>', original)
    if match_column:
        pos = match_column.start()
        original = original[:pos] + '<td>{{ g.camps_map.get(challenge.id, "Unassigned") }}</td>' + original[pos:]

    if match_header and match_column:
        override_template('admin/challenges/challenges.html', original)


def patch_user_challenges_page(app):
    """
    Adds a camp badge and a "Change camp" button to the /challenges page.
    Patch: challenges.html
    """
    try:
        theme = app.config.get('THEME_NAME', 'core')
        original = _get_template(app, 'challenges.html', theme=theme)

        match = re.search(r'(<h1[^>]*>.*?Challenges.*?</h1>)', original, re.DOTALL)

        if match:
            pos = match.end()
            camp_badge = '''
            <script src="/plugins/ctfd-plugin-camp/assets/i18n.js"></script>
            {% if session.get('id') %}
                {% set team = get_current_team() %}
                {% if team %}
                    {% set team_camp = get_team_camp(team.id) %}
                    {% if team_camp %}
                        <div class="mt-3">
                            <span class="badge badge-pill {% if team_camp == 'blue' %}badge-primary{% else %}badge-danger{% endif %} p-3" style="font-size: 1.1em;">
                                {% if team_camp == 'blue' %}
                                    🔵 <span data-i18n="you_are_in">You are in the</span> <strong data-i18n="blue_camp">Blue Camp</strong> (<span data-i18n="defenders">Defenders</span>)
                                {% else %}
                                    🔴 <span data-i18n="you_are_in">You are in the</span> <strong data-i18n="red_camp">Red Camp</strong> (<span data-i18n="attackers">Attackers</span>)
                                {% endif %}
                            </span>
                            {% set can_change_camp_display = can_change_camp_for_display() %}
                            {% if can_change_camp_display %}
                                <a href="/camps/select" class="btn btn-sm btn-outline-light ml-2">🔄 <span data-i18n="change_camp_btn">Change camp</span></a>
                            {% endif %}
                        </div>
                    {% endif %}
                {% endif %}
            {% endif %}
'''
            original = original[:pos] + camp_badge + original[pos:]
            override_template('challenges.html', original)

    except Exception:
        pass


def patch_admin_teams_listing(app):
    """
    Adds a "Camp" column to the admin team list.
    Patch: admin/teams/teams.html
    """
    try:
        original = _get_template(app, 'admin/teams/teams.html', theme='admin')

        if '<b>Camp</b>' in original:
            return

        match_header = re.search(r'<th class="sort-col text-center px-0"><b>Hidden</b></th>', original)
        if match_header:
            pos = match_header.start()
            original = original[:pos] + '<th class="sort-col text-center"><b>Camp</b></th>\n\t\t\t\t\t\t' + original[pos:]

        match_column = re.search(r'<td class="team-hidden d-md-table-cell d-lg-table-cell text-center"', original)
        if match_column:
            pos = match_column.start()
            original = original[:pos] + '<td class="team-camp text-center">{{ g.teams_camps_map.get(team.id, "Unassigned") }}</td>\n\n\t\t\t\t\t\t' + original[pos:]

        if match_header and match_column:
            override_template('admin/teams/teams.html', original)

    except Exception:
        pass


def patch_create_challenge(app):
    """
    Adds a "Camp" field to the challenge creation form.
    Patch: admin/challenges/create.html
    """
    original = _get_template(app, 'admin/challenges/create.html', theme='admin')

    match = re.search(r'{% block category %}', original)
    if match:
        pos = match.start()
        original = original[:pos] + """
    {% block camp %}
    <div class="form-group">
        <label>
            Camp:<br>
            <small class="form-text text-muted">
                Choose the camp for this challenge (leave "Neutral" for a challenge visible to all)
            </small>
        </label>
        <select class="form-control" name="camp">
            <option value="">⚪ Neutral (visible to all)</option>
            <option value="blue">🔵 Blue Camp (Defenders)</option>
            <option value="red">🔴 Red Camp (Attackers)</option>
        </select>
    </div>
    {% endblock %}
    """ + original[pos:]

        override_template('admin/challenges/create.html', original)


def patch_update_challenge(app):
    """
    Adds a "Camp" field to the challenge edit form.
    Patch: admin/challenges/update.html
    """
    original = _get_template(app, 'admin/challenges/update.html', theme='admin')

    match = re.search(r'{% block category %}', original)
    if match:
        pos = match.start()
        original = original[:pos] + """
    {% block camp %}
    {% set challenge_camp = get_challenge_camp(challenge.id) %}
    <div class="form-group">
        <label>
            Camp<br>
            <small class="form-text text-muted">Camp for this challenge</small>
        </label>
        <select class="form-control chal-camp" name="camp">
            <option value="" {% if not challenge_camp %}selected{% endif %}>⚪ Neutral (visible to all)</option>
            <option value="blue" {% if challenge_camp == 'blue' %}selected{% endif %}>🔵 Blue Camp (Defenders)</option>
            <option value="red" {% if challenge_camp == 'red' %}selected{% endif %}>🔴 Red Camp (Attackers)</option>
        </select>
    </div>
    {% endblock %}
    """ + original[pos:]

        override_template('admin/challenges/update.html', original)