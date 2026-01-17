import sqlite3
import json
from datetime import datetime
import hashlib

def create_tables_if_not_exist():
    """Ensure all required tables exist with correct schema"""
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    # Check if column exists and add if missing
    try:
        cursor.execute("PRAGMA table_info(quiz_results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'chapter' not in columns:
            cursor.execute('ALTER TABLE quiz_results ADD COLUMN chapter TEXT')
            print("✅ Added 'chapter' column to quiz_results table")
            
    except Exception as e:
        print(f"Warning: Could not check/add column: {e}")
    
    conn.commit()
    conn.close()

def get_physics_performance_summary(student_id):
    """Get detailed performance summary for all physics chapters"""
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COALESCE(chapter, 'General Physics') as chapter,
            COUNT(*) as quiz_count,
            AVG(score) as avg_score,
            MAX(score) as best_score,
            MIN(score) as lowest_score,
            MAX(quiz_date) as last_attempt
        FROM quiz_results 
        WHERE student_id = ?
        GROUP BY COALESCE(chapter, 'General Physics')
        ORDER BY avg_score DESC
    ''', (student_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [{
        'chapter': row[0],
        'quiz_count': row[1],
        'avg_score': round(row[2], 1),
        'best_score': row[3],
        'lowest_score': row[4],
        'last_attempt': row[5]
    } for row in results]

def validate_registration_data(form_data):
    """Validate registration form data"""
    errors = []
    
    if not form_data.get('full_name', '').strip():
        errors.append("Full name is required")
    
    email = form_data.get('email', '').strip()
    if not email or '@' not in email:
        errors.append("Valid email address is required")
    
    if not form_data.get('dob', '').strip():
        errors.append("Date of birth is required")
    
    return errors

def format_study_time(minutes):
    """Format study time in human-readable format"""
    if minutes < 60:
        return f"{minutes} minutes"
    elif minutes < 1440:  # Less than 24 hours
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
    else:
        days = minutes // 1440
        hours = (minutes % 1440) // 60
        return f"{days}d {hours}h" if hours > 0 else f"{days}d"

if __name__ == "__main__":
    # Run utility functions if needed
    create_tables_if_not_exist()
    print("✅ Utility functions checked and database updated if needed")
