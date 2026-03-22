from CTFd.plugins import override_template
import os
import re


def _get_template(app, template_name, theme='admin'):
    """
    Récupère le contenu d'un template CTFd, soit déjà overridé, soit depuis le filesystem.
    Utilise app.root_path pour résoudre dynamiquement le chemin au lieu de /opt/CTFd/.
    """
    if template_name in app.overridden_templates:
        return app.overridden_templates[template_name]

    # app.root_path pointe vers le répertoire du package CTFd (ex: /opt/CTFd/CTFd)
    template_path = os.path.join(app.root_path, 'themes', theme, 'templates')

    # Extraire le sous-chemin depuis le nom de template (ex: "admin/challenges/challenges.html" → "challenges/challenges.html")
    if template_name.startswith('admin/'):
        sub_path = template_name[len('admin/'):]
    else:
        sub_path = template_name

    full_path = os.path.join(template_path, sub_path)
    with open(full_path, 'r') as f:
        return f.read()


def patch_admin_challenges_listing(app):
    """
    Ajoute la colonne "Camp" dans la liste des challenges de l'admin
    Patch: admin/challenges/challenges.html
    """
    original = _get_template(app, 'admin/challenges/challenges.html', theme='admin')

    # Ajouter la colonne "Camp" dans le header du tableau (avant "Category")
    match_header = re.search(r'<th class="sort-col"><b>Category</b></th>', original)
    if match_header:
        pos = match_header.start()
        original = original[:pos] + '<th class="sort-col"><b>Camp</b></th>' + original[pos:]

    # Ajouter la colonne "Camp" dans les lignes du tableau (avant "Category")
    match_column = re.search(r'<td>{{ challenge.category }}</td>', original)
    if match_column:
        pos = match_column.start()
        original = original[:pos] + '<td>{{ g.camps_map.get(challenge.id, "Non assigné") }}</td>' + original[pos:]

    if match_header and match_column:
        override_template('admin/challenges/challenges.html', original)


def patch_user_challenges_page(app):
    """
    Ajoute le badge de camp et le bouton "Changer de camp" sur la page /challenges
    Patch: challenges.html
    """
    try:
        theme = app.config.get('THEME_NAME', 'core')
        original = _get_template(app, 'challenges.html', theme=theme)

        match = re.search(r'(<h1[^>]*>.*?Challenges.*?</h1>)', original, re.DOTALL)

        if match:
            pos = match.end()
            camp_badge = '''
            {% if session.get('id') %}
                {% set team = get_current_team() %}
                {% if team %}
                    {% set team_camp = get_team_camp(team.id) %}
                    {% if team_camp %}
                        <div class="mt-3">
                            <span class="badge badge-pill {% if team_camp == 'blue' %}badge-primary{% else %}badge-danger{% endif %} p-3" style="font-size: 1.1em;">
                                {% if team_camp == 'blue' %}
                                    🔵 Vous êtes dans le <strong>Camp Bleu</strong> (Défenseurs)
                                {% else %}
                                    🔴 Vous êtes dans le <strong>Camp Rouge</strong> (Attaquants)
                                {% endif %}
                            </span>
                            {% set can_change_camp_display = can_change_camp_for_display() %}
                            {% if can_change_camp_display %}
                                <a href="/camps/select" class="btn btn-sm btn-outline-light ml-2">🔄 Changer de camp</a>
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
    Ajoute la colonne "Camp" dans la liste des équipes de l'admin
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
            original = original[:pos] + '<td class="team-camp text-center">{{ g.teams_camps_map.get(team.id, "Non assigné") }}</td>\n\n\t\t\t\t\t\t' + original[pos:]

        if match_header and match_column:
            override_template('admin/teams/teams.html', original)

    except Exception:
        pass


def patch_create_challenge(app):
    """
    Ajoute le champ "Camp" dans le formulaire de création de challenge
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
                Choisir le camp pour ce challenge (laisser "Neutre" pour un challenge visible par tous)
            </small>
        </label>
        <select class="form-control" name="camp">
            <option value="">⚪ Neutre (visible par tous)</option>
            <option value="blue">🔵 Camp Bleu (Défenseurs)</option>
            <option value="red">🔴 Camp Rouge (Attaquants)</option>
        </select>
    </div>
    {% endblock %}
    """ + original[pos:]

        override_template('admin/challenges/create.html', original)


def patch_update_challenge(app):
    """
    Ajoute le champ "Camp" dans le formulaire de modification de challenge
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
            <small class="form-text text-muted">Camp du challenge</small>
        </label>
        <select class="form-control chal-camp" name="camp">
            <option value="" {% if not challenge_camp %}selected{% endif %}>⚪ Neutre (visible par tous)</option>
            <option value="blue" {% if challenge_camp == 'blue' %}selected{% endif %}>🔵 Camp Bleu (Défenseurs)</option>
            <option value="red" {% if challenge_camp == 'red' %}selected{% endif %}>🔴 Camp Rouge (Attaquants)</option>
        </select>
    </div>
    {% endblock %}
    """ + original[pos:]

        override_template('admin/challenges/update.html', original)
