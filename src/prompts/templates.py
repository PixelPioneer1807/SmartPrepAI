from langchain.prompts import PromptTemplate

mcq_prompt_template = PromptTemplate(
    template=(
        "Generate a {difficulty} multiple-choice question about {topic}.\n\n"
        "Return ONLY a JSON object with these exact fields: (strict)\n"
        "- 'question': A clear, specific question\n"
        "- 'options': An array of exactly 4 possible answers\n"
        "- 'correct_answer': One of the options that is the correct answer\n"
        "- 'explanation': A concise explanation (2-3 sentences) of why the correct answer is right and why it's important\n\n"
        "Example format:\n"
        '{{\n'
        '  "question": "What is the time complexity of binary search?",\n'
        '  "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],\n'
        '  "correct_answer": "O(log n)",\n'
        '  "explanation": "Binary search has O(log n) time complexity because it eliminates half of the search space in each iteration by comparing the target with the middle element. This logarithmic behavior makes it very efficient for searching in sorted arrays."\n'
        '}}\n\n'
        "Your response:"
    ),
    input_variables=["topic", "difficulty"]
)

fill_blank_prompt_template = PromptTemplate(
    template=(
        "Generate a {difficulty} fill-in-the-blank question about {topic}.\n\n"
        "Return ONLY a JSON object with these exact fields:\n"
        "- 'question': A sentence with '___' marking where the blank should be\n"
        "- 'answer': The correct word or phrase that belongs in the blank\n"
        "- 'explanation': A concise explanation (2-3 sentences) of why this answer is correct and its significance\n\n"
        "Example format:\n"
        '{{\n'
        '  "question": "The ___ scheduling algorithm gives priority to the process with the shortest burst time.",\n'
        '  "answer": "SJF",\n'
        '  "explanation": "SJF (Shortest Job First) scheduling selects the process with the smallest execution time first. This approach minimizes the average waiting time for all processes in the system."\n'
        '}}\n\n'
        "Your response:"
    ),
    input_variables=["topic", "difficulty"]
)
rag_prompt_template = PromptTemplate(
    template=(
        "You are an AI tutor. Your task is to create a new multiple-choice question to help a student learn from their past mistakes.\n\n"
        "The student is studying the topic: '{topic}'.\n\n"
        "Here are some examples of questions the student answered incorrectly in the past:\n"
        "--- CONTEXT ---\n"
        "{context}\n"
        "--- END CONTEXT ---\n\n"
        "Based on the context of their previous errors, generate a new, conceptually similar multiple-choice question to test their understanding of the underlying principles.\n"
        "The question should be of '{difficulty}' difficulty.\n\n"
        "Return ONLY a JSON object with these exact fields: (strict)\n"
        "- 'question': A clear, specific question that targets a weak area from the context.\n"
        "- 'options': An array of exactly 4 possible answers.\n"
        "- 'correct_answer': One of the options that is the correct answer.\n"
        "- 'explanation': A concise explanation (2-3 sentences) of why the correct answer is right.\n\n"
        "Your response:"
    ),
    input_variables=["topic", "context", "difficulty"]
)