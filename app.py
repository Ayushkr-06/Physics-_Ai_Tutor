import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3
import json
from datetime import datetime, timedelta
import random
import hashlib
from dotenv import load_dotenv
from gemini_utils import GeminiAI
import re

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'physics-tutor-secret-key-enhanced-2025'

# Add custom filters and functions to Jinja2 environment
app.jinja_env.globals.update(chr=chr)

def format_datetime(value):
    """Format datetime string to readable format"""
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        return value

app.jinja_env.filters['datetime'] = format_datetime

# Initialize AI helper
try:
    ai = GeminiAI()
    print("✅ Gemini AI initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Gemini AI: {e}")
    ai = None

def init_db():
    """Initialize Enhanced SQLite database with all required tables"""
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # Enhanced Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            dob TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            learning_goal TEXT,
            language TEXT DEFAULT 'English',
            mobile_number TEXT,
            gender TEXT,
            current_class INTEGER DEFAULT 10,
            school_name TEXT,
            subjects TEXT DEFAULT 'Physics',
            board TEXT DEFAULT 'CBSE',
            study_mode TEXT DEFAULT 'Self-paced',
            notification_preferences TEXT DEFAULT 'email',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Quiz results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT DEFAULT 'Physics',
            chapter TEXT,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            difficulty_level TEXT DEFAULT 'medium',
            quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    # Study sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            session_date DATE NOT NULL,
            chapter TEXT,
            topics_completed INTEGER DEFAULT 0,
            time_spent INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Enhanced database initialized successfully")

def hash_password(dob):
    """Create a simple hash from DOB for password verification"""
    return hashlib.md5(dob.encode()).hexdigest()

def format_markdown_content(text):
    """Convert markdown-style content to HTML for proper display"""
    from markupsafe import Markup
    
    if not text:
        return text

    # Initialize the HTML content
    html_parts = []
    
    # Split into paragraphs and sections
    current_section = []
    
    # Split into paragraphs
    paragraphs = text.split('\n\n')
    bullet_count = 0  # Track number of bullet points to limit emoji usage
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Check if it's a header
        if paragraph.startswith('# '):
            title = paragraph[2:].replace('**', '')
            current_section.append(f'<div class="study-plan-header"><h1>{title}</h1></div>')
            continue
            
        if paragraph.startswith('## '):
            subtitle = paragraph[3:].replace('**', '')
            # Add appropriate emoji based on section title
            emoji = ''
            if 'day' in subtitle.lower():
                emoji = '📅 '
            elif 'topic' in subtitle.lower():
                emoji = '📚 '
            elif 'practice' in subtitle.lower():
                emoji = '✍️ '
            elif 'test' in subtitle.lower() or 'quiz' in subtitle.lower():
                emoji = '📝 '
            current_section.append(f'<h2 class="study-section">{emoji}{subtitle}</h2>')
            continue
            
        if paragraph.startswith('### '):
            subheader = paragraph[4:].replace('**', '')
            current_section.append(f'<h3 class="study-subsection">{subheader}</h3>')
            continue
            
        # Handle bullet points with limited emojis
        if any(line.strip().startswith(('- ', '* ')) for line in paragraph.split('\n')):
            lines = paragraph.split('\n')
            current_section.append('<ul class="study-list">')
            for line in lines:
                line = line.strip()
                if line.startswith(('- ', '* ')):
                    line = line[2:]
                    # Process bold and italic before adding to list
                    line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
                    line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', line)
                    # Only add bullet emoji for first 3 items in a list
                    bullet_emoji = '• ' if bullet_count >= 3 else '📌 '
                    current_section.append(f'<li>{bullet_emoji}{line}</li>')
                    bullet_count += 1
            current_section.append('</ul>')
            continue
            
        # Regular paragraph
        # Replace bold and italic markers before adding to HTML
        paragraph = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', paragraph)
        paragraph = re.sub(r'\*(.*?)\*', r'<em>\1</em>', paragraph)
        
        # Check if it's a special section
        if paragraph.lower().startswith('important:'):
            current_section.append(f'<div class="important-note">💡 {paragraph}</div>')
        elif paragraph.lower().startswith('tip:'):
            current_section.append(f'<div class="study-tip">✨ {paragraph}</div>')
        else:
            current_section.append(f'<p class="study-text">{paragraph}</p>')
    
    # Join all sections with proper container
    formatted_content = '\n'.join(current_section)
    
    # Return complete HTML with proper study plan container
    return Markup(f'<div class="study-plan">{formatted_content}</div>')
    
    # Close the main container and return
    html_parts.append('</div>')
    return '\n'.join(html_parts)
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            if current_list:
                current_section.append(f'<ul class="study-plan-list">{" ".join(current_list)}</ul>')
                current_list = []
            continue
        
        # Handle headers
        if line.startswith('# '):
            title = line[2:]
            sections.append(f'<div class="study-plan-header"><h1>{title}</h1></div>')
        elif line.startswith('## '):
            if current_list:
                current_section.append(f'<ul class="study-plan-list">{" ".join(current_list)}</ul>')
                current_list = []
            if current_section:
                sections.append(f'<div class="study-plan-section">{"".join(current_section)}</div>')
            current_section = []
            heading = line[3:]
            current_section.append(f'<h2>{heading}</h2>')
        elif line.startswith('### '):
            if current_list:
                current_section.append(f'<ul class="study-plan-list">{" ".join(current_list)}</ul>')
                current_list = []
            heading = line[4:]
            current_section.append(f'<h3>{heading}</h3>')
        # Handle list items
        elif line.startswith('- ') or line.startswith('* '):
            item = line[2:]
            current_list.append(f'<li class="study-plan-item"><span class="study-icon">📝</span>{item}</li>')
        # Handle topics
        elif line.startswith('Topics to Cover:'):
            if current_list:
                current_section.append(f'<ul class="study-plan-list">{" ".join(current_list)}</ul>')
                current_list = []
            current_section.append('<div class="topics-section"><h4>� Topics to Cover:</h4>')
        elif line.startswith('Practice Problems:'):
            if current_list:
                current_section.append(f'<ul class="study-plan-list">{" ".join(current_list)}</ul>')
                current_list = []
            current_section.append('<div class="practice-section"><h4>🎯 Practice Problems:</h4>')
        # Regular paragraphs
        else:
            if current_list:
                current_section.append(f'<ul class="study-plan-list">{" ".join(current_list)}</ul>')
                current_list = []
            current_section.append(f'<p class="study-plan-text">{line}</p>')
    
    # Add any remaining items
    if current_list:
        current_section.append(f'<ul class="study-plan-list">{" ".join(current_list)}</ul>')
    if current_section:
        sections.append(f'<div class="study-plan-section">{"".join(current_section)}</div>')
    
    # Join all sections
    formatted_content = "".join(sections)
    return f'<div class="study-plan-container">{formatted_content}</div>'
    
    # Wrap in main container
    return f'<div class="study-plan-container">{formatted}</div>'
    
    return formatted
    
    return formatted

