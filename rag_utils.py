import json
import os
from typing import List, Dict, Any
import re
from difflib import SequenceMatcher

class RAGKnowledgeBase:
    def __init__(self, knowledge_base_path: str = "data/rag_knowledge_base.json"):
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_chunks = []
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load physics knowledge base from JSON file"""
        try:
            if os.path.exists(self.knowledge_base_path):
                with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.knowledge_chunks = data
                    else:
                        self.knowledge_chunks = data.get('chunks', [])
                print(f"✅ Loaded {len(self.knowledge_chunks)} physics knowledge chunks")
            else:
                print(f"❌ Knowledge base file not found: {self.knowledge_base_path}")
                self._create_sample_knowledge_base()
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            self._create_sample_knowledge_base()
    
    def _create_sample_knowledge_base(self):
        """Create comprehensive Class 10 Physics knowledge base"""
        sample_chunks = [
            {
                "chunk": "Light is a form of energy which enables us to see objects. We see objects when light emitted or reflected by them reaches our eyes. Light travels in straight lines. This can be observed from the fact that a small source of light casts sharp shadows of opaque objects. The straight-line path of light is called a ray of light.",
                "subtopic": "Nature of Light",
                "chapter": "Light - Reflection and Refraction"
            },
            {
                "chunk": "When light falls on a surface, it can be reflected, absorbed, or transmitted. The phenomenon of bouncing back of light rays from a surface is called reflection. Laws of reflection: (1) The incident ray, reflected ray and normal all lie in the same plane. (2) The angle of incidence is equal to the angle of reflection (∠i = ∠r).",
                "subtopic": "Reflection of Light",
                "chapter": "Light - Reflection and Refraction"
            },
            {
                "chunk": "A spherical mirror is a mirror whose reflecting surface is part of a sphere. There are two types: Concave mirror (converging mirror) - curves inward, can form real and virtual images. Convex mirror (diverging mirror) - curves outward, always forms virtual, diminished images. The focal length f = R/2, where R is radius of curvature.",
                "subtopic": "Spherical Mirrors",
                "chapter": "Light - Reflection and Refraction"
            },
            {
                "chunk": "Mirror formula: 1/v + 1/u = 1/f, where v = image distance, u = object distance, f = focal length. Magnification m = -v/u = height of image/height of object. For concave mirrors, focal length is positive; for convex mirrors, focal length is negative.",
                "subtopic": "Mirror Formula",
                "chapter": "Light - Reflection and Refraction"
            },
            {
                "chunk": "Refraction is the bending of light when it travels from one transparent medium to another. This happens due to change in speed of light in different media. Laws of refraction: (1) Incident ray, refracted ray and normal lie in the same plane. (2) Snell's law: n₁sin(θ₁) = n₂sin(θ₂), where n is refractive index.",
                "subtopic": "Refraction of Light",
                "chapter": "Light - Reflection and Refraction"
            },
            {
                "chunk": "A lens is a transparent object with at least one curved surface that can converge or diverge light rays. Convex lens (converging lens) - thicker at center, focal length positive, can form real and virtual images. Concave lens (diverging lens) - thinner at center, focal length negative, always forms virtual images.",
                "subtopic": "Lenses",
                "chapter": "Light - Reflection and Refraction"
            },
            {
                "chunk": "Lens formula: 1/v - 1/u = 1/f. Power of lens P = 1/f (in meters), measured in diopters (D). For combination of lenses: P = P₁ + P₂ + ... The human eye works like a camera with a convex lens (crystalline lens) forming real, inverted images on retina.",
                "subtopic": "Lens Formula and Human Eye",
                "chapter": "Light - Reflection and Refraction"
            },
            {
                "chunk": "Electric current is the flow of electric charge through a conductor. SI unit is ampere (A). One ampere = 1 coulomb/second. Current flows from positive terminal to negative terminal (conventional current direction). In metals, current is due to flow of free electrons (opposite to conventional current).",
                "subtopic": "Electric Current",
                "chapter": "Electricity"
            },
            {
                "chunk": "Electric potential difference (voltage) is the work done per unit charge to move charge between two points. V = W/Q. SI unit is volt (V). One volt = 1 joule/coulomb. Potential difference drives current through a circuit. Higher voltage means more energy per unit charge.",
                "subtopic": "Electric Potential",
                "chapter": "Electricity"
            },
            {
                "chunk": "Ohm's Law states that current through a conductor is directly proportional to potential difference across it, provided temperature remains constant. V = I × R, where V = voltage, I = current, R = resistance. Resistance opposes flow of current. SI unit of resistance is ohm (Ω).",
                "subtopic": "Ohm's Law",
                "chapter": "Electricity"
            },
            {
                "chunk": "Factors affecting resistance: (1) Length - R ∝ l (2) Area of cross-section - R ∝ 1/A (3) Material - depends on resistivity ρ (4) Temperature - for conductors, R increases with temperature. Formula: R = ρl/A. Resistivity is a material property.",
                "subtopic": "Resistance",
                "chapter": "Electricity"
            },
            {
                "chunk": "Series combination: Resistances add up, Rs = R₁ + R₂ + R₃... Current same through all resistors. Parallel combination: 1/Rp = 1/R₁ + 1/R₂ + 1/R₃... Voltage same across all resistors. Parallel combination gives less total resistance than individual resistances.",
                "subtopic": "Resistor Combinations",
                "chapter": "Electricity"
            },
            {
                "chunk": "Electric power is the rate of consumption of electric energy. P = VI = I²R = V²/R. SI unit is watt (W). Electric energy consumed = P × t = VIt. Commercial unit of energy is kilowatt-hour (kWh). 1 kWh = 3.6 × 10⁶ J. Electric bill is based on energy consumed.",
                "subtopic": "Electric Power",
                "chapter": "Electricity"
            },
            {
                "chunk": "A magnetic field exists around a magnet and current-carrying conductor. Magnetic field lines are imaginary lines showing direction of magnetic field. They emerge from North pole and enter South pole. Field lines never intersect. Uniform field has parallel, equally spaced lines.",
                "subtopic": "Magnetic Field",
                "chapter": "Magnetic Effects of Electric Current"
            },
            {
                "chunk": "Current-carrying conductor produces magnetic field. Direction given by Right Hand Thumb Rule: Thumb shows current direction, fingers curl in direction of magnetic field. For circular loop: field lines are circular near wire, straight at center. For solenoid: behaves like bar magnet.",
                "subtopic": "Magnetic Field due to Current",
                "chapter": "Magnetic Effects of Electric Current"
            },
            {
                "chunk": "Force on current-carrying conductor in magnetic field: F = BIl sin θ, where B = magnetic field, I = current, l = length, θ = angle. Direction by Fleming's Left Hand Rule: Thumb = Force, Index finger = Field, Middle finger = Current. Used in electric motors.",
                "subtopic": "Force on Current-carrying Conductor",
                "chapter": "Magnetic Effects of Electric Current"
            },
            {
                "chunk": "Electromagnetic induction: When magnetic flux through a conductor changes, EMF is induced. Faraday's laws: (1) Changing magnetic flux induces EMF. (2) Induced EMF = -dΦ/dt. Fleming's Right Hand Rule gives direction of induced current. Used in generators, transformers.",
                "subtopic": "Electromagnetic Induction",
                "chapter": "Magnetic Effects of Electric Current"
            }
        ]
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.knowledge_base_path), exist_ok=True)
        
        # Save comprehensive physics data
        with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
            json.dump(sample_chunks, f, indent=2, ensure_ascii=False)
        
        self.knowledge_chunks = sample_chunks
        print(f"✅ Created comprehensive physics knowledge base with {len(sample_chunks)} chunks")
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def search_relevant_chunks(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant knowledge chunks based on query"""
        if not self.knowledge_chunks:
            return []
        
        scored_chunks = []
        query_lower = query.lower()
        
        for chunk in self.knowledge_chunks:
            chunk_text = chunk.get('chunk', '').lower()
            subtopic = chunk.get('subtopic', '').lower()
            chapter = chunk.get('chapter', '').lower()
            
            # Calculate relevance scores
            content_score = self.similarity_score(query_lower, chunk_text)
            subtopic_score = self.similarity_score(query_lower, subtopic) * 1.5
            chapter_score = self.similarity_score(query_lower, chapter) * 1.2
            
            # Keyword matching bonus
            keywords = re.findall(r'\b\w+\b', query_lower)
            keyword_score = 0
            for keyword in keywords:
                if keyword in chunk_text or keyword in subtopic or keyword in chapter:
                    keyword_score += 0.3
            
            total_score = content_score + subtopic_score + chapter_score + min(keyword_score, 1.0)
            
            if total_score > 0.1:
                scored_chunks.append({
                    'chunk': chunk,
                    'score': total_score
                })
        
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        return [item['chunk'] for item in scored_chunks[:top_k]]
    
    def get_context_for_query(self, query: str, max_context_length: int = 1200) -> str:
        """Get relevant context for a query"""
        relevant_chunks = self.search_relevant_chunks(query, top_k=3)
        
        if not relevant_chunks:
            return "Physics concepts from Class 10 curriculum."
        
        context_parts = []
        current_length = 0
        
        for chunk in relevant_chunks:
            chunk_text = chunk.get('chunk', '')
            subtopic = chunk.get('subtopic', '')
            chapter = chunk.get('chapter', '')
            
            formatted_chunk = f"📚 **{chapter}** - {subtopic}:\n{chunk_text}\n"
            
            if current_length + len(formatted_chunk) <= max_context_length:
                context_parts.append(formatted_chunk)
                current_length += len(formatted_chunk)
            else:
                break
        
        return "\n".join(context_parts)
    
    def get_chapter_topics(self, chapter: str = None) -> List[str]:
        """Get all subtopics for a chapter or all topics"""
        if not chapter:
            return list(set([chunk.get('subtopic', '') for chunk in self.knowledge_chunks if chunk.get('subtopic')]))
        
        topics = []
        for chunk in self.knowledge_chunks:
            if chapter.lower() in chunk.get('chapter', '').lower():
                topic = chunk.get('subtopic', '')
                if topic and topic not in topics:
                    topics.append(topic)
        return topics
