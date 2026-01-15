from flask import Flask
from config import Config
from models import db, Professor, Class

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Register blueprints
    from auth import auth as auth_blueprint
    from routes import main as main_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    
    # Initialize database
    with app.app_context():
        db.create_all()
        
        # Create sample data if database is empty
        if not Professor.query.first():
            prof1 = Professor(prof_id='P001', name='Dr. Smith', course='Database Systems', course_id='CS101', schedule='Mon 10-12')
            prof2 = Professor(prof_id='P002', name='Dr. Johnson', course='Web Development', course_id='CS102', schedule='Wed 14-16')
            
            class1 = Class(course_id='CS101', professor='Dr. Smith', schedule='Mon 10-12', course='Database Systems', prof_id='P001')
            class2 = Class(course_id='CS102', professor='Dr. Johnson', schedule='Wed 14-16', course='Web Development', prof_id='P002')
            
            db.session.add_all([prof1, prof2, class1, class2])
            db.session.commit()
    
    return app