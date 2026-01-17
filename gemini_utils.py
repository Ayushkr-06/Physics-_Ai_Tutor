import os
from google import genai
from dotenv import load_dotenv
import json
import random
import re

# Safety check for RAG utils
try:
    from rag_utils import RAGKnowledgeBase
except ImportError:
    print("⚠️ Warning: rag_utils.py not found. Using dummy RAG system.")
    class RAGKnowledgeBase:
        def get_context_for_query(self, query): return ""

load_dotenv()

class GeminiAI:
    def __init__(self):
        """Initialize Gemini AI with API key and RAG system"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("⚠️ Warning: GEMINI_API_KEY not found in environment variables")
        
        # Initialize the new Client (replaces genai.configure)
        try:
            self.client = genai.Client(api_key=api_key)
            print("🛑 DEBUG CHECK: I am reading the NEW code!")
            self.model_name = 'gemini-2.5-flash'
            print(f"✅ Gemini Client connected using {self.model_name}")
        except Exception as e:
            print(f"❌ Gemini Connection failed: {e}")
            self.client = None
        
        # Initialize RAG system
        try:
            self.rag = RAGKnowledgeBase()
            print("✅ RAG Knowledge Base initialized for Class 10 Physics")
        except Exception as e:
            print(f"⚠️ RAG initialization error: {e}")
            self.rag = None

        # Visual Instruction for diagrams (Must be inside quotes!)
        self.visual_instruction = (
            "If a physics concept can be visually represented (e.g., ray diagrams, circuit diagrams, magnetic field lines), "
            "insert a tag in the format '' at the relevant spot. "
            "Example: [Image of ray diagram for concave mirror object at C]. "
            "Do not use markdown images, just this text tag."
        )
    
    def _safe_call(self, prompt):
        """Safe wrapper for Gemini API calls using the new SDK"""
        if not self.client:
            raise ValueError("Gemini Client not initialized")
            
        try:
            # New generate syntax for google-genai library
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f'[Gemini-ERROR] {e}')
            raise
    
    def _format_response_with_markdown(self, text: str) -> str:
        """Format physics content with proper HTML structure and styling"""
        if not text: return ""

        # Physics emoji mapping
        emoji_map = {
            'light': '💡', 'mirror': '🪞', 'lens': '🔍', 'reflection': '✨',
            'refraction': '🌈', 'electricity': '⚡', 'current': '🔌',
            'magnetic': '🧲', 'energy': '⚡', 'power': '💪', 'work': '⚙️',
            'force': '💥', 'motion': '🏃', 'velocity': '🚀', 'acceleration': '📈',
            'voltage': '⚡', 'resistance': '🔒', 'circuit': '🔌', 'conductor': '📡',
            'insulator': '🛡️', 'electromagnet': '🧲', 'generator': '⚡'
        }
        
        # Convert markdown to structured HTML
        html_content = text
        
        # Format headers
        html_content = re.sub(r'### (.*)', r'<h3>\1</h3>', html_content)
        html_content = re.sub(r'## (.*)', r'<h2>\1</h2>', html_content)
        html_content = re.sub(r'# (.*)', r'<h1>\1</h1>', html_content)
        
        # Format bold and italic
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
        
        # Convert bullet points to structured lists
        bullet_pattern = r'(?:^|\n)[ ]*[-*][ ]+(.*?)(?=\n|$)'
        if re.search(bullet_pattern, html_content, re.MULTILINE):
            # Find all bullet point sections
            sections = re.split(r'\n\n+', html_content)
            formatted_sections = []
            
            for section in sections:
                if re.search(bullet_pattern, section, re.MULTILINE):
                    # This section contains bullet points
                    bullets = re.findall(bullet_pattern, section, re.MULTILINE)
                    bullet_list = '\n'.join([f'<li>{item}</li>' for item in bullets])
                    formatted_sections.append(f'<ul class="concept-list">\n{bullet_list}\n</ul>')
                else:
                    formatted_sections.append(section)
            
            html_content = '\n\n'.join(formatted_sections)
        
        # Format paragraphs
        paragraphs = html_content.split('\n\n')
        formatted_paragraphs = []
        for p in paragraphs:
            if not p.strip():
                continue
            if not (p.startswith('<h') or p.startswith('<ul') or p.startswith('<div')):
                formatted_paragraphs.append(f'<p>{p}</p>')
            else:
                formatted_paragraphs.append(p)
        html_content = '\n'.join(formatted_paragraphs)
        
        # Add emojis for physics terms
        for term, emoji in emoji_map.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            html_content = re.sub(pattern, f'<span class="physics-emoji">{emoji}</span> {term}', html_content, flags=re.IGNORECASE)
        
        # Format formulas
        formula_pattern = r'([A-Z])\s*=\s*([^,\n<]+)'
        html_content = re.sub(formula_pattern, r'<code>\1 = \2</code>', html_content)
        
        # Wrap important notes
        if "Note:" in html_content:
            html_content = re.sub(r'Note:(.*?)(?=\n\n|$)', r'<div class="important-note">💡 \1</div>', html_content, flags=re.DOTALL)
        
        # Format definitions
        if "Definition:" in html_content:
            html_content = re.sub(r'Definition:(.*?)(?=\n\n|$)', r'<div class="definition-block"><strong>Definition:</strong>\1</div>', html_content, flags=re.DOTALL)
        
        # Format examples
        if "Example:" in html_content:
            html_content = re.sub(r'Example:(.*?)(?=\n\n|$)', r'<div class="example-block"><strong>Example:</strong>\1</div>', html_content, flags=re.DOTALL)
        
        return f'<div class="physics-content">{html_content}</div>'
    
    def generate_quiz_questions(self, subject="Physics", class_level=10, n=10, difficulty='medium', topic=None):
        """Generate RAG-enhanced quiz questions for Class 10 Physics"""
        try:
            # Get relevant context from RAG
            search_query = topic if topic else f"Class {class_level} Physics concepts"
            relevant_context = self.rag.get_context_for_query(search_query) if self.rag else ""
            
            topic_focus = f"Topic focus: {topic}" if topic else "General Class 10 Physics"
            
            prompt = f"""
            Generate exactly {n} multiple choice questions for Class 10 Physics (CBSE curriculum).
            {topic_focus}
            Difficulty level: {difficulty}
            
            Use this knowledge context to create accurate questions:
            {relevant_context}
            
            Return ONLY a valid JSON array with each question having:
            - question: the question text (include proper physics units and symbols)
            - options: array of exactly 4 options with units where applicable
            - correct: index of correct answer (0-3)
            - explanation: brief explanation of the correct answer with formula if applicable
            
            Example format:
            [
                {{
                    "question": "What is the SI unit of electric current?",
                    "options": ["Volt (V)", "Ampere (A)", "Ohm (Ω)", "Watt (W)"],
                    "correct": 1,
                    "explanation": "Ampere (A) is the SI unit of electric current."
                }}
            ]
            
            Focus on:
            - Light reflection, refraction, mirrors, lenses
            - Electric current, voltage, resistance, Ohm's law
            - Magnetic effects, electromagnetic induction
            - Numerical problems with proper units
            """
            
            response_text = self._safe_call(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
                questions = json.loads(json_text)
                
                if isinstance(questions, list) and len(questions) > 0:
                    # Validate and clean questions
                    valid_questions = []
                    for q in questions:
                        if all(key in q for key in ['question', 'options', 'correct']) and len(q['options']) == 4:
                            valid_questions.append(q)
                    
                    if valid_questions:
                        return valid_questions[:n]
            
            return self._fallback_physics_questions(n, topic)
            
        except Exception as e:
            print(f"Error generating RAG-enhanced quiz questions: {e}")
            return self._fallback_physics_questions(n, topic)
    
    def _fallback_physics_questions(self, n, topic=None):
        """Comprehensive fallback Class 10 Physics questions"""
        physics_questions = [
            {
                'question': 'What is the SI unit of electric current?',
                'options': ['Volt (V)', 'Ampere (A)', 'Ohm (Ω)', 'Watt (W)'],
                'correct': 1,
                'explanation': 'Ampere (A) is the SI unit of electric current, representing 1 coulomb of charge per second.'
            },
            {
                'question': 'Which type of mirror is used in car headlights?',
                'options': ['Plane mirror', 'Concave mirror', 'Convex mirror', 'Cylindrical mirror'],
                'correct': 1,
                'explanation': 'Concave mirrors are used in headlights as they produce parallel beams of light when the bulb is at the focus.'
            },
            {
                'question': 'What is the power of a lens having focal length of 50 cm?',
                'options': ['+2 D', '-2 D', '+0.5 D', '+5 D'],
                'correct': 0,
                'explanation': 'Power P = 1/f (in meters) = 1/0.5 = +2 D. Convex lens has positive power.'
            },
            {
                'question': 'According to Ohm\'s law, if voltage doubles and resistance remains constant, current will:',
                'options': ['Remain same', 'Double', 'Become half', 'Become four times'],
                'correct': 1,
                'explanation': 'From V = IR, if V doubles and R is constant, then I also doubles to maintain the relationship.'
            },
            {
                'question': 'The phenomenon of electromagnetic induction was discovered by:',
                'options': ['Newton', 'Faraday', 'Ohm', 'Ampere'],
                'correct': 1,
                'explanation': 'Michael Faraday discovered electromagnetic induction in 1831.'
            },
            {
                'question': 'In series combination of resistors, which quantity remains same?',
                'options': ['Voltage', 'Current', 'Resistance', 'Power'],
                'correct': 1,
                'explanation': 'In series combination, current remains same through all resistors as there is only one path.'
            },
            {
                'question': 'The angle of incidence is equal to angle of reflection. This is:',
                'options': ['First law of reflection', 'Second law of reflection', 'Snell\'s law', 'Lens formula'],
                'correct': 1,
                'explanation': 'The second law of reflection states that angle of incidence equals angle of reflection.'
            },
            {
                'question': 'What happens to the resistance of a conductor when temperature increases?',
                'options': ['Increases', 'Decreases', 'Remains same', 'Becomes zero'],
                'correct': 0,
                'explanation': 'For metallic conductors, resistance increases with increase in temperature due to increased atomic vibrations.'
            },
            {
                'question': 'The refractive index of water is 1.33. This means light in water travels at:',
                'options': ['Same speed as in air', '1.33 times faster than in air', '1.33 times slower than in air', 'Infinite speed'],
                'correct': 2,
                'explanation': 'Refractive index n = c/v, where c is speed in vacuum and v is speed in medium. Higher n means slower speed.'
            },
            {
                'question': 'Electric power consumed by a device is measured in:',
                'options': ['Volt', 'Ampere', 'Watt', 'Ohm'],
                'correct': 2,
                'explanation': 'Power is measured in Watts (W). Power P = VI = I²R = V²/R.'
            }
        ]
        
        # Select questions based on topic if specified
        if topic:
            filtered_questions = []
            topic_lower = topic.lower()
            for q in physics_questions:
                if any(keyword in q['question'].lower() or keyword in q['explanation'].lower() 
                       for keyword in topic_lower.split()):
                    filtered_questions.append(q)
            if filtered_questions:
                physics_questions = filtered_questions
        
        # Repeat and modify questions to reach desired count
        questions = []
        for i in range(n):
            q = physics_questions[i % len(physics_questions)].copy()
            if i >= len(physics_questions):
                q['question'] = f"[Q{i+1}] " + q['question']
            questions.append(q)
        
        return questions
    
    def generate_study_plan(self, class_level=10, subjects=['Physics'], learning_goal='', performance_data=None, language='English', duration='month'):
        """Generate a personalized study plan based on performance and duration"""
        try:
            # Get specific chapter context if it's a single chapter
            is_chapter_plan = duration == 'week' and len(subjects) == 1
            chapter = subjects[0] if is_chapter_plan else None
            
            # Get relevant context
            if self.rag:
                if is_chapter_plan:
                    context = self.rag.get_context_for_query(f"Class 10 Physics {chapter} chapter concepts formulas")
                else:
                    context = self.rag.get_context_for_query("Class 10 Physics chapters syllabus")
            else:
                context = ""
            
            # Format performance data
            performance_summary = """
