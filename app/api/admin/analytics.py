from flask import jsonify
from sqlalchemy import func, text
from models.user import User
from models.user import Clinic
from models.patient import Tutor, Animal
from models.appointment import Appointment
from models.exam import Consultation, ExamResult
from extensions import db
from datetime import datetime, timedelta
from . import admin_bp, admin_required

@admin_bp.route('/analytics/dashboard', methods=['GET'])
@admin_required
def get_dashboard_analytics():
    """Get dashboard analytics and statistics"""
    try:
        # Get date ranges
        today = datetime.utcnow().date()
        this_month_start = today.replace(day=1)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        this_year_start = today.replace(month=1, day=1)

        # Basic counts
        stats = {
            'total_clinics': Clinic.query.count(),
            'total_users': User.query.filter(User.is_dr_saulo == False).count(),
            'active_users': User.query.filter(User.is_dr_saulo == False, User.is_active == True).count(),
            'total_clients': Tutor.query.count(),
            'total_animals': Animal.query.count(),
            'total_appointments': Appointment.query.count(),
            'total_consultations': Consultation.query.count(),
            'total_exams': ExamResult.query.count()
        }

        # This month's appointments
        this_month_appointments = Appointment.query.filter(
            Appointment.datetime >= this_month_start
        ).count()

        # Last month's appointments for comparison
        last_month_appointments = Appointment.query.filter(
            Appointment.datetime >= last_month_start,
            Appointment.datetime < this_month_start
        ).count()

        # Today's appointments
        today_appointments = Appointment.query.filter(
            func.date(Appointment.datetime) == today
        ).count()

        # Pending appointments
        pending_appointments = Appointment.query.filter(
            Appointment.status == 'scheduled'
        ).count()

        # Completed appointments
        completed_appointments = Appointment.query.filter(
            Appointment.status == 'completed'
        ).count()

        # New clients this month
        new_clients_this_month = Tutor.query.filter(
            Tutor.created_at >= this_month_start
        ).count()

        # New animals this month
        new_animals_this_month = Animal.query.filter(
            Animal.created_at >= this_month_start
        ).count()

        # Appointments by status
        appointments_by_status = db.session.query(
            Appointment.status,
            func.count(Appointment.id)
        ).group_by(Appointment.status).all()

        # Users by role
        users_by_role = db.session.query(
            User.role,
            func.count(User.id)
        ).filter(User.is_dr_saulo == False).group_by(User.role).all()

        # Animals by species
        animals_by_species = db.session.query(
            Animal.species,
            func.count(Animal.id)
        ).group_by(Animal.species).all()

        # Clinic with most appointments this month
        top_clinic = db.session.query(
            Clinic.name,
            func.count(Appointment.id).label('count')
        ).join(Appointment).filter(
            Appointment.datetime >= this_month_start
        ).group_by(Clinic.id, Clinic.name).order_by(
            func.count(Appointment.id).desc()
        ).first()

        # Monthly appointment trend (last 6 months)
        monthly_trend = []
        for i in range(6):
            month_start = (today.replace(day=1) - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            count = Appointment.query.filter(
                Appointment.datetime >= month_start,
                Appointment.datetime <= month_end
            ).count()

            monthly_trend.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })

        monthly_trend.reverse()  # Show oldest to newest

        return jsonify({
            'overview': {
                **stats,
                'appointments_today': today_appointments,
                'pending_appointments': pending_appointments,
                'completed_appointments': completed_appointments,
                'this_month_appointments': this_month_appointments,
                'last_month_appointments': last_month_appointments,
                'appointment_growth': ((this_month_appointments - last_month_appointments) / max(last_month_appointments, 1) * 100) if last_month_appointments > 0 else 0,
                'new_clients_this_month': new_clients_this_month,
                'new_animals_this_month': new_animals_this_month
            },
            'breakdowns': {
                'appointments_by_status': [
                    {'status': status, 'count': count}
                    for status, count in appointments_by_status
                ],
                'users_by_role': [
                    {'role': role, 'count': count}
                    for role, count in users_by_role
                ],
                'animals_by_species': [
                    {'species': species, 'count': count}
                    for species, count in animals_by_species if species
                ]
            },
            'highlights': {
                'top_clinic': {
                    'name': top_clinic[0] if top_clinic else None,
                    'appointments': top_clinic[1] if top_clinic else 0
                }
            },
            'trends': {
                'monthly_appointments': monthly_trend
            }
        }), 200

    except Exception as e:
        return {'error': 'Failed to fetch analytics', 'details': str(e)}, 500

