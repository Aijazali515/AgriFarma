# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from agrifarma.services.security import admin_required as admin_only
from sqlalchemy import or_

from agrifarma.extensions import db
from agrifarma.forms.consultancy import ConsultantRegisterForm
from agrifarma.forms.message import MessageForm
from agrifarma.models.consultancy import Consultant, CONSULTANT_CATEGORIES, APPROVAL_STATUSES
from agrifarma.models.message import Message
from agrifarma.models.user import User

bp = Blueprint('consultancy', __name__)


@bp.route('/consultant/register', methods=['GET', 'POST'])
@login_required
def consultant_register():
    # If user already applied, show status
    existing = Consultant.query.filter_by(user_id=current_user.id).first()
    form = ConsultantRegisterForm()
    if form.validate_on_submit():
        if existing:
            flash('You have already applied as a consultant.', 'warning')
            return redirect(url_for('consultancy.consultant_register'))
        consultant = Consultant(
            user_id=current_user.id,
            category=form.category.data,
            expertise_level=form.expertise_level.data,
            contact_email=form.contact_email.data,
            approval_status='Pending',
        )
        db.session.add(consultant)
        db.session.commit()
        flash('Application submitted. Await admin approval.', 'success')
        return redirect(url_for('consultancy.consultants'))
    return render_template('consultant_register.html', form=form, existing=existing)


@bp.route('/consultants')
def consultants():
    category = request.args.get('category', default='', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = 12
    query = Consultant.query.filter_by(approval_status='Approved')
    if category:
        query = query.filter_by(category=category)
    pagination = query.order_by(Consultant.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('consultant_list.html', consultants=pagination.items, pagination=pagination, categories=CONSULTANT_CATEGORIES, selected_category=category)


@bp.route('/consultant/<int:consultant_id>')
def consultant_profile(consultant_id: int):
    consultant = db.session.get(Consultant, consultant_id)
    if not consultant or consultant.approval_status != 'Approved':
        abort(404)
    message_form = MessageForm()
    return render_template('consultant_profile.html', consultant=consultant, message_form=message_form)

@bp.route('/consultancy/message/<int:consultant_id>', methods=['POST'])
@login_required
def send_message(consultant_id: int):
    """Send a message to a consultant"""
    consultant = db.session.get(Consultant, consultant_id)
    if not consultant or consultant.approval_status != 'Approved':
        abort(404)
    
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            receiver_id=consultant.user_id,
            subject=form.subject.data,
            content=form.content.data
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('consultancy.consultant_profile', consultant_id=consultant_id))

@bp.route('/consultancy/inbox')
@login_required
def inbox():
    """View user's received messages"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    messages = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    unread_count = Message.query.filter_by(receiver_id=current_user.id, read=False).count()
    
    return render_template('inbox.html', messages=messages, unread_count=unread_count)

@bp.route('/consultancy/message/<int:message_id>')
@login_required
def view_message(message_id: int):
    """View a single message"""
    message = db.session.get(Message, message_id)
    
    if not message:
        abort(404)
    
    # Only receiver can view
    if message.receiver_id != current_user.id:
        abort(403)
    
    # Mark as read
    if not message.read:
        message.mark_as_read()
    
    return render_template('view_message.html', message=message)

@bp.route('/admin/consultants', methods=['GET', 'POST'])
@login_required
@admin_only
def admin_consultants():

    # Approve action via POST
    if request.method == 'POST':
        cid = request.form.get('consultant_id', type=int)
        action = request.form.get('action')
        consultant = db.session.get(Consultant, cid)
        if not consultant:
            abort(404)
        if action == 'approve':
            consultant.approval_status = 'Approved'
        elif action == 'reject':
            consultant.approval_status = 'Rejected'
        db.session.commit()
        flash('Consultant status updated.', 'info')
        return redirect(url_for('consultancy.admin_consultants'))

    pending = Consultant.query.filter_by(approval_status='Pending').order_by(Consultant.created_at.asc()).all()
    approved = Consultant.query.filter_by(approval_status='Approved').order_by(Consultant.created_at.desc()).limit(20).all()
    return render_template('admin_consultant_review.html', pending=pending, approved=approved, categories=CONSULTANT_CATEGORIES)