## 📊 **Current Performance Analysis**

Below is your recent quiz performance and focus areas:

### 📈 **Quiz Performance by Chapter**
"""
            total_score = 0
            total_chapters = 0
            weak_chapters = []
            strong_chapters = []
            
            if performance_data:
                for subject, avg_score, attempts, last_attempt in performance_data:
                    total_score += avg_score
                    total_chapters += 1
                    
                    if avg_score >= 80:
                        status = "🌟 Excellent"
                        strong_chapters.append(subject)
                    elif avg_score >= 60:
                        status = "💪 Good"
                    else:
                        status = "🎯 Needs Improvement"
                        weak_chapters.append(subject)
                        
                    # Format the performance line with an emoji based on score
                    if avg_score >= 80:
                        emoji = "🌟"
                    elif avg_score >= 60:
                        emoji = "💪"
                    else:
                        emoji = "📝"
                    performance_summary += f"\n- {emoji} **{subject}:** {avg_score:.1f}% ({status}) - *{attempts} attempts*"
                
                # Calculate overall performance
                avg_overall = total_score / total_chapters if total_chapters > 0 else 0
                
                performance_summary += """

### 📋 **Performance Summary**
"""
                performance_summary += f"\n- 📊 **Overall Performance:** {avg_overall:.1f}%"
                if weak_chapters:
                    performance_summary += f"\n- ⚠️ **Areas Needing Focus:** {', '.join(weak_chapters)}"
                if strong_chapters:
                    performance_summary += f"\n- ✨ **Strong Areas:** {', '.join(strong_chapters)}"
                
                # Add study tips based on performance
                performance_summary += """