# Class 10 Physics Chapters
PHYSICS_CHAPTERS = [
    "Light - Reflection and Refraction",
    "The Human Eye and the Colourful World", 
    "Electricity",
    "Magnetic Effects of Electric Current"
]

@app.route('/')
def index():
    """Landing page - check if user is logged in"""
    if 'student_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Enhanced user registration with proper error handling"""
    if request.method == 'POST':
        try:
            # Get form data with proper validation
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            dob = request.form.get('dob', '').strip()
            learning_goal = request.form.get('learning_goal', '').strip()
            language = request.form.get('language', 'English')
            
            # Debug prints
            print(f"Registration attempt: {full_name}, {email}, {dob}")
            
            # Validation
            if not full_name:
                flash('Full name is required!', 'danger')
                return render_template('register.html')
            
            if not email or '@' not in email:
                flash('Valid email address is required!', 'danger')
                return render_template('register.html')
            
            if not dob:
                flash('Date of birth is required!', 'danger')
                return render_template('register.html')
            
            # Convert DOB to DDMMYYYY format for password
            try:
                dob_parts = dob.split('-')  # YYYY-MM-DD from HTML date input
                if len(dob_parts) != 3:
                    raise ValueError("Invalid date format")
                
                dob_password = f"{dob_parts[2]}{dob_parts[1]}{dob_parts[0]}"  # DDMMYYYY
                password_hash = hash_password(dob_password)
                
                print(f"DOB password will be: {dob_password}")
                
            except Exception as e:
                print(f"DOB conversion error: {e}")
                flash('Invalid date format!', 'danger')
                return render_template('register.html')
            
            # Database operations
            conn = sqlite3.connect('students.db')
            cursor = conn.cursor()
            
            try:
                # Check if email already exists
                cursor.execute('SELECT id FROM students WHERE email = ?', (email,))
                if cursor.fetchone():
                    flash('Email already registered! Please sign in.', 'warning')
                    conn.close()
                    return redirect(url_for('login'))
                
                # Insert new user
                cursor.execute('''
                    INSERT INTO students (full_name, email, dob, password_hash, learning_goal, language, current_class, subjects)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (full_name, email, dob, password_hash, learning_goal, language, 10, 'Physics'))
                
                student_id = cursor.lastrowid
                conn.commit()
                
                if not student_id:
                    raise Exception("Failed to create user record")
                
                print(f"✅ User created with ID: {student_id}")
                
            except sqlite3.IntegrityError as e:
                print(f"Database integrity error: {e}")
                flash('Email already exists or database error!', 'danger')
                conn.rollback()
                conn.close()
                return render_template('register.html')
            except Exception as e:
                print(f"Database error: {e}")
                flash(f'Database error: {str(e)}', 'danger')
                conn.rollback()
                conn.close()
                return render_template('register.html')
            finally:
                conn.close()
            
            # Set session
            session['student_id'] = student_id
            session['name'] = full_name
            session['email'] = email
            session['class_level'] = 10
            session['subjects'] = ['Physics']
            session['learning_goal'] = learning_goal
            session['language'] = language
            session['quiz_difficulty'] = 'medium'
            
            flash(f'Welcome {full_name}! Your account has been created successfully. Your login password is your DOB in DDMMYYYY format ({dob_password}).', 'success')
            print(f"✅ New user registered: {full_name} ({email})")
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            print(f"❌ Registration error: {e}")
            flash(f'Registration failed: {str(e)}. Please try again.', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with email and DOB"""
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            dob_password = request.form.get('dob_password', '').strip()
            
            if not email or not dob_password:
                flash('Please enter both email and date of birth!', 'danger')
                return render_template('login.html')
            
            # Verify user
            conn = sqlite3.connect('students.db')
            cursor = conn.cursor()
            
            password_hash = hash_password(dob_password)
            cursor.execute('''
                SELECT id, full_name, learning_goal, language, current_class, subjects 
                FROM students 
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                # Set session
                session['student_id'] = user[0]
                session['name'] = user[1]
                session['email'] = email
                session['learning_goal'] = user[2] or ''
                session['language'] = user[3] or 'English'
                session['class_level'] = user[4] or 10
                session['subjects'] = json.loads(user[5]) if user[5] else ['Physics']
                session['quiz_difficulty'] = 'medium'
                
                flash(f'Welcome back, {user[1]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or date of birth!', 'danger')
                return render_template('login.html')
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            flash('Login failed. Please try again.', 'danger')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    name = session.get('name', 'User')
    session.clear()
    flash(f'Goodbye {name}! You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """User settings page"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Get form data
            mobile_number = request.form.get('mobile_number', '').strip()
            gender = request.form.get('gender', '').strip()
            school_name = request.form.get('school_name', '').strip()
            board = request.form.get('board', 'CBSE')
            study_mode = request.form.get('study_mode', 'Self-paced')
            notification_preferences = ','.join(request.form.getlist('notifications'))
            
            # Update database
            conn = sqlite3.connect('students.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE students 
                SET mobile_number = ?, gender = ?, school_name = ?, 
                    board = ?, study_mode = ?, notification_preferences = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (mobile_number, gender, school_name, board, study_mode, 
                  notification_preferences, session['student_id']))
            
            conn.commit()
            conn.close()
            
            flash('Settings updated successfully!', 'success')
            
        except Exception as e:
            print(f"❌ Settings update error: {e}")
            flash('Failed to update settings. Please try again.', 'danger')
    
    # Get current user data
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT full_name, email, dob, mobile_number, gender, current_class,
               school_name, board, study_mode, notification_preferences,
               learning_goal, language
        FROM students WHERE id = ?
    ''', (session['student_id'],))
    
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        user_info = {
            'full_name': user_data[0],
            'email': user_data[1],
            'dob': user_data[2],
            'mobile_number': user_data[3] or '',
            'gender': user_data[4] or '',
            'current_class': user_data[5] or 10,
            'school_name': user_data[6] or '',
            'board': user_data[7] or 'CBSE',
            'study_mode': user_data[8] or 'Self-paced',
            'notification_preferences': (user_data[9] or 'email').split(','),
            'learning_goal': user_data[10] or '',
            'language': user_data[11] or 'English'
        }
    else:
        user_info = {}
    
    return render_template('settings.html', user_info=user_info)

@app.route('/quiz')
def quiz():
    """Physics quiz page with correct chapters"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('quiz_start.html', 
                         subject='Physics', 
                         chapters=PHYSICS_CHAPTERS,
                         class_level=10)

@app.route('/quiz/start', methods=['POST'])
def start_quiz():
    """Start a new quiz session with selected parameters"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
        
    try:
        # Get quiz parameters from form
        chapter = request.form.get('chapter')
        if not chapter:
            flash('Please select a chapter', 'danger')
            return redirect(url_for('quiz'))
            
        level = request.form.get('level', 'medium')
        try:
            num_questions = int(request.form.get('num_questions', 10))
        except ValueError:
            flash('Invalid number of questions', 'danger')
            return redirect(url_for('quiz'))
        
        # Load and filter questions
        try:
            with open('data/quiz_questions.json', 'r') as f:
                all_questions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading questions: {e}")
            flash('Failed to load questions. Please try again.', 'danger')
            return redirect(url_for('quiz'))
            
        # Filter questions by chapter and level
        filtered_questions = [
            q for q in all_questions 
            if q.get('chapter') == chapter and q.get('difficulty', 'Medium').lower() == level.lower()
        ]
        
        # If not enough questions from JSON, generate with AI
        if len(filtered_questions) < num_questions and ai:
            try:
                ai_questions = ai.generate_quiz_questions(
                    subject='Physics',
                    class_level=10,
                    n=num_questions - len(filtered_questions),
                    difficulty=level,
                    topic=chapter
                )
                if ai_questions:
                    filtered_questions.extend(ai_questions)
            except Exception as e:
                print(f"Error generating AI questions: {e}")
                # Continue with available questions
                pass
        
        # Randomly select required number of questions
        if not filtered_questions:
            flash('No questions available for selected criteria', 'danger')
            return redirect(url_for('quiz'))
            
        selected_questions = random.sample(filtered_questions, min(num_questions, len(filtered_questions)))
        
        # Store quiz state in session
        session['current_quiz_questions'] = selected_questions
        session['current_quiz_chapter'] = chapter
        session['quiz_difficulty'] = level
        session['quiz_start_time'] = datetime.now().isoformat()
        
        return render_template('quiz_active.html',
                            questions=selected_questions,
                            chapter=chapter,
                            level=level)
                            
    except Exception as e:
        print(f"Error starting quiz: {e}")
        flash('An error occurred while starting the quiz. Please try again.', 'danger')
        return redirect(url_for('quiz'))

@app.route('/get_quiz_questions')
def get_quiz_questions():
    """Get AI-generated physics quiz questions for specific topic and difficulty"""
    if not ai:
        return jsonify({'error': 'AI service not available'}), 500
        
    topic = request.args.get('topic', '')  # Topic selection is passed from frontend
    difficulty = session.get('quiz_difficulty', 'medium')
    
    try:
        # Load questions from JSON first
        with open('data/quiz_questions.json', 'r') as f:
            all_questions = json.load(f)
            
        filtered_questions = []
        if topic:  # If topic is selected
            filtered_questions = [q for q in all_questions if topic.lower() in q['chapter'].lower()]
        else:  # Mixed topics
            filtered_questions = all_questions
            
        # Filter by difficulty if specified
        if difficulty == 'easy':
            filtered_questions = [q for q in filtered_questions if q.get('difficulty', 'Medium') == 'Easy']
        elif difficulty == 'hard':
            filtered_questions = [q for q in filtered_questions if q.get('difficulty', 'Medium') == 'Medium']
            
        # If we don't have enough questions from JSON, generate more with AI
        if len(filtered_questions) < 10:
            ai_questions = ai.generate_quiz_questions(
                subject='Physics',
                class_level=10,
                n=10-len(filtered_questions),  # Generate remaining needed questions
                difficulty=difficulty,
                topic=topic
            )
            if ai_questions:
                filtered_questions.extend(ai_questions)
        
        # Randomly select 10 questions
        selected_questions = random.sample(filtered_questions, min(10, len(filtered_questions)))
        
        if not selected_questions:
            return jsonify({'error': 'No questions available for selected topic'}), 500
        
        # Store quiz state in session
        session['current_quiz_subject'] = 'Physics'
        session['current_quiz_topic'] = topic
        session['current_quiz_questions'] = selected_questions
        session['quiz_start_time'] = datetime.now().isoformat()
        
        print(f"✅ Generated {len(selected_questions)} questions for topic: {topic}")
        return jsonify({'questions': selected_questions})
        
    except Exception as e:
        print(f"❌ Error generating quiz: {e}")
        return jsonify({'error': f'Failed to generate questions: {str(e)}'}), 500

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    """Submit quiz answers and calculate score"""
    try:
        data = request.get_json()
        answers = data.get('answers', [])
        questions = session.get('current_quiz_questions', [])
        subject = session.get('current_quiz_subject', 'Physics')
        chapter = session.get('current_quiz_chapter', 'General Physics')
        quiz_start_time = datetime.fromisoformat(session.get('quiz_start_time', datetime.now().isoformat()))

        if not questions:
            return jsonify({'error': 'No quiz questions found'}), 400

        # Calculate score and prepare questions with answers
        correct_answers = 0
        quiz_data = []
        
        for i, question in enumerate(questions):
            if i >= len(answers):
                continue
                
            user_answer = answers[i]
            # Handle both formats of correct answer
            correct = question.get('correct_answer', None)
            if correct is None:
                correct = question.get('correct', 0)
            elif isinstance(correct, str):
                try:
                    correct = question['options'].index(correct)
                except ValueError:
                    correct = 0
            
            is_correct = user_answer == correct
            if is_correct:
                correct_answers += 1
                
            # Get or generate short explanation
            explanation = question.get('explanation', '')
            if not explanation and ai:
                try:
                    explanation = ai.get_quick_explanation(
                        question=question['question'],
                        correct_answer=question['options'][correct],
                        subject='Physics',
                        class_level=10
                    )
                except:
                    explanation = "Explanation will be provided by the tutor."
            
            quiz_data.append({
                'question': question['question'],
                'options': question['options'],
                'user_answer': user_answer,
                'correct_answer': correct,
                'explanation': explanation,
                'is_correct': is_correct
            })

        score = int((correct_answers / len(questions)) * 100) if questions else 0
        time_taken = (datetime.now() - quiz_start_time).seconds

        # Store quiz result
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO quiz_results (student_id, subject, chapter, score, total_questions, difficulty_level)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session['student_id'], subject, chapter, correct_answers, len(questions), session.get('quiz_difficulty', 'medium')))
        
        conn.commit()
        conn.close()

        # Store result data in session for results page
        session['quiz_results'] = {
            'score': score,
            'correct_count': correct_answers,
            'wrong_count': len(questions) - correct_answers,
            'time_taken': f"{time_taken // 60}:{time_taken % 60:02d}",
            'questions': quiz_data
        }

        # Adjust difficulty
        if score >= 80:
            session['quiz_difficulty'] = 'hard'
            next_message = "Excellent! Next quiz will be more challenging."
        elif score <= 40:
            session['quiz_difficulty'] = 'easy'
            next_message = "Let's strengthen the basics with easier questions."
        else:
            session['quiz_difficulty'] = 'medium'
            next_message = "Good progress! Keep practicing."

        return jsonify({'redirect': url_for('quiz_results')})

    except Exception as e:
        print(f"❌ Error submitting quiz: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/quiz/results')
def quiz_results():
    """Show detailed quiz results"""
    if 'student_id' not in session or 'quiz_results' not in session:
        return redirect(url_for('quiz'))
        
    results = session.get('quiz_results')
    return render_template('quiz_results.html', **results)

@app.route('/get_detailed_explanation/<int:question_index>')
def get_detailed_explanation(question_index):
    """Get detailed AI-generated explanation for a question"""
    if not ai or 'quiz_results' not in session:
        return jsonify({'error': 'Service not available'}), 500
        
    try:
        questions = session['quiz_results']['questions']
        if question_index >= len(questions):
            return jsonify({'error': 'Question not found'}), 404
            
        question = questions[question_index]
        detailed_explanation = ai.get_detailed_explanation(
            question=question['question'],
            correct_answer=question['options'][question['correct_answer']],
            user_answer=question['options'][question['user_answer']],
            subject='Physics',
            class_level=10,
            chapter=session.get('current_quiz_chapter', '')
        )
        
        # Format the explanation with proper HTML
        formatted_explanation = format_markdown_content(detailed_explanation)
        
        return jsonify({'explanation': formatted_explanation})
        
    except Exception as e:
        print(f"❌ Error generating detailed explanation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Enhanced student dashboard"""
    if 'student_id' not in session:
        return redirect(url_for('login'))

    try:
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()

        # Get chapter-wise performance
        cursor.execute('''
            SELECT chapter, AVG(score) as avg_score, COUNT(*) as quiz_count
            FROM quiz_results
            WHERE student_id = ?
            GROUP BY chapter
        ''', (session['student_id'],))
        quiz_performance = cursor.fetchall()

        # Calculate daily streak
        cursor.execute('''
            SELECT COUNT(DISTINCT session_date) as streak
            FROM study_sessions
            WHERE student_id = ? AND session_date >= date('now', '-7 days')
        ''', (session['student_id'],))
        streak_result = cursor.fetchone()
        daily_streak = streak_result[0] if streak_result else 0

        conn.close()

        # Generate focus areas using AI
        focus_areas = []
        if ai:
            focus_areas = ai.get_focus_areas(quiz_performance, PHYSICS_CHAPTERS)

        return render_template('dashboard.html',
                             quiz_performance=quiz_performance,
                             daily_streak=daily_streak,
                             focus_areas=focus_areas,
                             chapters=PHYSICS_CHAPTERS)

    except Exception as e:
        print(f"❌ Error loading dashboard: {e}")
        flash('Error loading dashboard data.', 'danger')
        return render_template('dashboard.html', quiz_performance=[], daily_streak=0, focus_areas=[], chapters=PHYSICS_CHAPTERS)

@app.route('/study_plan', methods=['GET', 'POST'])
def study_plan():
    """Generate enhanced study plan with proper formatting"""
    if 'student_id' not in session:
        return redirect(url_for('login'))

    if not ai:
        return render_template('study_plan.html',
                             study_plan="<div class='alert alert-warning'><strong>AI service not available.</strong> Please check your internet connection.</div>")

    try:
        # Initialize study plans in session if not exists
        if 'study_plans' not in session:
            session['study_plans'] = {}

        # Get student performance data for the specific chapter
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        
        if request.method == 'POST':
            plan_type = request.form.get('plan_type')
            chapter = request.form.get('chapter')
            
            if not chapter and plan_type == 'chapter':
                flash('Please select a chapter for the study plan', 'warning')
                return redirect(url_for('study_plan'))

            # Get performance data for the specific chapter
            if chapter:
                cursor.execute('''
                    SELECT chapter, AVG(score) as avg_score, COUNT(*) as attempts,
                           MAX(quiz_date) as last_attempt
                    FROM quiz_results
                    WHERE student_id = ? AND chapter = ?
                    GROUP BY chapter
                ''', (session['student_id'], chapter))
            else:
                cursor.execute('''
                    SELECT chapter, AVG(score) as avg_score, COUNT(*) as attempts,
                           MAX(quiz_date) as last_attempt
                    FROM quiz_results
                    WHERE student_id = ?
                    GROUP BY chapter
                ''', (session['student_id'],))
            
            performance_data = cursor.fetchall()
            conn.close()

            # Generate study plan with focused content
            topics = [chapter] if chapter else PHYSICS_CHAPTERS
            duration = 'week' if plan_type == 'chapter' else 'month'

            # Generate study plan based on type
            raw_study_plan = ai.generate_study_plan(
                class_level=session.get('class_level', 10),
                subjects=topics,
                learning_goal=session.get('learning_goal', ''),
                performance_data=performance_data,
                language=session.get('language', 'English'),
                duration=duration
            )

            # Format the study plan with proper HTML styling
            formatted_study_plan = format_markdown_content(raw_study_plan)

            # Save the plan in session
            if chapter:
                session['study_plans'][chapter] = {
                    'plan': formatted_study_plan,
                    'generated_at': datetime.now().isoformat(),
                    'type': 'chapter'
                }
            else:
                session['study_plans']['complete'] = {
                    'plan': formatted_study_plan,
                    'generated_at': datetime.now().isoformat(),
                    'type': 'complete'
                }
            session.modified = True

            print("✅ Enhanced study plan generated and saved successfully")
            return render_template('study_plan.html', 
                                study_plan=formatted_study_plan, 
                                chapters=PHYSICS_CHAPTERS,
                                show_form=True,
                                saved_plans=session['study_plans'])
        else:
            # Get chapter-wise performance for the overview
            cursor.execute('''
                SELECT chapter, 
                       ROUND(AVG(CAST(score AS FLOAT) * 100.0 / total_questions), 1) as avg_score, 
                       COUNT(*) as quiz_count
                FROM quiz_results
                WHERE student_id = ?
                GROUP BY chapter
            ''', (session['student_id'],))
            quiz_performance = cursor.fetchall()
            
            # Add default entries for chapters with no data
            existing_chapters = {row[0] for row in quiz_performance}
            for chapter in PHYSICS_CHAPTERS:
                if chapter not in existing_chapters:
                    # For chapters without quiz data, create placeholder entry
                    quiz_performance = list(quiz_performance)
                    quiz_performance.append((chapter, 0, 0))
            
            # Show the form and saved plans on GET request
            return render_template('study_plan.html', 
                                study_plan=None,
                                chapters=PHYSICS_CHAPTERS,
                                show_form=True,
                                saved_plans=session.get('study_plans', {}),
                                quiz_performance=quiz_performance)

    except Exception as e:
        print(f"❌ Error generating study plan: {e}")
        error_plan = f"""
        <div class='alert alert-danger'>
            <h5><i class='fas fa-exclamation-triangle'></i> Unable to generate study plan</h5>
            <p><strong>Error:</strong> {str(e)}</p>
            <p>Please check your internet connection and try again.</p>
        </div>
        """
        return render_template('study_plan.html', study_plan=error_plan)

@app.route('/chatbot')
def chatbot():
    """Enhanced AI chatbot page with modern UI"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    return render_template('chatbot.html', 
                         user=session.get('name', 'User'),
                         email=session.get('email', ''),
                         chapters=PHYSICS_CHAPTERS)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with Gemini AI"""
    if not ai:
        return jsonify({'error': 'AI service not available'}), 500
    
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        history = data.get('history', [])

        if not message:
            return jsonify({'error': 'No message provided'}), 400

        # Get response from Gemini AI
        context = {
            'name': session.get('name', 'User'),
            'class_level': session.get('class_level', 10),
            'language': session.get('language', 'English'),
            'subjects': PHYSICS_CHAPTERS,
            'chat_history': history[-5:]  # Use last 5 messages for context
        }

        response = ai.chat(
            message=message,
            context=context
        )
        
        # Return raw HTML response (already formatted by format_markdown_content)
        return jsonify({
            'response': response,
            'status': 'success'
        })

    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({
            'error': f'Failed to process message: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/ask_doubt', methods=['POST'])
def ask_doubt():
    """Enhanced doubt solving with proper formatting"""
    if not ai:
        return jsonify({'error': 'AI service not available'}), 500

    try:
        data = request.get_json()
        question = data.get('question', '').strip()

        if not question:
            return jsonify({'error': 'No question provided'}), 400

        # Get AI response
        raw_response = ai.solve_doubt(
            question=question,
            class_level=session.get('class_level', 10),
            language=session.get('language', 'English'),
            subjects=PHYSICS_CHAPTERS
        )

        # Format the response with proper HTML styling
        formatted_response = format_markdown_content(raw_response)

        print(f"✅ Enhanced doubt solved for: {question[:50]}...")
        return jsonify({'response': formatted_response})

    except Exception as e:
        print(f"❌ Error solving doubt: {e}")
        error_response = f"""
        <div class='alert alert-danger'>
            <h6><i class='fas fa-exclamation-triangle'></i> Unable to process your question</h6>
            <p><strong>Error:</strong> {str(e)}</p>
            <p>Please try rephrasing your question or check your internet connection.</p>
        </div>
        """
        return jsonify({'response': error_response})

@app.route('/get_motivation')
def get_motivation():
    """Get enhanced motivational content with proper error handling"""
    if not ai:
        return jsonify({
            'motivation': '🌟 <strong>Keep learning and stay motivated!</strong> Every step forward is progress! 💪',
            'streak': 0,
            'performance': None,
            'quizCount': 0
        })
        
    if 'student_id' not in session:
        return jsonify({
            'motivation': '🌟 <strong>Ready to start your physics journey?</strong> Sign in to get personalized motivation! 📚',
            'streak': 0,
            'performance': None,
            'quizCount': 0
        })
        
    try:

        # Get recent performance
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        
        # Get quiz performance
        cursor.execute('''
            SELECT AVG(score) as recent_avg, COUNT(*) as quiz_count
            FROM quiz_results
            WHERE student_id = ? AND quiz_date >= date('now', '-7 days')
        ''', (session['student_id'],))
        result = cursor.fetchone()
        recent_performance = result[0] if result and result[0] else 50
        quiz_count = result[1] if result else 0
        
        # Get study streak
        cursor.execute('''
            SELECT COUNT(DISTINCT session_date) as streak
            FROM study_sessions
            WHERE student_id = ? AND session_date >= date('now', '-7 days')
        ''', (session['student_id'],))
        streak_result = cursor.fetchone()
        study_streak = streak_result[0] if streak_result else 0
        
        conn.close()

        # Generate personalized motivational content with dynamic inspiration
        if quiz_count == 0 and study_streak == 0:
            motivation = "🌟 <strong>Welcome to your physics journey!</strong> Take your first quiz to get started! 📚"
        elif study_streak > 5:  # High streak motivation
            motivation = f"🔥 <strong>Amazing {study_streak} day streak!</strong> Your dedication to physics is truly inspiring! Keep going! 💪"
        elif quiz_count > 0 and recent_performance >= 80:  # High performance motivation
            motivation = "⭐ <strong>Outstanding work!</strong> Your grasp of physics concepts is getting stronger every day! You're a natural! 🌟"
        elif quiz_count > 0 and recent_performance >= 60:  # Good progress motivation
            motivation = "📈 <strong>Great progress!</strong> Keep up this momentum and watch your understanding grow! 💫"
        else:
            # Generate personalized motivation based on context
            raw_motivation = ai.get_motivation(
                performance=recent_performance,
                name=session.get('name', 'Student'),
                language=session.get('language', 'English'),
                streak=study_streak,
                quiz_count=quiz_count
            )
            # Format motivation with HTML styling
            motivation = format_markdown_content(raw_motivation)

        # Add emojis based on context
        if "🌟" not in motivation and "⭐" not in motivation:
            motivation = f"✨ {motivation}"

        return jsonify({
            'motivation': motivation,
            'streak': study_streak,
            'performance': round(recent_performance, 1) if recent_performance else None,
            'quizCount': quiz_count
        })

    except Exception as e:
        print(f"❌ Error generating motivation: {e}")
        fallback_quotes = [
            f"🌟 <strong>Keep shining, {session.get('name', 'Student')}!</strong> Your dedication to physics is inspiring! �",
            "⚡ <strong>Physics mastery comes one concept at a time.</strong> You're making great progress! 🚀",
            "🎯 <strong>Every problem solved is a step toward excellence.</strong> Keep that momentum going! ✨",
            "💡 <strong>Your understanding grows with every study session.</strong> You're capable of amazing things! 🏆"
        ]
        return jsonify({
            'motivation': random.choice(fallback_quotes),
            'streak': 0,
            'performance': None,
            'quizCount': 0
        })

@app.route('/view_study_plan/<chapter>')
def view_study_plan(chapter):
    """View a previously generated study plan"""
    if 'student_id' not in session:
        return redirect(url_for('login'))
        
    saved_plans = session.get('study_plans', {})
    if chapter in saved_plans:
        return render_template('study_plan.html',
                             study_plan=saved_plans[chapter]['plan'],
                             chapters=PHYSICS_CHAPTERS,
                             show_form=True,
                             saved_plans=saved_plans,
                             viewing_chapter=chapter)
    else:
        flash('No study plan found for this chapter. Please generate one.', 'warning')
        return redirect(url_for('study_plan'))

@app.route('/mark_study_session', methods=['POST'])
def mark_study_session():
    """Mark study session as completed"""
    try:
        if 'student_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401

        data = request.get_json() or {}
        chapter = data.get('chapter', 'General Physics')
        
        today = datetime.now().date()
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO study_sessions (student_id, session_date, chapter, topics_completed)
            VALUES (?, ?, ?, 1)
        ''', (session['student_id'], today, chapter))

        conn.commit()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        print(f"❌ Error marking study session: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("🚀 Starting Enhanced Class 10 Physics AI Tutor...")
    print("=" * 60)
    print(f"📊 Database: {'✅ Ready' if os.path.exists('students.db') else '❌ Error'}")
    print(f"🤖 AI Service: {'✅ Ready' if ai else '❌ Error'}")
    print(f"📚 Chapters: {', '.join(PHYSICS_CHAPTERS)}")
    print(f"🔐 Authentication: ✅ Enhanced")
    print(f"⚙️  Settings: ✅ Complete")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
