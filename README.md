# 🚀 Personalized Physics Tutor

A comprehensive web-based AI-powered Physics learning platform designed specifically for Class 10 CBSE students. This interactive tutor provides personalized learning experiences, quizzes, study plans, and real-time doubt solving capabilities.

## ✨ Features

### 📚 Core Features
- **Personalized Learning**: Adaptive content based on student performance
- **Interactive Quizzes**: Topic-wise assessments with detailed explanations
- **AI-Powered Chat**: Real-time doubt solving with context-aware responses
- **Study Plans**: Customized study schedules with performance tracking
- **Performance Analytics**: Detailed progress tracking and focus areas
- **Smart RAG System**: Retrieval Augmented Generation for accurate responses

### 🎯 Subject Coverage
Class 10 Physics (CBSE):
- Light - Reflection and Refraction
- The Human Eye and the Colourful World
- Electricity
- Magnetic Effects of Electric Current

## 🛠️ Technical Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite3
- **AI Integration**: Google's Gemini AI
- **Authentication**: Session-based

### Frontend
- **Template Engine**: Jinja2
- **Styling**: Custom CSS with responsive design
- **Interactivity**: JavaScript
- **UI Components**: Bootstrap with custom components

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── gemini_utils.py        # Gemini AI integration utilities
├── rag_utils.py          # RAG system implementation
├── requirements.txt       # Python dependencies
├── students.db           # SQLite database
├── utils.py             # Helper utilities
│
├── data/
│   ├── progress.json           # Student progress data
│   ├── quiz_questions.json     # Quiz question bank
│   ├── rag_knowledge_base.json # RAG system knowledge base
│   └── student_responses.json  # Student interaction data
│
├── static/
│   ├── css/
│   │   ├── chatbot.css
│   │   ├── study_plan.css
│   │   └── style.css
│   ├── images/
│   │   └── logo.png
│   └── js/
│       ├── chatbot.js
│       ├── performance_analytics.js
│       ├── progress.js
│       ├── quick_formulas.js
│       ├── quiz_results.js
│       ├── reminder.js
│       ├── script.js
│       └── study_plan_actions.js
│
└── templates/
    ├── base.html
    ├── chatbot.html
    ├── dashboard.html
    ├── index.html
    ├── login.html
    ├── quiz_active.html
    ├── quiz_results.html
    ├── quiz_start.html
    ├── register.html
    ├── settings.html
    └── study_plan.html
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Gemini API Key (for AI features)
- Modern web browser

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd personalized-physics-tutor
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\\Scripts\\activate   # For Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file with:
GEMINI_API_KEY=your_api_key_here
```

5. Initialize the database:
```bash
python app.py
```

6. Run the application:
```bash
flask run
```

Visit `http://localhost:5000` in your browser.

## 🔧 Configuration

- **Database**: SQLite configuration in `app.py`
- **AI Settings**: Gemini AI parameters in `gemini_utils.py`
- **RAG System**: Knowledge base configuration in `rag_utils.py`

## 🌟 Features in Detail

### 1. User Authentication
- Registration with email and DOB
- Session-based authentication
- User profile management

### 2. Interactive Learning
- AI-powered chatbot for doubts
- Real-time quiz generation
- Performance-based difficulty adjustment

### 3. Study Planning
- Customized study schedules
- Topic-wise learning paths
- Progress tracking

### 4. Performance Analytics
- Chapter-wise performance tracking
- Streak monitoring
- Focus area recommendations

### 5. RAG System
- Context-aware responses
- NCERT-aligned knowledge base
- Dynamic content generation

## 📝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- CBSE Physics curriculum
- Google's Gemini AI platform
- Open-source community

## � Support

For support, email [skshivam771@gmail.com] or raise an issue in the repository.