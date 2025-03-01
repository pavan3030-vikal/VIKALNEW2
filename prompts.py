# prompts.py
"""
VIKAL’s next-level prompt templates—crafted to make learning epic.
- Generic: Bold, engaging explanations and solutions for /explain and /solve endpoints.
"""

PROMPTS = {
    "generic": {
        "explanation": """
Explain {topic} like a pro with VIKAL’s signature style:

### Quick Dive
- Sum up {topic} in 2-3 punchy sentences a beginner would love.

### Deep Dive
- Break down {topic}’s core ideas with razor-sharp accuracy.
- Toss in a historical nugget or a “wow” fact tied to {category}.
- Show how {topic} works in real life with one killer example.

### Must-Knows
- List 3-5 game-changing concepts or formulas for {topic}.
- Keep each explanation tight and crystal-clear.

### VIKAL Brain Booster
- Craft a wild analogy or mnemonic to make {topic} unforgettable (e.g., “TCP is like a cosmic mailman…”).

### Real-World Wins
- Drop 3 jaw-dropping uses of {topic} today—make them specific and cool.

### Flashcards
- Create 5 question-and-answer pairs on {topic}’s key bits.
- Format each as: "Q: [Question]? A: [Short, sharp answer]."

### VIKAL’s Exam Cheat Codes
- Share 3-5 slick tricks to ace questions on {topic} (e.g., “Watch for this trap…”).

### Power-Ups
- Suggest 3 top-tier resources (e.g., “5-min Khan Academy vid: [url]”).

Keep it student-friendly, sharp, and packed with VIKAL’s vibe!
""",
        "solution": {
            "smart": """
Solve {topic} with VIKAL’s quick genius:

### Solution
- Crack {topic} in under 100 words with slick shortcuts.
- Add a “VIKAL’s Pro Tip” for extra brilliance.
- Box the answer: \\boxed{{answer}}.

### VIKAL’s Solve Smarter Hacks
- Drop 3-5 genius tips to nail this in exams.

### Power-Ups
- List 5 killer resources for {topic} (e.g., “Quick vid: [url]”).

Make it fast, fierce, and VIKAL-sharp!
""",
            "step": """
Solve {topic} with VIKAL’s step-by-step magic:

### Solution
- Crack {topic} in under 200 words with numbered, no-fail steps.
- Sneak in a “VIKAL’s Pro Tip” (e.g., a shortcut or insight).
- Box the answer: \\boxed{{answer}}.

### VIKAL’s Solve Smarter Hacks
- Drop 3-5 slick tips to ace this problem type.

### Power-Ups
- List 5 killer resources tied to {topic}.

Keep it clear, precise, and VIKAL-cool!
""",
            "teacher": """
Solve {topic} with VIKAL’s teacher vibe:

### Solution
- Solve {topic} in under 200 words with simple steps and a fun example.
- Add a “VIKAL’s Pro Tip” to spark an “aha!” moment.
- Box the answer: \\boxed{{answer}}.

### VIKAL’s Solve Smarter Hacks
- Share 3-5 friendly tips to master this for exams.

### Power-Ups
- Suggest 5 engaging resources for {topic}.

Teach it VIKAL-style—clear and inspiring!
""",
            "research": """
Solve {topic} with VIKAL’s research edge:

### Solution
- Solve {topic} in under 300 words with deep steps and context.
- Include a “VIKAL’s Pro Tip” for advanced insight.
- Box the answer: \\boxed{{answer}}.

### VIKAL’s Solve Smarter Hacks
- Give 3-5 pro-level tips for exam domination.

### Power-Ups
- List 5 hardcore resources for {topic}.

Make it rigorous, rich, and VIKAL-bold!
"""
        }
    }
}

def get_prompt(category, type_key, style, topic, transcript=None):
    """
    Fetch the appropriate prompt based on category, type_key, style, and topic.
    - For /explain: Uses generic.explanation.
    - For /solve: Uses generic.solution with the specified style.
    """
    if type_key == "explanation":
        return PROMPTS["generic"]["explanation"].format(topic=topic, category=category)
    # Default to generic for all categories for now; expand with 'exams' later if needed
    section = "generic"
    return PROMPTS.get(section, {}).get(type_key, {}).get(style.lower(), PROMPTS["generic"]["solution"]["teacher"]).format(topic=topic)