### 💡 **Personalized Study Tips**
"""
                if avg_overall >= 80:
                    performance_summary += """
- 🎯 Focus on maintaining your excellent performance
- 🧠 Challenge yourself with advanced problems
- 🌟 Help classmates and explain concepts to reinforce learning"""
                elif avg_overall >= 60:
                    performance_summary += """
- 📝 Review weak topics more frequently
- ✍️ Practice more numerical problems
- 🔄 Take regular revision quizzes"""
                else:
                    performance_summary += """
- 📖 Start with basic concepts and fundamentals
- 🎯 Focus on one topic at a time
- ✍️ Take detailed notes and practice daily
- 🤝 Consider joining study groups"""
                
            else:
                performance_summary += """
- 📝 No quiz performance data yet - Ready to start fresh!

### 💪 **Getting Started Tips**
- 📚 Begin with the fundamentals of each chapter
- 🎯 Take regular quizzes to track your progress
- ✍️ Practice solving example problems daily
- 🌟 Focus on understanding concepts before memorizing formulas
"""
            
            prompt = f"""
            Create a focused study plan for a Class 10 Physics student (CBSE).
            
            **Student Profile:**
            - Class: {class_level} CBSE
            - Subject: {'Single Chapter: ' + chapter if chapter else 'Complete Physics'}
            - Learning Goal: {learning_goal}
            - Language: {language}
            - Duration: {'7 days (Chapter focus)' if duration == 'week' else '1 month (Full syllabus)'}
            
            {performance_summary}
            
            **Curriculum Context:**
            {context[:600]}
            
            Create a comprehensive study plan with this structure:
            
            {'# 🚀 ' + chapter if chapter else '# 🚀 Physics Master Plan'}
            
            *{'Master this chapter with our focused study plan!' if chapter else 'Transform your physics understanding with this structured schedule!'}*
            
            ## 📅 Study Schedule
            
            {'### Day 1: Core Concepts' if chapter else '### Week 1: Foundation Building'}
            - Learning Goals
            - Key Topics
            - Practice Focus
            - Self Assessment
            
            {'### Day 2-3: Deep Understanding' if chapter else '### Week 2: Skill Development'}
            [Continue with daily/weekly breakdown]
            
            ## 📈 Learning Objectives
            - Clear, achievable goals
            - Key formulas to master
            - Problem-solving skills
            
            ## 🧪 Practice Strategy
            - Structured approach
            - Focus areas
            - Example problems
            
            ## 📝 Assessment Plan
            - Progress tracking
            - Self-evaluation
            
            ## 💡 Study Tips
            - Specific to the content
            - Memory techniques
            - Common pitfalls to avoid
            
            Use minimal emojis, clear headings, proper physics terminology, and professional language.
            Include NCERT references and essential formulas.
            Make it structured and achievable.
            Response in {language}.
            """
            
            response = self._safe_call(prompt)
            return self._format_response_with_markdown(response)
            
        except Exception as e:
            print(f"Error generating study plan: {e}")
            return self._generate_fallback_study_plan()
    
    def _generate_fallback_study_plan(self):
        """Enhanced fallback study plan for Class 10 Physics"""
        return """
