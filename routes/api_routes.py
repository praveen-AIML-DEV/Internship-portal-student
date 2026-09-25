from flask import Blueprint, request, jsonify, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models import Notification, Skill, Job, Internship

api_bp = Blueprint('api', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

@api_bp.route('/api/notifications')
def get_notifications():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])
    db = SessionLocal()
    try:
        notifs = db.query(Notification).filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(10).all()
        return jsonify([n.to_dict() for n in notifs])
    finally:
        db.close()

@api_bp.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
def mark_read(notif_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    db = SessionLocal()
    try:
        notif = db.query(Notification).filter_by(id=notif_id, user_id=user_id).first()
        if notif:
            notif.is_read = True
            db.commit()
            return jsonify({'success': True})
        return jsonify({'error': 'Notification not found'}), 404
    finally:
        db.close()

@api_bp.route('/api/skills')
def list_skills():
    db = SessionLocal()
    try:
        skills = db.query(Skill).all()
        return jsonify([s.to_dict() for s in skills])
    finally:
        db.close()
