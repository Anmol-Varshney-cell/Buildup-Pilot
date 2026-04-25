from flask_login import UserMixin
from datetime import datetime

from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    mobile = db.Column(db.String(15))
    otp = db.Column(db.String(6))
    otp_expires = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_active(self):
        return self.active
    
    profile = db.relationship('StudentProfile', backref='user', uselist=False)
    applications = db.relationship('Application', backref='user')
    tickets = db.relationship('SupportTicket', backref='user')
    skill_tests = db.relationship('SkillTest', backref='user')
    
    def __repr__(self):
        return f'<User {self.email} - {self.role}>'

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    profession = db.Column(db.String(100))
    college = db.Column(db.String(100))
    branch = db.Column(db.String(50))
    graduation_year = db.Column(db.Integer)
    skills = db.Column(db.Text)
    resume_path = db.Column(db.String(200))
    resume_score = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    portfolio = db.Column(db.String(200))
    profile_image_path = db.Column(db.String(200))
    portfolio_file_path = db.Column(db.String(200))
    weak_areas = db.Column(db.JSON)
    
    skill_tests = db.relationship('SkillTest', backref='profile')
    interview_readiness = db.relationship('InterviewReadiness', backref='profile')
    
    def __repr__(self):
        return f'<Profile {self.first_name} {self.last_name}>'

class Mentor(db.Model):
    __tablename__ = 'mentors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    expertise = db.Column(db.String(200))
    experience = db.Column(db.Integer)
    bio = db.Column(db.Text)
    hourly_rate = db.Column(db.Integer, default=0)
    availability = db.Column(db.JSON)
    
    bookings = db.relationship('MentorBooking', backref='mentor')
    reviews = db.relationship('MentorReview', backref='mentor')
    
    def __repr__(self):
        return f'<Mentor {self.name}>'

class MentorBooking(db.Model):
    __tablename__ = 'mentor_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'), nullable=False)
    booking_type = db.Column(db.String(50))
    scheduled_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer, default=30)
    status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    meeting_link = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'

class MentorReview(db.Model):
    __tablename__ = 'mentor_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.rating} stars>'

class SkillTest(db.Model):
    __tablename__ = 'skill_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'))
    test_type = db.Column(db.String(50))
    category = db.Column(db.String(50))
    score = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    time_taken = db.Column(db.Integer)
    tab_switches = db.Column(db.Integer, default=0)
    ai_detected = db.Column(db.Boolean, default=False)
    weak_topics = db.Column(db.JSON)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
    question_order = db.Column(db.JSON)
    
    questions = db.relationship('TestQuestion', backref='test')
    
    def __repr__(self):
        return f'<SkillTest {self.test_type} - Score: {self.score}>'

class TestQuestion(db.Model):
    __tablename__ = 'test_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('skill_tests.id'))
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON)
    correct_answer = db.Column(db.String(200))
    user_answer = db.Column(db.String(200))
    is_correct = db.Column(db.Boolean)
    topic = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Question {self.id}>'

class InterviewReadiness(db.Model):
    __tablename__ = 'interview_readiness'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'))
    communication_score = db.Column(db.Integer, default=0)
    dsa_score = db.Column(db.Integer, default=0)
    aptitude_score = db.Column(db.Integer, default=0)
    projects_score = db.Column(db.Integer, default=0)
    core_subjects_score = db.Column(db.Integer, default=0)
    overall_score = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Readiness Score: {self.overall_score}>'

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(20))
    work_mode = db.Column(db.String(20), default='onsite')
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    stipend = db.Column(db.Integer)
    required_skills = db.Column(db.Text)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    branch = db.Column(db.String(100))
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    applications = db.relationship('Application', backref='job')
    
    def __repr__(self):
        return f'<Job {self.title} at {self.company}>'

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(20), default='applied')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Application {self.id} - {self.status}>'

class MockInterview(db.Model):
    __tablename__ = 'mock_interviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    job_role = db.Column(db.String(100))
    status = db.Column(db.String(20), default='scheduled')
    scheduled_time = db.Column(db.DateTime)
    score = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    questions_asked = db.Column(db.JSON)
    answers_given = db.Column(db.JSON)
    proctoring_logs = db.Column(db.JSON)
    
    def __repr__(self):
        return f'<MockInterview {self.id} - {self.status}>'

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='medium')
    subject = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='open')
    screenshot = db.Column(db.String(200))
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    responses = db.relationship('TicketResponse', backref='ticket')
    
    def __repr__(self):
        return f'<Ticket {self.id} - {self.status}>'

class TicketResponse(db.Model):
    __tablename__ = 'ticket_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Response {self.id}>'

class CommunicationPractice(db.Model):
    __tablename__ = 'communication_practices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    practice_type = db.Column(db.String(20))
    topic = db.Column(db.String(200))
    content = db.Column(db.Text)
    duration = db.Column(db.Integer, default=0)
    clarity_rating = db.Column(db.Integer, default=0)
    structure_rating = db.Column(db.Integer, default=0)
    confidence_rating = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Communication Practice {self.id} - {self.practice_type}>'

class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    badge_icon = db.Column(db.String(50))
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    test_category = db.Column(db.String(50))
    score = db.Column(db.Integer)
    certificate_id = db.Column(db.String(50), unique=True)
    issued_by = db.Column(db.String(100), default='BUILD UP PILOT')
    validity_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    
    def __repr__(self):
        return f'<Certificate {self.name}>'

class Discussion(db.Model):
    __tablename__ = 'discussions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    category = db.Column(db.String(50))
    upvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    comments = db.relationship('DiscussionComment', backref='discussion')
    
    def __repr__(self):
        return f'<Discussion {self.id} - {self.title}>'

class DiscussionComment(db.Model):
    __tablename__ = 'discussion_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Comment {self.id}>'

class RoadMap(db.Model):
    __tablename__ = 'roadmaps'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_role = db.Column(db.String(100))
    duration_days = db.Column(db.Integer, default=30)
    roadmap_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RoadMap {self.target_role}>'