# 🚀 **7-Day Class 10 Physics Mastery Plan**

*Master the fundamental concepts that govern our universe!*

## 📅 **Daily Study Schedule**

### **Day 1: 💡 Light - Reflection & Mirrors**
- **🎯 Focus**: Understanding light behavior and mirror concepts
- **📖 Topics**: 
  - Laws of reflection
  - Plane mirrors and image formation
  - Spherical mirrors (concave & convex)
  - Mirror formula: 1/v + 1/u = 1/f
- **🧮 Practice**: Solve 8-10 numerical problems on mirrors
- **🎬 Resources**: Search "Class 10 Physics Light Reflection NCERT" on YouTube
- **⏰ Time**: 60-75 minutes
- **✅ Goal**: Master mirror formula applications

### **Day 2: 🌈 Refraction & Lenses**
- **🎯 Focus**: Light bending and lens behavior
- **📖 Topics**:
  - Laws of refraction and Snell's law
  - Refractive index concepts
  - Convex and concave lenses
  - Lens formula: 1/v - 1/u = 1/f
- **🧮 Practice**: Lens power calculations and image formation
- **🎬 Resources**: "Class 10 Physics Refraction Lenses"
- **⏰ Time**: 60-75 minutes
- **✅ Goal**: Understand lens applications

