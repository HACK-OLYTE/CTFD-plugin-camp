from CTFd.models import db
from datetime import datetime


class ChallengeCamp(db.Model):
    """Associates a challenge with a camp (blue or red)."""

    __tablename__ = 'challenge_camps'

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey('challenges.id', ondelete='CASCADE'),
        nullable=False,
        unique=True  # A challenge can only belong to one camp
    )
    camp = db.Column(db.String(80), nullable=False)  # "blue" or "red"

    challenge = db.relationship('Challenges', foreign_keys=[challenge_id], lazy='select')

    def __repr__(self):
        return f'<ChallengeCamp challenge_id={self.challenge_id} camp={self.camp}>'


class TeamCamp(db.Model):
    """Associates a team with a camp (blue or red)."""

    __tablename__ = 'team_camps'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(
        db.Integer,
        db.ForeignKey('teams.id', ondelete='CASCADE'),
        nullable=False,
        unique=True  # A team can only belong to one camp
    )
    camp = db.Column(db.String(80), nullable=False)  # "blue" or "red"

    team = db.relationship('Teams', foreign_keys=[team_id], lazy='select')

    def __repr__(self):
        return f'<TeamCamp team_id={self.team_id} camp={self.camp}>'


class CampAccessLog(db.Model):
    """Logs cross-camp challenge access attempts."""

    __tablename__ = 'camp_access_logs'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id', ondelete='SET NULL'), nullable=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id', ondelete='SET NULL'), nullable=True)
    team_camp = db.Column(db.String(10), nullable=False)
    challenge_camp = db.Column(db.String(10), nullable=False)
    ip_address = db.Column(db.String(500))  # Stores: "METHOD URL (IP: x.x.x.x)"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    team = db.relationship('Teams', foreign_keys=[team_id], lazy='select')
    challenge = db.relationship('Challenges', foreign_keys=[challenge_id], lazy='select')

    def __repr__(self):
        return f'<CampAccessLog team={self.team_id} challenge={self.challenge_id}>'
