import json
import re
import os

from flask import request, g, redirect
from CTFd.plugins import register_plugin_assets_directory
from CTFd.models import db
from CTFd.utils.config import get_config
from CTFd.utils.user import get_current_team, is_admin, get_ip

from .blueprint import load_bp, can_change_camp
from .models import ChallengeCamp, TeamCamp, CampAccessLog
from .patches.admin import (
    patch_admin_challenges_listing,
    patch_admin_teams_listing,
    patch_user_challenges_page,
    patch_create_challenge,
    patch_update_challenge,
)

import sqlalchemy as sa


def load(app):
    """Main load function for the CTFd Camps plugin."""

    # Create tables if they don't exist
    with app.app_context():
        inspector = sa.inspect(db.engine)
        tables = inspector.get_table_names()

        if 'challenge_camps' not in tables:
            print("[CTFd Camps] Creating table challenge_camps...")
            ChallengeCamp.__table__.create(db.engine)

        if 'team_camps' not in tables:
            print("[CTFd Camps] Creating table team_camps...")
            TeamCamp.__table__.create(db.engine)

        if 'camp_access_logs' not in tables:
            print("[CTFd Camps] Creating table camp_access_logs...")
            CampAccessLog.__table__.create(db.engine)

    # Apply admin template patches
    patch_admin_challenges_listing(app)
    patch_admin_teams_listing(app)
    patch_user_challenges_page(app)
    patch_create_challenge(app)
    patch_update_challenge(app)

    @app.before_request
    def check_team_has_camp():
        """Redirects to /camps/select if the team has no camp and visits /challenges."""
        if is_admin():
            return

        if request.endpoint and (
            request.endpoint.startswith('api.') or
            request.endpoint.startswith('views.static') or
            request.endpoint.startswith('admin.')
        ):
            return

        if request.path.startswith('/camps/'):
            return

        if request.path == '/challenges' or request.path.startswith('/challenges/'):
            team = get_current_team()
            if team:
                if not TeamCamp.query.filter_by(team_id=team.id).first():
                    return redirect('/camps/select')

    @app.before_request
    def block_cross_camp_attempt():
        """Blocks POST /api/v1/challenges/attempt for cross-camp challenges."""
        if request.path != '/api/v1/challenges/attempt' or request.method != 'POST':
            return

        if is_admin():
            return

        team = get_current_team()
        if not team:
            return

        team_camp_entry = TeamCamp.query.filter_by(team_id=team.id).first()
        if not team_camp_entry:
            return

        team_camp = team_camp_entry.camp

        try:
            data = request.get_json()
            challenge_id = data.get('challenge_id') if data else None
            if not challenge_id:
                return

            camp_entry = ChallengeCamp.query.filter_by(challenge_id=int(challenge_id)).first()
            challenge_camp = camp_entry.camp if camp_entry else None

            if challenge_camp is not None and challenge_camp != team_camp:
                try:
                    log_entry = CampAccessLog(
                        team_id=team.id,
                        challenge_id=int(challenge_id),
                        team_camp=team_camp,
                        challenge_camp=challenge_camp,
                        ip_address=f"POST /api/v1/challenges/attempt challenge_id={challenge_id} (IP: {get_ip(req=request)})"[:500]
                    )
                    db.session.add(log_entry)
                    db.session.commit()
                except Exception:
                    db.session.rollback()

                from flask import jsonify
                return jsonify({
                    'success': True,
                    'data': {
                        'status': 'incorrect',
                        'message': 'This challenge is not accessible by your camp'
                    }
                }), 403
        except Exception:
            pass

    @app.after_request
    def filter_challenges_by_camp(response):
        """Filters challenge API responses to only show the team's camp challenges."""
        if is_admin():
            return response

        # Filter challenge list
        if request.path == '/api/v1/challenges' and response.status_code == 200:
            try:
                team = get_current_team()
                if not team:
                    return response

                team_camp_entry = TeamCamp.query.filter_by(team_id=team.id).first()
                if not team_camp_entry:
                    response.set_data(json.dumps({'success': True, 'data': []}))
                    return response

                team_camp = team_camp_entry.camp
                data = json.loads(response.get_data(as_text=True))

                if data.get('success') and 'data' in data:
                    camps_map = {c.challenge_id: c.camp for c in ChallengeCamp.query.all()}
                    data['data'] = [
                        c for c in data['data']
                        if camps_map.get(c['id']) is None or camps_map.get(c['id']) == team_camp
                    ]
                    response.set_data(json.dumps(data))

            except Exception as e:
                print(f"[CTFd Camps] Error filtering challenge list: {e}")

        # Filter individual challenge
        match = re.match(r'^/api/v1/challenges/(\d+)$', request.path)
        if match and response.status_code == 200:
            challenge_id = int(match.group(1))
            try:
                team = get_current_team()
                if not team:
                    return response

                team_camp_entry = TeamCamp.query.filter_by(team_id=team.id).first()
                if not team_camp_entry:
                    response.set_data(json.dumps({
                        'success': False,
                        'error': 'You must choose a camp to access challenges'
                    }))
                    response.status_code = 403
                    return response

                team_camp = team_camp_entry.camp
                camp_entry = ChallengeCamp.query.filter_by(challenge_id=challenge_id).first()
                challenge_camp = camp_entry.camp if camp_entry else None

                if challenge_camp is not None and challenge_camp != team_camp:
                    try:
                        log_entry = CampAccessLog(
                            team_id=team.id,
                            challenge_id=challenge_id,
                            team_camp=team_camp,
                            challenge_camp=challenge_camp,
                            ip_address=f"{request.method} {request.url} (IP: {get_ip(req=request)})"[:500]
                        )
                        db.session.add(log_entry)
                        db.session.commit()
                    except Exception:
                        db.session.rollback()

                    response.set_data(json.dumps({
                        'success': False,
                        'error': 'This challenge is not accessible by your camp'
                    }))
                    response.status_code = 403

            except Exception as e:
                print(f"[CTFd Camps] Error filtering individual challenge: {e}")

        return response

    @app.context_processor
    def inject_camp_data():
        """Injects camp helper functions into all templates."""

        def get_challenge_camp(challenge_id):
            entry = ChallengeCamp.query.filter_by(challenge_id=challenge_id).first()
            return entry.camp if entry else None

        def get_team_camp(team_id):
            entry = TeamCamp.query.filter_by(team_id=team_id).first()
            return entry.camp if entry else None

        def can_change_camp_for_display():
            team = get_current_team()
            if not team:
                return False
            can_change, _ = can_change_camp(team.id)
            return can_change

        return dict(
            get_challenge_camp=get_challenge_camp,
            get_team_camp=get_team_camp,
            get_current_team=get_current_team,
            can_change_camp_for_display=can_change_camp_for_display,
        )

    @app.after_request
    def inject_challenge_badges(response):
        """Injects colored camp dots on challenge cards when the option is enabled."""
        if request.path != '/challenges' or response.status_code != 200:
            return response

        if not get_config('camps_show_challenge_badges', default=False):
            return response

        team = get_current_team()
        team_camp = None
        if team:
            entry = TeamCamp.query.filter_by(team_id=team.id).first()
            team_camp = entry.camp if entry else None

        all_camps = {c.challenge_id: c.camp for c in ChallengeCamp.query.all()}
        camps_map = {
            cid: camp for cid, camp in all_camps.items()
            if team_camp is None or camp == team_camp
        }

        inject_script = f"""
<script>
(function() {{
    const campsMap = {camps_map};

    function addCampBadges() {{
        document.querySelectorAll('.challenge-button[value]').forEach(button => {{
            const challengeId = parseInt(button.getAttribute('value'));
            const camp = campsMap[challengeId];
            if (camp && !button.querySelector('.camp-badge')) {{
                const badge = document.createElement('div');
                badge.className = 'camp-badge';
                badge.style.cssText = `
                    position: absolute; bottom: 8px; left: 8px;
                    width: 14px; height: 14px; border-radius: 50%;
                    background-color: ${{camp === 'blue' ? '#007bff' : '#dc3545'}};
                    border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    z-index: 10; pointer-events: none;
                `;
                badge.title = camp === 'blue' ? 'Blue Camp' : 'Red Camp';
                button.style.position = 'relative';
                button.appendChild(badge);
            }}
        }});
    }}

    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', addCampBadges);
    }} else {{
        addCampBadges();
    }}
    new MutationObserver(addCampBadges).observe(document.body, {{ childList: true, subtree: true }});
}})();
</script>
"""
        html = response.get_data(as_text=True)
        if '</body>' in html:
            response.set_data(html.replace('</body>', inject_script + '</body>'))

        return response

    @app.before_request
    def enrich_challenges_with_camp():
        """Populates g.camps_map and g.teams_camps_map for admin templates."""
        if request.endpoint and 'challenges' in str(request.endpoint):
            try:
                g.camps_map = {c.challenge_id: c.camp for c in ChallengeCamp.query.all()}
            except Exception:
                g.camps_map = {}

        if request.endpoint and 'teams' in str(request.endpoint):
            try:
                g.teams_camps_map = {tc.team_id: tc.camp for tc in TeamCamp.query.all()}
            except Exception:
                g.teams_camps_map = {}

    @app.before_request
    def extract_camp_from_request():
        """Extracts 'camp' from challenge create/update requests and stashes it in g."""
        if not (request.endpoint and 'api.challenges' in request.endpoint):
            return
        if request.method not in ['POST', 'PATCH']:
            return

        camp_value = None
        if request.form.get('camp'):
            camp_value = request.form.get('camp')
            request.form = request.form.copy()
            del request.form['camp']
        elif request.is_json and request.json and request.json.get('camp'):
            camp_value = request.json.get('camp')
            del request.json['camp']

        g.camp_value = camp_value if camp_value in ['blue', 'red'] else None

    @app.after_request
    def save_challenge_camp(response):
        """Persists the camp assignment after a challenge is created or updated."""
        if not (hasattr(g, 'camp_value') and g.camp_value):
            return response

        if request.method == 'POST' and response.status_code in [200, 201]:
            try:
                data = json.loads(response.get_data(as_text=True))
                challenge_id = data.get('data', {}).get('id')
                if challenge_id:
                    db.session.add(ChallengeCamp(challenge_id=challenge_id, camp=g.camp_value))
                    db.session.commit()
            except Exception:
                db.session.rollback()

        elif request.method == 'PATCH' and response.status_code == 200:
            try:
                challenge_id = request.view_args.get('challenge_id')
                if challenge_id:
                    entry = ChallengeCamp.query.filter_by(challenge_id=challenge_id).first()
                    if entry:
                        entry.camp = g.camp_value
                    else:
                        db.session.add(ChallengeCamp(challenge_id=challenge_id, camp=g.camp_value))
                    db.session.commit()
            except Exception:
                db.session.rollback()

        return response

    # Register assets and blueprint
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_name = os.path.basename(dir_path)
    register_plugin_assets_directory(
        app,
        base_path="/plugins/" + dir_name + "/assets/",
        endpoint="camps_assets"
    )

    app.register_blueprint(load_bp())

    print("[CTFd Camps] Plugin loaded successfully!")