### **Day 3: ⚡ Electricity Basics**
- **🎯 Focus**: Electric current and potential difference
- **📖 Topics**:
  - Electric current and conventional flow
  - Potential difference and voltage
  - Ohm's Law: V = I × R
  - Factors affecting resistance
- **🧮 Practice**: Current, voltage, resistance calculations
- **🎬 Resources**: "Class 10 Physics Electricity Ohm's Law"
- **⏰ Time**: 60-75 minutes
- **✅ Goal**: Apply Ohm's law confidently

### **Day 4: 🔌 Resistors & Circuits**
- **🎯 Focus**: Circuit analysis and combinations
- **📖 Topics**:
  - Series combination: Rs = R₁ + R₂ + R₃
  - Parallel combination: 1/Rp = 1/R₁ + 1/R₂
  - Mixed circuits and problem solving
- **🧮 Practice**: Complex circuit problems
- **🎬 Resources**: "Class 10 Physics Resistor Combinations"
- **⏰ Time**: 60-75 minutes
- **✅ Goal**: Solve any resistor network

### **Day 5: 💪 Electric Power & Energy**
- **🎯 Focus**: Power consumption and energy bills
- **📖 Topics**:
  - Electric power: P = VI = I²R = V²/R
  - Electric energy and commercial units
  - kWh calculations and electricity bills
  - Heating effects of current
- **🧮 Practice**: Power and energy numerical problems
- **🎬 Resources**: "Class 10 Physics Electric Power Energy"
- **⏰ Time**: 60-75 minutes
- **✅ Goal**: Calculate electricity costs

### **Day 6: 🧲 Magnetic Effects**
- **🎯 Focus**: Magnetism and current relationship
- **📖 Topics**:
  - Magnetic field around current-carrying conductors
  - Right-hand thumb rule
  - Magnetic field due to solenoid
  - Force on current-carrying conductor
  - Fleming's left-hand rule
- **🧮 Practice**: Magnetic field direction problems
- **🎬 Resources**: "Class 10 Physics Magnetic Effects Current"
- **⏰ Time**: 60-75 minutes
- **✅ Goal**: Master hand rules

### **Day 7: 📝 Revision & Integration**
- **🎯 Focus**: Complete review and exam preparation
- **📖 Topics**: All covered concepts with formula sheet
- **🧮 Practice**: 
  - Mixed problems from all chapters
  - Sample question paper (3 hours)
  - Previous year questions
- **🎬 Resources**: "Class 10 Physics Complete Revision"
- **⏰ Time**: 90-120 minutes
- **✅ Goal**: Exam readiness achieved

