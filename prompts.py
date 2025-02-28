# prompts.py
"""
Centralized prompt templates for VIKAL's queries.
- Generic: Precise, structured explanations and summaries for Learn/Summarize modes.
- Exams (UPSC, GATE, RRB): Detailed, exam-focused solutions for Solve mode.
"""

PROMPTS = {
    "generic": {
        "explanation": """
Explain {topic} comprehensively and accurately using this exact format:

### Simple Explanation
- Provide a concise, beginner-friendly overview of {topic} in 2-3 sentences using clear, everyday language.

### In-Depth Explanation
- Detail the key principles or components of {topic} with technical accuracy.
- Include historical context or development if relevant (e.g., for engineering concepts).
- Outline main theories or schools of thought where applicable.
- Explain how {topic} functions or is applied in its field, with specific examples.

### Key Concepts or Formulas
- List 3-5 critical concepts, formulas, or frameworks essential to {topic}.
- Provide a brief, precise explanation for each, avoiding ambiguity.

### Real-World Applications or Examples
- Describe 3 specific, practical applications or examples of {topic} in modern contexts.
- Ensure examples are concrete and relevant (e.g., engineering use cases).

### Flashcards
- Create 5 question-and-answer flashcards on key aspects of {topic}.
- Format each as: "Q: [Question]? A: [Concise, accurate answer]."

### Exam Tips
- List 3-5 actionable points to remember for an exam on {topic}.
- Focus on common pitfalls, key formulas, or testable concepts.

### Resources
- Recommend 3 reliable, specific sources for further study (e.g., books, websites, videos).
- Ensure sources are authoritative and accessible.

Instructions:
- Tailor all content for a student audience—clear, concise, and exam-relevant.
- Use precise language, avoiding vague or generic statements.
- For engineering topics, emphasize practical EE applications and accuracy.
""",
        "summary": """
Summarize this YouTube video transcript accurately using this exact format:

### Summary
- Provide a concise, clear overview of the video content in 2-3 sentences, capturing the main idea.

### Analogy
- Create a short, relatable analogy (complex or day-to-day) to contextualize the video’s content.

### Notes
- List 10 key points or moments from the transcript as bullet points.
- Use an appropriate emoji for each (e.g., 📌 for key idea, ⚡ for insight).
- Keep each point concise, specific, and tied to the transcript.

### Keywords
- Extract 5-7 critical keywords, complex terms, or acronyms from the transcript.
- For each, provide a clear definition or explanation based on its context.

### Exam Tips
- List 3-5 actionable points to remember for an exam based on the video content.
- Highlight testable ideas or common exam traps.

Instructions:
- Base all content solely on this transcript: Video Title {topic} {transcript}.
- Limit output to 330 words—prioritize clarity and relevance.
- Tailor for a student audience, ensuring accuracy and exam focus.
""",
        "solution": {
            "smart": """
Solve this problem efficiently: {topic}.
Use this exact format:

### Solution
- Provide a concise solution to {topic} in under 100 words.
- Use shortcuts or key insights where applicable, ensuring accuracy.
- Include final answer in a boxed format (e.g., \\boxed{{answer}}).

### Exam Tips
- List 3 actionable points to remember for an exam on this problem type.
- Focus on quick methods, common errors, or key checks.

### Resources
- Recommend 5 specific, reliable sources for further study (e.g., books, websites).
- Ensure sources are authoritative and relevant.

Instructions:
- Tailor for a student audience—clear, precise, exam-focused.
- Avoid unnecessary steps—optimize for speed and correctness.
""",
            "step": """
Solve this problem with detailed steps: {topic}.
Use this exact format:

### Solution
- Solve {topic} in under 200 words using clear, numbered steps.
- Include all intermediate calculations and reasoning.
- Present the final answer in a boxed format (e.g., \\boxed{{answer}}).

### Exam Tips
- List 3-5 actionable points to remember for an exam on this problem type.
- Highlight critical steps, formulas, or pitfalls.

### Resources
- Recommend 5 specific, reliable sources for further study.
- Ensure sources are authoritative and relevant.

Instructions:
- Tailor for a student audience—logical, precise, exam-ready.
- Ensure steps are complete, accurate, and easy to follow.
""",
            "teacher": """
Solve this problem like a teacher: {topic}.
Use this exact format:

### Solution
- Solve {topic} in under 200 words with clear steps and simple explanations.
- Include relatable examples or analogies to clarify concepts.
- Present the final answer in a boxed format (e.g., \\boxed{{answer}}).

### Exam Tips
- List 3-5 actionable points to remember for an exam on this problem type.
- Focus on understanding, common mistakes, or key takeaways.

### Resources
- Recommend 5 specific, reliable sources for further study.
- Ensure sources are authoritative and engaging.

Instructions:
- Tailor for a student audience—friendly, clear, exam-focused.
- Emphasize teaching clarity and practical insights.
""",
            "research": """
Solve this problem in a detailed, research style: {topic}.
Use this exact format:

### Solution
- Solve {topic} in under 300 words with in-depth steps and context.
- Include technical details, derivations, or theoretical insights where relevant.
- Present the final answer in a boxed format (e.g., \\boxed{{answer}}).

### Exam Tips
- List 3-5 actionable points to remember for an exam on this problem type.
- Highlight advanced concepts, derivations, or exam strategies.

### Resources
- Recommend 5 specific, reliable sources for further study.
- Ensure sources are authoritative, detailed, and academic.

Instructions:
- Tailor for a student audience—rigorous, precise, exam-ready.
- Provide comprehensive reasoning and technical accuracy.
"""
        }
    },
    "exams": {
        "upsc": {
            "solution": {
                "smart": "Solve this UPSC question efficiently: {topic}. Provide concise solution (100 words) with shortcuts under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}} for final answer. Ensure clarity, accuracy, and exam relevance.",
                "step": "Solve this UPSC question with detailed steps: {topic}. Provide solution (200 words) with numbered steps under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}}. Ensure precision and exam focus.",
                "teacher": "Solve this UPSC question like a teacher: {topic}. Provide clear solution (200 words) with examples under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}}. Ensure simplicity and exam readiness.",
                "research": "Solve this UPSC question in research style: {topic}. Provide detailed solution (300 words) with context under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}}. Ensure depth and exam relevance."
            }
        },
        "gate": {
            "solution": {
                "smart": "Solve this GATE question efficiently: {topic}. Provide concise solution (100 words) with shortcuts under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}}. Ensure EE accuracy and exam focus.",
                "step": "Solve this GATE question with steps: {topic}. Provide solution (200 words) with numbered steps under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}}. Ensure EE precision and exam readiness.",
                "teacher": "Solve this GATE question like a teacher: {topic}. Provide clear solution (200 words) with examples under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}}. Ensure EE clarity and exam focus.",
                "research": "Solve this GATE question thoroughly: {topic}. Provide detailed solution (300 words) with derivations under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}}. Ensure EE depth and exam relevance."
            }
        },
        "rrb": {
            "solution": {
                "smart": "Solve this RRB question efficiently: {topic}. Provide concise solution (100 words) with shortcuts under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}}. Ensure clarity and exam focus.",
                "step": "Solve this RRB question with steps: {topic}. Provide solution (200 words) with numbered steps under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}}. Ensure precision and exam readiness.",
                "teacher": "Solve this RRB question like a teacher: {topic}. Provide clear solution (200 words) with examples under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}}. Ensure simplicity and exam focus.",
                "research": "Solve this RRB question in detail: {topic}. Provide detailed solution (300 words) with context under ### Solution, 3-5 exam tips under ### Exam Tips, and 5+ specific resources under ### Resources. Use \\boxed{{answer}}. Ensure depth and exam relevance."
            }
        }
    }
}

def get_prompt(category, type_key, style, topic, transcript=None):
    """
    Fetch the appropriate prompt based on category (exam/generic), type (solution/explanation/summary), style, and topic.
    Default to generic explanation if type matches, regardless of style or category.
    """
    if type_key == "explanation":
        return PROMPTS["generic"]["explanation"].format(topic=topic)
    elif type_key == "summary" and transcript:
        return PROMPTS["generic"]["summary"].format(topic=topic, transcript=transcript)
    section = "exams" if category in ["upsc", "gate", "rrb"] else "generic"
    return PROMPTS.get(section, {}).get(type_key, {}).get(style.lower(), f"Solve {topic} with style {style}.").format(topic=topic)