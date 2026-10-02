import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Preformatted
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "SET — Conversational RAG with Memory Architecture Blueprint")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.drawString(54, 36, "Confidential & Proprietary — Smart Expense Tracker (SET)")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()

def create_rag_blueprint_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    c_primary = colors.HexColor("#4F46E5")   # Indigo
    c_dark = colors.HexColor("#0F172A")      # Slate 900
    c_body = colors.HexColor("#334155")      # Slate 700
    c_accent = colors.HexColor("#10B981")    # Emerald
    c_code_bg = colors.HexColor("#F8FAFC")   # Light gray
    c_card_bg = colors.HexColor("#EEF2FF")   # Indigo tint

    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_dark,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Header1',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_dark,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_body,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_body,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=0
    )

    story = []

    # Title block
    story.append(Paragraph("⚡ Conversational RAG with Memory Architecture", title_style))
    story.append(Paragraph("Complete Technical Blueprint, Architecture Diagram & Python Implementation Guide for Smart Expense Tracker", subtitle_style))

    # Overview Callout
    overview_text = (
        "<b>Executive Summary:</b> This blueprint details how to build a 100% Free, Local <b>Retrieval-Augmented Generation (RAG) system with Short-Term Conversational Memory</b> for financial expense tracking. "
        "It combines <i>Local Vector Similarity Search</i> for semantic transactions with <i>SQL Aggregation</i> for exact mathematical precision and <i>Session Memory</i> for seamless multi-turn conversations."
    )
    t_overview = Table([[Paragraph(overview_text, body_style)]], colWidths=[504])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#C7D2FE")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 10))

    # Architecture Diagram Table
    story.append(Paragraph("1. System Architecture Blueprint", h1_style))
    
    arch_data = [
        [Paragraph("<b>Step / Layer</b>", h2_style), Paragraph("<b>Component & Responsibility</b>", h2_style), Paragraph("<b>Tech Used</b>", h2_style)],
        [Paragraph("<b>1. Input & Session</b>", body_style), Paragraph("User query via Voice Mic / Chat with active session ID.", body_style), Paragraph("Web Speech / JS", body_style)],
        [Paragraph("<b>2. Memory Buffer</b>", body_style), Paragraph("Tracks last 6-8 conversation turns to resolve pronouns ('it', 'those').", body_style), Paragraph("Django Session / Dict", body_style)],
        [Paragraph("<b>3. Query Rewriter</b>", body_style), Paragraph("Reformulates follow-up questions into standalone search prompts.", body_style), Paragraph("Rule / Gemini Flash", body_style)],
        [Paragraph("<b>4. Hybrid Retriever</b>", body_style), Paragraph("Semantic Vector Search (Top-K) + SQL Aggregation (Sum/Count/Avg).", body_style), Paragraph("TF-IDF / Dense + Postgres", body_style)],
        [Paragraph("<b>5. Context Synthesizer</b>", body_style), Paragraph("Grounded prompt formulation with strict financial context.", body_style), Paragraph("Python Engine", body_style)],
        [Paragraph("<b>6. Dual Output</b>", body_style), Paragraph("Generates grounded markdown chat response + streams neural speech.", body_style), Paragraph("Gemini + Edge-TTS", body_style)],
    ]
    t_arch = Table(arch_data, colWidths=[110, 290, 104])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # Section 2: Conversational Memory Buffer
    story.append(Paragraph("2. Conversational Memory Architecture (Short-Term Buffer)", h1_style))
    story.append(Paragraph(
        "Standard RAG handles each query in isolation. The Memory Buffer maintains a rolling window of recent dialog turns, allowing the user to ask follow-up questions naturally (e.g. <i>'What about last month?'</i>, <i>'Which of those was highest?'</i>).",
        body_style
    ))

    code_memory = """# File: ai_engine/memory.py
from dataclasses import dataclass, field
from typing import List, Dict
import time

@dataclass
class ConversationTurn:
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float = field(default_factory=time.time)

class SessionMemoryBuffer:
    def __init__(self, max_turns: int = 8):
        self.max_turns = max_turns
        self._history: List[ConversationTurn] = []

    def add_user_message(self, text: str):
        self._history.append(ConversationTurn(role='user', content=text))
        self._trim()

    def add_bot_message(self, text: str):
        self._history.append(ConversationTurn(role='assistant', content=text))
        self._trim()

    def get_context_tuples(self) -> List[Dict[str, str]]:
        return [{'role': t.role, 'text': t.content} for t in self._history]

    def _trim(self):
        if len(self._history) > self.max_turns * 2:
            self._history = self._history[-(self.max_turns * 2):]

    def rewrite_query_with_context(self, current_query: str) -> str:
        \"\"\"Condenses follow-up queries using prior turn context.\"\"\"
        if not self._history:
            return current_query
        
        last_turns = self._history[-4:]
        pronouns = ['it', 'those', 'them', 'that', 'same', 'there', 'what about', 'how about']
        is_followup = any(p in current_query.lower() for p in pronouns) or len(current_query.split()) < 4
        
        if is_followup and len(last_turns) >= 2:
            prev_user = [t.content for t in last_turns if t.role == 'user'][-1]
            return f"{prev_user} -> follow up: {current_query}"
        return current_query
"""
    t_code1 = Table([[Preformatted(code_memory, code_style)]], colWidths=[504])
    t_code1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code1)
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # Section 3: Local Vector Index & Semantic Retriever
    story.append(Paragraph("3. Local Vector Index & Semantic Search (Zero Cost)", h1_style))
    story.append(Paragraph(
        "To achieve zero cost and instant search, we build a local vector index using high-performance TF-IDF sublinear vectors or dense embeddings with Cosine Similarity. When bank statements are uploaded, every transaction chunk is indexed instantly.",
        body_style
    ))

    code_rag = """# File: ai_engine/rag.py
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any

class LocalFinancialVectorStore:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            sublinear_tf=True,
            token_pattern=r'(?u)\\b\\w+\\b'
        )
        self.documents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.matrix = None

    def build_index(self, transactions: List[Dict[str, Any]]):
        \"\"\"Indexes a list of transactions into memory.\"\"\"
        self.documents = []
        self.metadata = []
        for txn in transactions:
            # Create rich semantic chunk
            chunk = (
                f"Date: {txn.get('txn_date')} | "
                f"Payee/Narration: {txn.get('description')} | "
                f"Amount: Rs. {txn.get('amount')} | "
                f"Type: {txn.get('txn_type')} | "
                f"Category: {txn.get('category', 'Uncategorized')}"
            )
            self.documents.append(chunk)
            self.metadata.append(txn)
            
        if self.documents:
            self.matrix = self.vectorizer.fit_transform(self.documents)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        \"\"\"Performs cosine similarity search against indexed transactions.\"\"\"
        if self.matrix is None or not self.documents:
            return []
            
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] > 0.05:  # Relevance threshold
                results.append({
                    'chunk': self.documents[idx],
                    'score': float(scores[idx]),
                    'txn': self.metadata[idx]
                })
        return results
"""
    t_code2 = Table([[Preformatted(code_rag, code_style)]], colWidths=[504])
    t_code2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code2)
    story.append(Spacer(1, 10))

    # Section 4: Hybrid RAG & Query Routing
    story.append(Paragraph("4. Hybrid Query Router (Vector Search + SQL Math)", h1_style))
    story.append(Paragraph(
        "Financial systems must never guess mathematical sums. The Hybrid Router sends numerical and aggregate questions to PostgreSQL/Django ORM (`Sum`, `Avg`, `Count`) while sending vendor and semantic discovery questions to the Vector Store.",
        body_style
    ))

    code_hybrid = """# File: ai_engine/hybrid_router.py
import re
from django.db.models import Sum, Count, Avg
from tracker.models import Transaction

def route_and_retrieve(user, query: str, vector_store: LocalFinancialVectorStore) -> Dict[str, Any]:
    q_lower = query.lower()
    math_triggers = ['total', 'how much', 'spent on', 'sum', 'average', 'highest', 'largest']
    
    # 1. Check if query asks for aggregations (SQL Engine)
    is_math_query = any(k in q_lower for k in math_triggers)
    math_summary = {}
    
    if is_math_query:
        qs = Transaction.objects.filter(account__user=user)
        # Check category matches
        for cat in ['Food & Dining', 'Travel & Fuel', 'Shopping', 'Bills & Utilities', 'Groceries']:
            if cat.lower() in q_lower or cat.split()[0].lower() in q_lower:
                qs = qs.filter(category__iexact=cat)
                
        agg = qs.aggregate(total_spent=Sum('debit'), count=Count('id'), avg_spent=Avg('debit'))
        math_summary = {
            'total_debit': float(agg['total_spent'] or 0.0),
            'transaction_count': agg['count'] or 0,
            'average_debit': float(agg['avg_spent'] or 0.0)
        }

    # 2. Perform Semantic Vector Search (Top-5 Chunks)
    vector_results = vector_store.search(query, top_k=5)
    
    return {
        'math_summary': math_summary,
        'semantic_chunks': [r['chunk'] for r in vector_results],
        'raw_transactions': [r['txn'] for r in vector_results]
    }
"""
    t_code3 = Table([[Preformatted(code_hybrid, code_style)]], colWidths=[504])
    t_code3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code3)
    story.append(Spacer(1, 10))

    story.append(PageBreak())

    # Section 5: Grounded LLM Context Fusion & Voice
    story.append(Paragraph("5. Grounded Prompt Formulation & Voice Synthesis", h1_style))
    story.append(Paragraph(
        "We inject the conversation history, mathematical calculations, and retrieved transaction chunks directly into the prompt. The response is rendered in the chat and spoken via the SET Neural Voice module.",
        body_style
    ))

    code_chat = """# File: ai_engine/chat.py
import google.genai as genai
from config import settings

def generate_rag_response(user, user_query: str, session_memory, vector_store) -> str:
    # 1. Resolve query with conversation memory
    search_query = session_memory.rewrite_query_with_context(user_query)
    
    # 2. Retrieve Hybrid Context
    context_data = route_and_retrieve(user, search_query, vector_store)
    
    # 3. Construct Grounded Prompt
    prompt = f\"\"\"You are SET (Smart Expense Tracker AI), an expert financial assistant.
User Name: {user.first_name or user.username}

RELEVANT RETRIEVED TRANSACTIONS:
{chr(10).join(context_data['semantic_chunks']) if context_data['semantic_chunks'] else 'No specific semantic matches found.'}

CALCULATED FINANCIAL DATA (SQL GROUND TRUTH):
{context_data['math_summary']}

RECENT DIALOG HISTORY:
{session_memory.get_context_tuples()}

USER QUESTION: {user_query}

GUIDELINES:
1. Address the user naturally by name ({user.first_name or user.username}). Never use 'boss'.
2. Use Rupees (₹) for all currency figures.
3. Be precise with dates, vendors, and amounts.
4. Keep the explanation crisp, helpful, and concise.
\"\"\"
    
    # 4. Call Gemini (Free Tier)
    if settings.GEMINI_API_KEY:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        reply = response.text
    else:
        # Intelligent Offline Local Fallback
        reply = local_financial_fallback(user, user_query, context_data)
        
    # 5. Store turn in memory buffer
    session_memory.add_user_message(user_query)
    session_memory.add_bot_message(reply)
    
    return reply
"""
    t_code4 = Table([[Preformatted(code_chat, code_style)]], colWidths=[504])
    t_code4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code4)
    story.append(Spacer(1, 10))

    # Section 6: Step by Step Implementation Checklist
    story.append(Paragraph("6. Step-by-Step Implementation & Viva Checklist", h1_style))
    checklist_items = [
        "<b>Step 1:</b> Create <code>ai_engine/memory.py</code> with <code>SessionMemoryBuffer</code> to retain rolling multi-turn context.",
        "<b>Step 2:</b> Create <code>ai_engine/rag.py</code> with <code>LocalFinancialVectorStore</code> for zero-cost semantic search.",
        "<b>Step 3:</b> Update <code>tracker/views.py</code> upload endpoint to auto-index newly ingested transactions into the vector store.",
        "<b>Step 4:</b> Integrate <code>route_and_retrieve</code> in <code>ai_engine/chat.py</code> to fuse SQL math ground-truth with semantic chunks.",
        "<b>Step 5:</b> Stream voice output using <code>/api/tts/</code> (SET Neural Voice with Pause/Continue/Stop controller).",
        "<b>Step 6:</b> Test multi-turn follow-ups: <i>'How much spent on Swiggy?'</i> &rarr; <i>'What about Zomato?'</i> &rarr; <i>'Which was largest?'</i>"
    ]
    for item in checklist_items:
        story.append(Paragraph(f"• {item}", bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    pdf_path = os.path.abspath("RAG_With_Memory_Blueprint_SET.pdf")
    create_rag_blueprint_pdf(pdf_path)