## 📈 **Weekly Learning Objectives**
1. **🎯** Master all fundamental physics formulas
2. **🧮** Solve 50+ numerical problems confidently  
3. **📝** Complete detailed chapter notes
4. **🎬** Watch 10+ educational physics videos
5. **🧪** Understand real-world physics applications

## 🧪 **Daily Practice Strategy**
- **Morning**: Theory reading (20 mins)
- **Afternoon**: Problem solving (30 mins)
- **Evening**: Video watching (15 mins)
- **Night**: Quick revision (10 mins)

## 💡 **Physics Mastery Tips**
- **📊** Draw diagrams for every concept
- **🔢** Practice numerical problems daily
- **🎯** Focus on NCERT examples first
- **💭** Connect physics to daily life
- **🤔** Ask "why" for every formula

## 📝 **Assessment Checkpoints**
- **Daily**: 5-question mini quiz
- **Alternate days**: One complete numerical problem
- **Weekend**: Chapter-wise test
- **Final**: Mock exam with time limits

---
**🌟 Remember**: *Physics is not just about memorizing formulas - it's about understanding how our universe works! Every concept you learn brings you closer to becoming a real scientist.* **You've got this!** 💪🚀

**📞 Keep practicing, stay curious, and let physics amaze you every day!** ⚡
        """
    
    def chat(self, message, context=None):
        """Interactive physics chat with context memory"""
        try:
            # Get relevant context from knowledge base
            rag_context = self.rag.get_context_for_query(message) if self.rag else ""
            
            chat_prompt = f"""
            You are a helpful Physics AI Assistant for Class 10 students.
            
            Student Message: {message}
            Student Name: {context.get('name', 'Student') if context else 'Student'}
            
            Previous conversation context:
            {context.get('chat_history', []) if context else []}
            
            Relevant physics knowledge:
            {rag_context}
            
            Respond in a clear, helpful, and engaging way:
            1. If it's a physics concept question, explain with examples and formulas
            2. If it's a problem to solve, show step-by-step solution
            3. If it's a general question, respond naturally and guide towards physics learning
            
            {self.visual_instruction}
            
            Make responses:
            - Clear and accurate
            - Student-friendly
            - Encouraging and motivating
            - With proper physics terminology
            - Using markdown formatting
            """
            
            response = self._safe_call(chat_prompt)
            return self._format_response_with_markdown(response)
            
        except Exception as e:
            print(f"Chat error: {e}")
            return f"""
            💬 I'm having trouble processing that right now.
            
            Could you:
            1. Rephrase your question, or
            2. Try asking about a specific physics topic?
            
            I'm here to help with:
            - 💡 Physics concepts
            - 📝 Problem solving
            - 🔬 Experiments and applications
            - 📚 Study guidance
            
            Let's try again! 🚀
            """

    def solve_doubt(self, question, class_level=10, language='English', subjects=['Physics']):
        """Solve physics doubts with RAG-enhanced explanations"""
        try:
            # Get relevant context from knowledge base
            relevant_context = self.rag.get_context_for_query(question) if self.rag else ""
            
            prompt = f"""
            You are an expert Class 10 Physics tutor helping Indian CBSE students.
            
            **Student's Question:** {question}
            **Class Level:** {class_level}
            **Subject Focus:** Physics
            
            **Relevant Knowledge Context:**
            {relevant_context}
            
            Provide a comprehensive, well-structured explanation:
            
            ## 🤔 **Understanding Your Question**
            - Break down what's being asked clearly
            
            ## 💡 **Key Physics Concepts**
            - Explain relevant physics principles
            - Use proper scientific terminology
            - Include formulas where applicable
            
            ## 📝 **Step-by-Step Solution** (if numerical)
            - Show detailed calculations with units
            - Explain each step clearly
            - Include final answer with proper units
            
            ## 🎯 **Final Answer**
            - Clear, concise conclusion
            - Real-world relevance if applicable
            
            ## 💪 **Quick Study Tip**
            - Memory trick or important concept to remember
            
            ## 📚 **Related Topics**
            - What else to study for deeper understanding
            
            {self.visual_instruction}
            
            Use emojis, **bold text**, proper physics units, and bullet points for clarity.
            Keep explanation under 400 words but comprehensive.
            Be encouraging and make physics exciting!
            Response in {language}.
            """
            
            response = self._safe_call(prompt)
            return self._format_response_with_markdown(response)
            
        except Exception as e:
            print(f"Error solving doubt: {e}")
            return f"""
            ## 🤔 **I'm having trouble answering that right now!**
            
            **Possible reasons:**
            - ❌ Internet connection issues
            - 🔧 Technical problem: {str(e)[:100]}
            
            ## 💡 **Let's try this instead:**
            
            **1. 🔄 Rephrase your question** - Make it more specific
            **2. 📶 Check internet connection** - Ensure stable connection  
            **3. 🎯 Ask about specific topics** - Try these examples:
            
            ### 📚 **Example Questions I Can Help With:**
            - **💡 Light**: "Explain laws of reflection" or "How do concave mirrors work?"
            - **⚡ Electricity**: "What is Ohm's law?" or "How to calculate resistance?"
            - **🧲 Magnetism**: "Right hand thumb rule" or "Electromagnetic induction"
            - **🧮 Numerical**: "Mirror formula problem" or "Power calculation"
            
            ### 🚀 **I'm your Class 10 Physics expert!**
            **Ask me anything about:**
            - Light, mirrors, lenses 💡
            - Electricity, current, circuits ⚡
            - Magnetism and induction 🧲
            - Formulas and numerical problems 🧮
            
            **💪 Don't give up - physics is amazing once you get it!** 🌟
            """
    
    def get_focus_areas(self, quiz_performance, subjects):
        """Analyze quiz performance and suggest physics focus areas"""
        try:
            if not quiz_performance:
                return [
                    "🎯 Take your first Physics quiz to get personalized recommendations!",
                    "💡 Start with Light - Reflection and Refraction chapter",
                    "⚡ Practice basic Electricity concepts and Ohm's law",
                    "🧲 Explore Magnetic Effects of Electric Current"
                ]
            
            focus_areas = []
            for subject, avg_score, quiz_count in quiz_performance:
                if avg_score < 40:
                    focus_areas.append(f"🔴 **{subject}**: Urgent attention needed! (Score: {avg_score:.1f}%) - Review basic concepts daily")
                elif avg_score < 60:
                    focus_areas.append(f"🟡 **{subject}**: Need more practice (Score: {avg_score:.1f}%) - Focus on numerical problems")
                elif avg_score < 80:
                    focus_areas.append(f"🟢 **{subject}**: Good progress! (Score: {avg_score:.1f}%) - Polish advanced topics")
                else:
                    focus_areas.append(f"⭐ **{subject}**: Excellent work! (Score: {avg_score:.1f}%) - Try challenging problems")
            
            # Add specific physics recommendations
            if any(score < 60 for _, score, _ in quiz_performance):
                focus_areas.append("📚 **Recommendation**: Revise NCERT examples and practice more numericals")
            
            return focus_areas[:5]
            
        except Exception as e:
            print(f"Error getting focus areas: {e}")
            return [
                "🎯 Continue regular physics practice across all chapters",
                "💡 Focus on understanding concepts before memorizing formulas",
                "⚡ Practice numerical problems daily",
                "🧲 Connect physics concepts to real-world applications"
            ]
    
    def get_detailed_explanation(self, question, correct_answer, user_answer, subject="Physics", class_level=10, chapter=""):
        """Generate detailed explanation for quiz questions"""
        try:
            # Get relevant context from RAG
            search_query = f"{question} {chapter} physics concept"
            relevant_context = self.rag.get_context_for_query(search_query) if self.rag else ""
            
            prompt = f"""
            Generate a detailed physics explanation for a Class {class_level} student who answered a quiz question.

            **Question:** {question}
            **Correct Answer:** {correct_answer}
            **Student's Answer:** {user_answer}
            **Chapter:** {chapter}
            
            **Relevant Context:**
            {relevant_context}

            Provide a comprehensive explanation with:

            ### 💡 **Core Concept**
            - Explain the fundamental physics principle
            - Define key terms and variables
            - Reference relevant laws/formulas
            
            ### 📝 **Detailed Solution**
            - Step-by-step explanation
            - Why the correct answer is right
            - Why other options are wrong
            - Include formulas and calculations if relevant
            
            ### 🔍 **Common Misconceptions**
            - Address why students might choose wrong answers
            - Clarify confusing aspects
            
            ### 🌟 **Key Takeaways**
            - Important points to remember
            - Tips for similar questions
            - Real-world applications
            
            ### 📚 **Related Topics**
            - Connected concepts to study
            - Suggested practice problems

            {self.visual_instruction}

            Use proper physics terminology, emojis, bold text, and bullet points.
            Make it engaging and educational.
            """
            
            response = self._safe_call(prompt)
            return self._format_response_with_markdown(response)
            
        except Exception as e:
            print(f"Error generating detailed explanation: {e}")
            return f"""
            ### ❌ **Oops! Technical Difficulty**
            
            I'm having trouble generating a detailed explanation right now.
            
            ### 💡 **Quick Explanation:**
            The correct answer is: **{correct_answer}**
            
            ### 🎯 **Study Tips:**
            - Review {chapter} chapter in your NCERT textbook
            - Practice similar problems
            - Ask your teacher for clarification
            
            ### 🚀 **Keep Going!**
            Don't worry! Physics becomes clearer with practice. Keep exploring!
            """

    def get_motivation(self, performance, name, language='English', streak=0, quiz_count=0):
        """Generate physics-specific motivational content"""
        try:
            if performance >= 80:
                performance_level = "outstanding"
                emoji = "🌟"
                tone = "celebrating excellence"
            elif performance >= 60:
                performance_level = "good with room for growth"
                emoji = "💪"
                tone = "encouraging improvement"
            else:
                performance_level = "building strong foundations"
                emoji = "🎯"
                tone = "motivating perseverance"

            # Add streak context
            streak_context = ""
            if streak > 0:
                streak_context = f"with a {streak}-day study streak"
            
            prompt = f"""
            Generate an inspiring, physics-focused motivational message for {name}, a Class 10 student with {performance_level} performance {streak_context}.
            
            The message should be:
            - Physics and science-themed
            - Age-appropriate for 15-16 year olds
            - Include a fascinating physics fact or inspiration
            - Reference famous physicists or discoveries
            - Brief but powerfully motivating (2-3 sentences)
            - Use emojis and exciting language
            - Tone: {tone}
            {f'- Acknowledge their {streak}-day study streak' if streak > 0 else ''}
            {f'- Mention their quiz progress ({quiz_count} quizzes taken)' if quiz_count > 0 else ''}
            
            Response in {language}.
            """
            
            response = self._safe_call(prompt)
            return f"{emoji} " + self._format_response_with_markdown(response)
            
        except Exception as e:
            physics_quotes = [
                f"🌟 **Fantastic work, {name}!** Just like light travels at 3×10⁸ m/s, your physics knowledge is expanding at incredible speed! Keep exploring the universe! 🚀💡",
                f"⚡ **{name}, you're electrifying!** Remember, Einstein once said imagination is more important than knowledge. Your curiosity today shapes tomorrow's discoveries! 🧠🌌",
                f"🚀 **Keep it up, {name}!** From Newton's apple 🍎 to Einstein's relativity, every great physicist started with questions just like yours. You're on the path to greatness! 🎯",
                f"💪 **{name}, stay charged up!** Just like energy can neither be created nor destroyed, your effort in learning physics will always transform into success! ⚡📈",
                f"🎯 **Focus mode activated, {name}!** Every formula you master is like unlocking a secret of the universe. From Ohm's law to electromagnetic induction - you're becoming a real scientist! 🧪🔬",
                f"🌟 **Brilliant work, {name}!** Physics is everywhere - in your smartphone 📱, the sunset 🌅, and even in your heartbeat ❤️. You're learning to decode the language of nature! 🌍"
            ]
            return random.choice(physics_quotes)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🛠️  TESTING GEMINI UTILS INITIALIZATION")
    print("="*50)
    
    try:
        ai = GeminiAI()
        if ai.client:
            print("\n✅ SUCCESS: Connected to Gemini 2.0 Flash!")
            print("🚀 The API key is working and the new library is installed.")
        else:
            print("\n❌ FAILURE: Could not connect to Gemini.")
            print("👉 Check if GEMINI_API_KEY is correct in your .env file.")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        
    print("="*50 + "\n")