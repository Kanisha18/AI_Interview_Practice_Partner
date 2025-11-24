from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json
import uuid

Base = declarative_base()

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    role = Column(String, nullable=False)
    status = Column(String, default="active")
    persona = Column(String, default="neutral")
    current_question_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # JSON fields stored as text
    _conversation_history = Column("conversation_history", Text, default="[]")
    _scores = Column("scores", Text, nullable=True)
    _feedback = Column("feedback", Text, nullable=True)
    _persona_history = Column("persona_history", Text, default="[]")
    _asked_questions = Column("asked_questions", Text, default="[]")
    
    # Python properties for easy access
    @property
    def conversation_history(self):
        return json.loads(self._conversation_history) if self._conversation_history else []
    
    @conversation_history.setter
    def conversation_history(self, value):
        self._conversation_history = json.dumps(value) if value else "[]"
    
    @property
    def scores(self):
        return json.loads(self._scores) if self._scores else {}
    
    @scores.setter
    def scores(self, value):
        self._scores = json.dumps(value) if value else None
    
    @property
    def feedback(self):
        return json.loads(self._feedback) if self._feedback else {}
    
    @feedback.setter
    def feedback(self, value):
        self._feedback = json.dumps(value) if value else None
    
    @property
    def persona_history(self):
        return json.loads(self._persona_history) if self._persona_history else []
    
    @persona_history.setter
    def persona_history(self, value):
        self._persona_history = json.dumps(value) if value else "[]"
    
    @property
    def asked_questions(self):
        return json.loads(self._asked_questions) if self._asked_questions else []
    
    @asked_questions.setter
    def asked_questions(self, value):
        self._asked_questions = json.dumps(value) if value else "[]"
