from flask import Blueprint, render_template, request, jsonify
from CTFd.models import db, Teams, Challenges
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.utils.decorators.visibility import check_challenge_visibility
from CTFd.utils.decorators import during_ctf_time_only, require_verified_emails
from CTFd.utils.config import get_config
from CTFd.utils.user import get_current_team
from CTFd.cache import clear_config
from datetime import datetime, timezone
from .models import TeamCamp, ChallengeCamp, CampAccessLog


def set_config(key, value, commit=True):
    """Save a CTFd config value."""
    from CTFd.models import Configs

    config = Configs.query.filter_by(key=key).first()
    if config:
        config.value = value
    else:
        config = Configs(key=key, value=value)
        db.session.add(config)

    if commit:
        db.session.commit()
        clear_config()


def can_change_camp(team_id):
    """
    Returns (can_change: bool, reason: str).
    Checks deadline and allow_change config.
    """
    deadline_str = get_config('camps_change_deadline', default='')
    if deadline_str:
        try:
            if datetime.now(timezone.utc) > datetime.fromisoformat(deadline_str):
                return False, "The camp change deadline has passed"
        except Exception:
            pass

    if not get_config('camps_allow_change', default=True):
        if TeamCamp.query.filter_by(team_id=team_id).first():
            return False, "Camp change is disabled. Your choice is final."

    return True, "OK"


def can_join_camp(camp, current_team_id=None):
    """
    Returns (can_join: bool, reason: str).
    Checks per-camp team limits if enabled.
    """
    if not get_config('camps_enable_team_limits', default=False):
        return True, ""

    if camp == 'blue':
        max_teams = get_config('camps_max_blue_teams', default=0)
    elif camp == 'red':
        max_teams = get_config('camps_max_red_teams', default=0)
    else:
        return False, "Invalid camp"

    if max_teams == 0:
        return True, ""

    current_count = TeamCamp.query.filter_by(camp=camp).count()

    if current_team_id:
        entry = TeamCamp.query.filter_by(team_id=current_team_id).first()
        if entry and entry.camp == camp:
            return True, ""

    if current_count >= max_teams:
        camp_name = "Blue" if camp == 'blue' else "Red"
        return False, f"The {camp_name} camp is full ({current_count}/{max_teams} teams)"

    return True, ""


