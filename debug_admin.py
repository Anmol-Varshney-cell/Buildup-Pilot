from app import app
from models import User, SupportTicket, SkillTest, Job, Application
from extensions import db

with app.app_context():
    try:
        total_users = User.query.count() or 1
        print(f'Total users: {total_users}')
        
        active_users = User.query.filter_by(active=True).count()
        print(f'Active users: {active_users}')
        
        total_tickets = SupportTicket.query.count()
        print(f'Total tickets: {total_tickets}')
        
        closed_tickets = SupportTicket.query.filter_by(status='closed').count()
        print(f'Closed tickets: {closed_tickets}')
        
        student_users = User.query.filter_by(role='student').count() or 1
        print(f'Student users: {student_users}')
        
        students_with_applications = db.session.query(
            db.func.count(db.distinct(Application.user_id))
        ).scalar() or 0
        print(f'Students with applications: {students_with_applications}')
        
        total_tests = SkillTest.query.count()
        print(f'Total tests: {total_tests}')
        
        passed_tests = SkillTest.query.filter(SkillTest.score >= 70).count()
        print(f'Passed tests: {passed_tests}')
        
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
        
        print(f'Stats calculated successfully: {stats}')
        print('Admin dashboard data generation: SUCCESS')
        
    except Exception as e:
        print(f'Error in admin dashboard: {e}')
        import traceback
        traceback.print_exc()