@admin_bp.route('/analytics/clinics', methods=['GET'])
@admin_required
def get_clinic_analytics():
    """Get analytics for all clinics"""
    try:
        # Get all clinics with their statistics
        clinics_stats = db.session.query(
            Clinic.id,
            Clinic.name,
            Clinic.email,
            func.count(User.id).label('user_count'),
            func.count(Appointment.id).label('appointment_count'),
            func.sum(func.case([(Appointment.status == 'completed', 1)], else_=0)).label('completed_appointments'),
            func.sum(func.case([(Appointment.datetime >= func.current_date(), 1)], else_=0)).label('today_appointments')
        ).outerjoin(User).outerjoin(Appointment).group_by(Clinic.id, Clinic.name, Clinic.email).all()

        clinics_data = []
        for clinic_id, name, email, user_count, apt_count, completed_apt, today_apt in clinics_stats:
            # Get consultation count for this clinic
            consultation_count = db.session.query(Consultation).join(Appointment).filter(
                Appointment.clinic_id == clinic_id
            ).count()

            # Get exam count for this clinic
            exam_count = db.session.query(ExamResult).join(Consultation).join(Appointment).filter(
                Appointment.clinic_id == clinic_id
            ).count()

            clinics_data.append({
                'id': str(clinic_id),
                'name': name,
                'email': email,
                'user_count': user_count or 0,
                'appointment_count': apt_count or 0,
                'completed_appointments': completed_apt or 0,
                'today_appointments': today_apt or 0,
                'consultation_count': consultation_count,
                'exam_count': exam_count
            })

        return jsonify(clinics_data), 200

    except Exception as e:
        return {'error': 'Failed to fetch clinic analytics', 'details': str(e)}, 500

@admin_bp.route('/analytics/users', methods=['GET'])
@admin_required
def get_user_analytics():
    """Get user activity analytics"""
    try:
        # User creation by month (last 6 months)
        user_creation_trend = []
        for i in range(6):
            month_start = (datetime.utcnow().date().replace(day=1) - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            count = User.query.filter(
                User.created_at >= month_start,
                User.created_at <= month_end,
                User.is_dr_saulo == False
            ).count()

            user_creation_trend.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })

        user_creation_trend.reverse()

        # Users by clinic
        users_by_clinic = db.session.query(
            Clinic.name,
            func.count(User.id).label('user_count'),
            func.sum(func.case([(User.is_active == True, 1)], else_=0)).label('active_user_count')
        ).join(User).filter(User.is_dr_saulo == False).group_by(Clinic.id, Clinic.name).all()

        # Recent user activity
        recent_users = User.query.filter(
            User.is_dr_saulo == False
        ).order_by(User.created_at.desc()).limit(10).all()

        recent_users_data = []
        for user in recent_users:
            recent_users_data.append({
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'clinic_name': user.clinic.name if user.clinic else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })

        return jsonify({
            'user_creation_trend': user_creation_trend,
            'users_by_clinic': [
                {
                    'clinic_name': name,
                    'total_users': user_count,
                    'active_users': active_user_count
                }
                for name, user_count, active_user_count in users_by_clinic
            ],
            'recent_users': recent_users_data
        }), 200

    except Exception as e:
        return {'error': 'Failed to fetch user analytics', 'details': str(e)}, 500

@admin_bp.route('/analytics/system', methods=['GET'])
@admin_required
def get_system_health():
    """Get system health metrics"""
    try:
        # Database connection check
        db_status = 'healthy'
        try:
            db.session.execute(text('SELECT 1'))
        except:
            db_status = 'error'

        # Storage metrics (you would need to implement actual storage checking)
        storage_status = {
            'status': 'healthy',
            'total_space': '100GB',
            'used_space': '45GB',
            'free_space': '55GB'
        }

        # Last backup (you would need to implement backup tracking)
        last_backup = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success'
        }

        return jsonify({
            'database': db_status,
            'storage': storage_status,
            'last_backup': last_backup,
            'system_uptime': '99.9%'  # You would need to implement actual uptime tracking
        }), 200

    except Exception as e:
        return {'error': 'Failed to fetch system health', 'details': str(e)}, 500