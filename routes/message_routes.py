from functools import wraps
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from sqlalchemy import create_engine, or_, and_, desc
from sqlalchemy.orm import sessionmaker

from config import Config
from models import User, Student, Company, College, Message, Notification

message_bp = Blueprint('messages', __name__)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access messages.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_user_display_name(user):
    if not user:
        return "User"
    if user.student_profile:
        return user.student_profile.full_name
    if user.company_profile:
        return user.company_profile.company_name
    if user.college_profile:
        return user.college_profile.college_name
    if user.role == 'admin':
        return "System Administrator"
    return user.email.split('@')[0].capitalize()


@message_bp.route('/messages')
@login_required
def inbox():
    current_uid = session.get('user_id')
    db = SessionLocal()
    try:
        # Get all potential contacts (companies if student, students if company, etc.)
        all_companies = db.query(Company).all()
        all_students = db.query(Student).all()
        target_uid = request.args.get('uid', type=int)

        return render_template(
            'messages.html',
            current_uid=current_uid,
            target_uid=target_uid,
            companies=all_companies,
            students=all_students
        )
    finally:
        db.close()


@message_bp.route('/api/messages/conversations')
@login_required
def api_conversations():
    current_uid = session.get('user_id')
    db = SessionLocal()
    try:
        # Fetch all messages where current user is sender or recipient
        msgs = db.query(Message).filter(
            or_(Message.sender_id == current_uid, Message.recipient_id == current_uid)
        ).order_by(desc(Message.created_at)).all()

        partner_ids = []
        conversations_map = {}

        for m in msgs:
            partner_id = m.recipient_id if m.sender_id == current_uid else m.sender_id
            if partner_id not in conversations_map:
                partner_ids.append(partner_id)
                partner_user = db.query(User).filter_by(id=partner_id).first()
                conversations_map[partner_id] = {
                    'partner_id': partner_id,
                    'partner_name': get_user_display_name(partner_user),
                    'partner_role': partner_user.role if partner_user else 'user',
                    'last_message': m.content,
                    'last_time': m.created_at.strftime('%b %d, %H:%M') if m.created_at else '',
                    'unread_count': 0
                }

            if m.recipient_id == current_uid and not m.is_read:
                conversations_map[partner_id]['unread_count'] += 1

        conv_list = [conversations_map[pid] for pid in partner_ids]
        return jsonify(conv_list)
    finally:
        db.close()


@message_bp.route('/api/messages/history/<int:other_id>')
@login_required
def api_message_history(other_id):
    current_uid = session.get('user_id')
    db = SessionLocal()
    try:
        other_user = db.query(User).filter_by(id=other_id).first()
        if not other_user:
            return jsonify({'error': 'User not found'}), 404

        msgs = db.query(Message).filter(
            or_(
                and_(Message.sender_id == current_uid, Message.recipient_id == other_id),
                and_(Message.sender_id == other_id, Message.recipient_id == current_uid)
            )
        ).order_by(Message.created_at.asc()).all()

        # Mark unread incoming messages as read
        unread_msgs = [m for m in msgs if m.recipient_id == current_uid and not m.is_read]
        for m in unread_msgs:
            m.is_read = True
        if unread_msgs:
            db.commit()

        return jsonify({
            'partner_name': get_user_display_name(other_user),
            'partner_role': other_user.role,
            'messages': [m.to_dict() for m in msgs]
        })
    finally:
        db.close()


@message_bp.route('/api/messages/send', methods=['POST'])
@login_required
def api_send_message():
    current_uid = session.get('user_id')
    data = request.get_json() or {}
    recipient_id = data.get('recipient_id')
    content = (data.get('content') or '').strip()

    if not recipient_id or not content:
        return jsonify({'error': 'Recipient and message content required'}), 400

    db = SessionLocal()
    try:
        sender_user = db.query(User).filter_by(id=current_uid).first()
        recipient_user = db.query(User).filter_by(id=recipient_id).first()

        if not recipient_user:
            return jsonify({'error': 'Recipient user not found'}), 404

        msg = Message(
            sender_id=current_uid,
            recipient_id=recipient_id,
            content=content,
            is_read=False
        )
        db.add(msg)

        # Create system notification for recipient
        sender_name = get_user_display_name(sender_user)
        db.add(Notification(
            user_id=recipient_id,
            title=f"New Message from {sender_name}",
            message=content[:100] + ('...' if len(content) > 100 else ''),
            category="Message"
        ))

        db.commit()
        return jsonify({
            'success': True,
            'message': msg.to_dict()
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@message_bp.route('/api/messages/unread-count')
@login_required
def api_unread_count():
    current_uid = session.get('user_id')
    db = SessionLocal()
    try:
        count = db.query(Message).filter_by(recipient_id=current_uid, is_read=False).count()
        return jsonify({'unread_count': count})
    finally:
        db.close()
