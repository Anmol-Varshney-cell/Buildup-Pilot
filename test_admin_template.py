from app import app
from models import User, SupportTicket, SkillTest, Job, Application
from extensions import db
from flask import render_template

with app.app_context():
    try:
        # Get admin user
        admin_user = User.query.filter_by(email='admin@buildup.com').first()
        
        # Generate stats
        total_users = User.query.count() or 1
        active_users = User.query.filter_by(active=True).count()
        total_tickets = SupportTicket.query.count()
        closed_tickets = SupportTicket.query.filter_by(status='closed').count()
        student_users = User.query.filter_by(role='student').count() or 1
        students_with_applications = db.session.query(
            db.func.count(db.distinct(Application.user_id))
        ).scalar() or 0
        total_tests = SkillTest.query.count()
        passed_tests = SkillTest.query.filter(SkillTest.score >= 70).count()

        stats = {
            'total_students': User.query.filter_by(role='student').count(),
            'total_recruiters': User.query.filter_by(role='recruiter').count(),
            'total_jobs': Job.query.filter_by(is_active=True).count(),
            'total_applications': Application.query.count(),
            'active_tickets': SupportTicket.query.filter_by(status='open').count(),
            'active_users_rate': int((active_users / total_users) * 100),
            'application_rate': int((students_with_applications / student_users) * 100),
            'support_response_rate': int((closed_tickets / total_tickets) * 100) if total_tickets else 0,
            'problem_solve_rate': int((passed_tests / total_tests) * 100) if total_tests else 0
        }

        display_name = admin_user.email.split('@')[0] if admin_user.email else 'Admin'
        platform_help = f'Welcome back, {display_name}. Student progress and admin actions are live from current portal data.'
        
        print('Testing template rendering...')
        html = render_template('admin/dashboard.html', stats=stats, platform_help=platform_help)
        print('Template rendered successfully!')
        print(f'HTML length: {len(html)}')
        
    except Exception as e:
        print(f'Error rendering template: {e}')
        import traceback
        traceback.print_exc()