def load_bp():
    """Creates and returns the camps Blueprint."""
    camps_bp = Blueprint(
        'camps',
        __name__,
        template_folder='templates',
        static_folder='assets'
    )

    # ── Admin routes ──────────────────────────────────────────────────────────

    @camps_bp.route('/admin/camps')
    @admins_only
    def camps_admin():
        teams = Teams.query.all()
        teams_camps = {tc.team_id: tc.camp for tc in TeamCamp.query.all()}
        teams_data = [
            {'id': t.id, 'name': t.name, 'camp': teams_camps.get(t.id)}
            for t in teams
        ]

        blue_count = TeamCamp.query.filter_by(camp='blue').count()
        red_count = TeamCamp.query.filter_by(camp='red').count()
        stats = {
            'blue': blue_count,
            'red': red_count,
            'unassigned': len(teams) - blue_count - red_count,
            'total': len(teams)
        }

        deadline_str = get_config('camps_change_deadline', default='')
        deadline_formatted = ''
        deadline_passed = False
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
                deadline_formatted = deadline.strftime('%Y-%m-%dT%H:%M')
                deadline_passed = datetime.now(timezone.utc) > deadline
            except Exception:
                pass

        config = {
            'allow_change': get_config('camps_allow_change', default=True),
            'show_public_stats': get_config('camps_show_public_stats', default=False),
            'show_challenge_badges': get_config('camps_show_challenge_badges', default=False),
            'enable_team_limits': get_config('camps_enable_team_limits', default=False),
            'max_blue_teams': get_config('camps_max_blue_teams', default=0),
            'max_red_teams': get_config('camps_max_red_teams', default=0),
            'deadline': deadline_formatted,
            'deadline_passed': deadline_passed,
        }

        return render_template('camps_admin.html', teams=teams_data, stats=stats, config=config)

    @camps_bp.route('/admin/camps/config', methods=['POST'])
    @admins_only
    def update_config():
        try:
            deadline = (request.json or {}).get('deadline', '')
            if deadline:
                try:
                    datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                except Exception:
                    return jsonify({'success': False, 'error': 'Invalid date format'}), 400

            set_config('camps_allow_change', request.json.get('allow_change', True), commit=False)
            set_config('camps_show_public_stats', request.json.get('show_public_stats', False), commit=False)
            set_config('camps_show_challenge_badges', request.json.get('show_challenge_badges', False), commit=False)
            set_config('camps_enable_team_limits', request.json.get('enable_team_limits', False), commit=False)
            set_config('camps_max_blue_teams', int(request.json.get('max_blue_teams', 0)), commit=False)
            set_config('camps_max_red_teams', int(request.json.get('max_red_teams', 0)), commit=False)
            set_config('camps_change_deadline', deadline, commit=False)
            db.session.commit()
            clear_config()

            return jsonify({'success': True, 'message': 'Configuration updated'})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @camps_bp.route('/admin/camps/team/<int:team_id>', methods=['POST'])
    @admins_only
    def update_team_camp(team_id):
        camp = (request.json or {}).get('camp')
        if camp not in ['blue', 'red', 'none', None]:
            return jsonify({'success': False, 'error': 'Invalid camp'}), 400

        if not Teams.query.filter_by(id=team_id).first():
            return jsonify({'success': False, 'error': 'Team not found'}), 404

        try:
            if camp in ('none', None):
                TeamCamp.query.filter_by(team_id=team_id).delete()
                db.session.commit()
                return jsonify({'success': True, 'message': 'Camp removed'})

            entry = TeamCamp.query.filter_by(team_id=team_id).first()
            if entry:
                entry.camp = camp
            else:
                db.session.add(TeamCamp(team_id=team_id, camp=camp))
            db.session.commit()
            return jsonify({'success': True, 'message': f'{camp.capitalize()} camp assigned'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @camps_bp.route('/admin/camps/logs')
    @admins_only
    def camps_logs():
        logs = CampAccessLog.query.order_by(CampAccessLog.timestamp.desc()).limit(100).all()

        team_ids = {log.team_id for log in logs if log.team_id}
        challenge_ids = {log.challenge_id for log in logs if log.challenge_id}

        teams_map = {t.id: t.name for t in Teams.query.filter(Teams.id.in_(team_ids)).all()} if team_ids else {}
        challenges_map = {c.id: c.name for c in Challenges.query.filter(Challenges.id.in_(challenge_ids)).all()} if challenge_ids else {}

        logs_data = [{
            'id': log.id,
            'team_name': teams_map.get(log.team_id, f'Team #{log.team_id}'),
            'team_id': log.team_id,
            'team_camp': log.team_camp,
            'challenge_name': challenges_map.get(log.challenge_id, f'Challenge #{log.challenge_id}'),
            'challenge_id': log.challenge_id,
            'challenge_camp': log.challenge_camp,
            'request_info': log.ip_address or '',
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        } for log in logs]

        stats = {
            'total': CampAccessLog.query.count(),
            'unique_teams': db.session.query(CampAccessLog.team_id).distinct().count(),
            'shown': len(logs_data),
        }

        return render_template('camps_logs.html', logs=logs_data, stats=stats)

    @camps_bp.route('/admin/camps/logs/clear', methods=['POST'])
    @admins_only
    def clear_logs():
        try:
            CampAccessLog.query.delete()
            db.session.commit()
            return jsonify({'success': True, 'message': 'Logs cleared'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    # ── User routes ───────────────────────────────────────────────────────────

    @camps_bp.route('/camps/select')
    @authed_only
    def select_camp_page():
        team = get_current_team()
        if not team:
            return "You must be in a team to access this page", 403

        entry = TeamCamp.query.filter_by(team_id=team.id).first()
        current_camp = entry.camp if entry else None
        can_change, error_msg = can_change_camp(team.id)

        allow_change = get_config('camps_allow_change', default=True)
        show_public_stats = get_config('camps_show_public_stats', default=False)
        enable_team_limits = get_config('camps_enable_team_limits', default=False)

        stats = None
        if show_public_stats or enable_team_limits:
            stats = {
                'blue': TeamCamp.query.filter_by(camp='blue').count(),
                'red': TeamCamp.query.filter_by(camp='red').count(),
                'show_counts': show_public_stats,
                'show_limits': enable_team_limits,
            }
            if enable_team_limits:
                stats['blue_max'] = get_config('camps_max_blue_teams', default=0)
                stats['red_max'] = get_config('camps_max_red_teams', default=0)

        can_join_blue, blue_error = can_join_camp('blue', team.id)
        can_join_red, red_error = can_join_camp('red', team.id)

        deadline_formatted = None
        deadline_str = get_config('camps_change_deadline', default='')
        if deadline_str:
            try:
                deadline_formatted = datetime.fromisoformat(deadline_str).strftime('%Y-%m-%d %H:%M')
            except Exception:
                pass

        return render_template(
            'camps_select.html',
            current_camp=current_camp,
            can_change=can_change,
            allow_change=allow_change,
            can_join_blue=can_join_blue,
            can_join_red=can_join_red,
            blue_error=blue_error,
            red_error=red_error,
            change_error=error_msg if not can_change else None,
            deadline=deadline_formatted,
            stats=stats,
        )

    @camps_bp.route('/api/v1/camps/select', methods=['POST'])
    @authed_only
    def select_camp_api():
        team = get_current_team()
        if not team:
            return jsonify({'success': False, 'error': 'You must be in a team'}), 403

        from CTFd.utils.user import get_current_user
        user = get_current_user()
        if team.captain_id and user.id != team.captain_id:
            return jsonify({'success': False, 'error': "Only the captain can change the team's camp"}), 403

        camp = (request.json or {}).get('camp')
        if camp not in ['blue', 'red']:
            return jsonify({'success': False, 'error': 'Invalid camp'}), 400

        can_change, error_msg = can_change_camp(team.id)
        if not can_change:
            return jsonify({'success': False, 'error': error_msg}), 403

        can_join, join_error = can_join_camp(camp, team.id)
        if not can_join:
            return jsonify({'success': False, 'error': join_error}), 403

        try:
            entry = TeamCamp.query.filter_by(team_id=team.id).first()
            if entry:
                old_camp = entry.camp
                entry.camp = camp
                message = f'Camp changed from {old_camp} to {camp}'
            else:
                db.session.add(TeamCamp(team_id=team.id, camp=camp))
                message = f'You joined the {camp} camp'

            # TOCTOU check: re-verify count after flush
            db.session.flush()
            if get_config('camps_enable_team_limits', default=False):
                max_teams = int(get_config(f'camps_max_{camp}_teams', default=0))
                if max_teams > 0 and TeamCamp.query.filter_by(camp=camp).count() > max_teams:
                    db.session.rollback()
                    camp_name = "Blue" if camp == 'blue' else "Red"
                    return jsonify({'success': False, 'error': f'The {camp_name} camp became full'}), 409

            db.session.commit()
            return jsonify({'success': True, 'message': message})

        except Exception:
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Save failed'}), 500

    @camps_bp.route('/api/v1/camps/challenges')
    @during_ctf_time_only
    @require_verified_emails
    @authed_only
    @check_challenge_visibility
    def get_challenges_with_camps():
        """Returns challenges filtered by the team's camp."""
        team = get_current_team()
        if not team:
            return jsonify({'success': False, 'error': 'You must be in a team'}), 403

        entry = TeamCamp.query.filter_by(team_id=team.id).first()
        team_camp = entry.camp if entry else None

        if not team_camp:
            return jsonify({'success': False, 'error': 'You must choose a camp'}), 403

        camps_map = {c.challenge_id: c.camp for c in ChallengeCamp.query.all()}
        result = [
            {
                'id': ch.id,
                'name': ch.name,
                'category': ch.category,
                'value': ch.value,
                'camp': camps_map.get(ch.id),
                'type': ch.type,
                'state': ch.state,
            }
            for ch in Challenges.query.filter_by(state='visible').all()
            if camps_map.get(ch.id) is None or camps_map.get(ch.id) == team_camp
        ]

        return jsonify({'success': True, 'data': result, 'team_camp': team_camp})

    return camps_bp
