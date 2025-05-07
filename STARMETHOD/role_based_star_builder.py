import os
import re
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from collections import defaultdict

def star_story_builder():
    """
    Role-based STAR method story builder for interview preparation.
    Incorporates role-specific competency frameworks and provides tailored guidance.
    """
    # Initialize competency database from PDFs
    print("Loading competency frameworks from PDF files...")
    # competency_data = load_apple_competencies_from_pdfs() # Now load_role_competencies_from_pdfs
    competency_data = load_role_competencies_from_pdfs() # Changed here

    visualize_competency_data(competency_data)

    competencies_dict = competency_data['roles_competencies']
    competency_details = competency_data['competency_details']

    print("\\n🌟 Welcome to the Role-Based STAR Story Builder!")
    print("This program helps structure your answers using the STAR method,")
    print("focusing on competencies relevant to specific roles.")
    print("\\n**The STAR Method:**")
    print("S - Situation: Describe the context and background.")
    print("T - Task: Explain your responsibility and objectives.")
    print("A - Action: Detail the steps you took to address the situation.")
    print("R - Result: Highlight the outcomes and what you learned.")

    # Select role
    print("\nFirst, let's identify the role you're interviewing for:")
    available_roles = list(competencies_dict.keys())
    for i, role in enumerate(available_roles, 1):
        print(f"{i}. {role}")

    while True:
        try:
            role_idx = int(input("\nEnter the number of your target role: ")) - 1
            selected_role = available_roles[role_idx]
            break
        except (ValueError, IndexError):
            print("Please enter a valid number from the list.")

    role_competencies = competencies_dict[selected_role]

    print(f"\nYou selected: {selected_role}")
    print("Key competencies for this role include:")
    for comp in role_competencies:
        print(f"- {comp}")
        # Show competency description if available
        if comp in competency_details and competency_details[comp]['description']:
            print(f"  Description: {competency_details[comp]['description'][:150]}...")

    # Main loop
    while True:
        print("\n" + "="*50)
        print("Enter your interview question (or type one of the following):")
        print("- 'competencies': View key competencies for your role")
        print("- 'samples': View sample interview questions")
        print("- 'exit': Quit the program")

        question = input("\nQuestion: ")
        if question.lower() == 'exit':
            print("\nThank you for practicing! Good luck with your interview!")
            break

        if question.lower() == 'competencies':
            print(f"\nKey competencies for {selected_role}:")
            for comp in role_competencies:
                print(f"- {comp}")
            continue

        if question.lower() == 'samples':
            print("\nSample Interview Questions for this role:")
            sample_questions = get_role_specific_questions(selected_role)
            for i, q in enumerate(sample_questions, 1):
                print(f"{i}. {q}")
            continue

        # Identify relevant competencies for this question
        print(f"\nAnalyzing: \"{question}\"")
        print("\nThis question likely targets these competencies:")

        relevant_competencies = identify_relevant_competencies(question, role_competencies)
        for comp in relevant_competencies:
            print(f"- {comp}")

        # Choose primary competency to focus on
        primary_competency = choose_primary_competency(relevant_competencies)
        print(f"\nWe'll focus on demonstrating '{primary_competency}'.")

        # Build the STAR story with enhanced guidance
        story = build_enhanced_star_story(question, primary_competency, competency_details)

        # Generate a "Talented" level response
        talented_response = generate_talented_response(story, primary_competency, competency_details)

        # Present the enhanced story
        print("\n" + "="*50)
        print("🌟 YOUR ENHANCED STAR INTERVIEW RESPONSE:")
        print(f"\nQuestion: {question}")
        print(f"\nCompetency Focus: {primary_competency}")
        print("\n🔹 SITUATION:")
        print(talented_response['situation'])
        print("\n🔹 TASK:")
        print(talented_response['task'])
        print("\n🔹 ACTION:")
        print(talented_response['action'])
        print("\n🔹 RESULT:")
        print(talented_response['result'])

        # Save option
        save_choice = input("\nSave this story? (yes/no): ").lower()
        if save_choice in ['yes', 'y']:
            filename = save_enhanced_story(talented_response, question, primary_competency)
            print(f"Story saved to {filename}")

# def load_apple_competencies():
def load_role_competencies(): # Renamed function
    """
    Load sample competencies for different roles. (Previously Apple-specific)
    """
    # This data is still somewhat Apple-like but serves as an example structure.
    return {
        "Software Engineer": [
            "Technical Problem Solving",
            "Innovation",
            "Collaboration",
            "Communication",
            "Customer Focus"
        ],
        "Product Manager": [
            "Strategic Thinking",
            "User-Centered Design",
            "Cross-Functional Leadership",
            "Business Acumen",
            "Execution Excellence"
        ],
        "UX Designer": [
            "User Empathy",
            "Design Thinking",
            "Visual Communication",
            "Prototyping Skills",
            "Collaborative Problem Solving"
        ],
        "Data Scientist": [
            "Analytical Thinking",
            "Statistical Modeling",
            "Programming Skills",
            "Business Impact",
            "Communication of Complex Ideas"
        ],
        "Operations": [
            "Process Improvement",
            "Attention to Detail",
            "Problem Solving",
            "Adaptability",
            "Time Management"
        ]
    }

def get_role_specific_questions(role):
    """
    Get sample interview questions specific to a role.
    """
    questions = {
        "Software Engineer": [
            "Tell me about a time you solved a complex technical problem.",
            "Describe a situation where you had to learn a new technology quickly.",
            "Give an example of when you improved the performance of an application.",
            "Tell me about a time you collaborated with a difficult team member.",
            "Describe a situation where you had to make a technical trade-off."
        ],
        "Product Manager": [
            "Tell me about a time you identified a user need that led to a successful product feature.",
            "Describe how you prioritized competing product features.",
            "Give an example of when you had to influence stakeholders without authority.",
            "Tell me about a product launch that didn't go as planned and what you learned.",
            "Describe how you've used data to make product decisions."
        ],
        "UX Designer": [
            "Tell me about a time you advocated for the user despite business pushback.",
            "Describe a project where you improved a user experience significantly.",
            "How have you incorporated user feedback into your design process?",
            "Tell me about a time you had to simplify a complex design problem.",
            "Describe how you've collaborated with engineers to implement your designs."
        ],
        "Data Scientist": [
            "Tell me about a project where your analysis led to a business impact.",
            "Describe a time you had to explain complex technical findings to non-technical stakeholders.",
            "How have you handled a situation with incomplete or messy data?",
            "Tell me about a time you built a model that failed and what you learned.",
            "Describe a project where you had to balance statistical rigor with business needs."
        ],
        "Operations": [
            "Tell me about a time you improved an operational process.",
            "Describe a situation where you had to handle a crisis or unexpected problem.",
            "How have you ensured quality in your work?",
            "Tell me about a time you had to meet a tight deadline.",
            "Describe how you've handled competing priorities."
        ]
    }
    
    return questions.get(role, [
        "Tell me about a time you demonstrated excellence in your work.",
        "Describe a situation where you had to solve a problem creatively.",
        "Give an example of when you collaborated effectively with others.",
        "Tell me about a time you had to adapt to change.",
        "Describe a situation where you went above and beyond expectations."
    ])

def identify_relevant_competencies(question, competencies):
    """Identify which competencies are most relevant to the given question."""
    keyword_mapping = {
        "customer": ["Customer Focus"],
        "relationship": ["Customer Focus", "Interpersonal Savvy"],
        "uncertain": ["Manages Ambiguity"],
        "ambiguous": ["Manages Ambiguity"],
        "technology": ["Tech Savvy"],
        "innovation": ["Tech Savvy"],
        "challenge": ["Action Oriented", "Being Resilient"],
        "conflict": ["Manages Conflict"],
        "complex": ["Manages Complexity", "Managing Complexity"],
        "result": ["Drives Results"],
        "communicate": ["Communicates Effectively"],
        "decision": ["Decision Quality"],
        "collaborate": ["Collaborates"],
        "team": ["Collaborates", "Interpersonal Savvy"],
        "resilient": ["Being Resilient"],
        "adapt": ["Situational Adaptability"],
        "resource": ["Resourcefulness"],
        "business": ["Business Insight"],
        "plan": ["Plans and Aligns"],
        "persuade": ["Persuades"],
        "influence": ["Persuades"],
        "learn": ["Nimble Learning", "Self Development"],
        "accountability": ["Ensures Accountability"],
        "process": ["Optimizes Work Processes"],
        "grow": ["Self Development"]
    }
    
    matching_competencies = set()
    question_lower = question.lower()
    
    for keyword, related_comps in keyword_mapping.items():
        if keyword in question_lower:
            for comp in related_comps:
                if comp in competencies:
                    matching_competencies.add(comp)
    
    # If no matches, return the first 2-3 competencies for the role
    if not matching_competencies:
        return competencies[:min(3, len(competencies))]
    
    return list(matching_competencies)[:3]  # Return top 3 matches

def choose_primary_competency(competencies):
    """
    Let the user choose which competency to focus on.
    """
    if len(competencies) == 1:
        return competencies[0]
        
    print("\nWhich competency would you like to focus on for this story?")
    for i, comp in enumerate(competencies, 1):
        print(f"{i}. {comp}")
    
    while True:
        try:
            choice = int(input("Enter your choice (number): ")) - 1
            if 0 <= choice < len(competencies):
                return competencies[choice]
            else:
                print(f"Please enter a number between 1 and {len(competencies)}")
        except ValueError:
            print("Please enter a valid number")

def build_enhanced_star_story(question, competency, competency_details):
    """
    Build a STAR story with enhanced guidance based on the competency.
    """
    story = {}
    
    # --- S: Situation ---
    print(f"\n🔹 SITUATION: Set the scene where you demonstrated {competency}")
    print(get_competency_situation_prompt(competency, competency_details))
    
    story['situation'] = input("\nDescribe the Situation:\n")
    
    # Ask clarifying questions for the situation
    clarifying_questions = get_situation_clarifying_questions(competency, story['situation'])
    if clarifying_questions:
        print("\nLet me ask a few clarifying questions to enhance your situation:")
        for q in clarifying_questions:
            additional_info = input(f"- {q}\n")
            if additional_info:
                story['situation'] += f" {additional_info}"
    
    print(f"Word count: {word_count(story['situation'])} words")
    
    # --- T: Task ---
    print(f"\n🔹 TASK: What was your responsibility related to {competency}?")
    print(get_competency_task_prompt(competency, competency_details))
    
    story['task'] = input("\nDescribe the Task:\n")
    
    # Ask clarifying questions for the task
    clarifying_questions = get_task_clarifying_questions(competency, story['task'])
    if clarifying_questions:
        print("\nTo strengthen your task description:")
        for q in clarifying_questions:
            additional_info = input(f"- {q}\n")
            if additional_info:
                story['task'] += f" {additional_info}"
    
    print(f"Word count: {word_count(story['task'])} words")
    
    # --- A: Action ---
    print(f"\n🔹 ACTION: Detail how you demonstrated {competency}")
    print(get_competency_action_prompt(competency, competency_details))
    
    story['action'] = input("\nDescribe the Action:\n")
    
    # Ask clarifying questions for the action
    clarifying_questions = get_action_clarifying_questions(competency, story['action'])
    if clarifying_questions:
        print("\nTo make your actions more impressive:")
        for q in clarifying_questions:
            additional_info = input(f"- {q}\n")
            if additional_info:
                story['action'] += f" {additional_info}"
    
    print(f"Word count: {word_count(story['action'])} words")
    
    # --- R: Result ---
    print(f"\n🔹 RESULT: What was the outcome that showcases {competency}?")
    print(get_competency_result_prompt(competency, competency_details))
    
    story['result'] = input("\nDescribe the Result:\n")
    
    # Ask clarifying questions for the result
    clarifying_questions = get_result_clarifying_questions(competency, story['result'])
    if clarifying_questions:
        print("\nTo make your results more impactful:")
        for q in clarifying_questions:
            additional_info = input(f"- {q}\n")
            if additional_info:
                story['result'] += f" {additional_info}"
    
    print(f"Word count: {word_count(story['result'])} words")
    
    return story

def get_competency_situation_prompt(competency, competency_details=None):
    """Return competency-specific prompts for the situation section."""
    if competency_details and competency in competency_details and competency_details[competency]['situation']:
        return f"Suggested guidance for {competency} situations:\n{competency_details[competency]['situation']}"

    prompts = {
        "Customer Focus": "Describe a situation involving customer needs or expectations. What was the customer context?",
        "Tech Savvy": "Describe a situation requiring technical innovation or digital solutions. What was the technology landscape?",
        "Drives Results": "Describe a challenging situation with clear objectives. What obstacles were you facing?",
        # Add more competency-specific prompts here
    }

    default = "Consider:\n- What was the context?\n- When and where did this happen?\n- Who was involved?\n- What challenges existed?"

    return prompts.get(competency, default)

def get_competency_task_prompt(competency, competency_details=None):
    """Return competency-specific prompts for the task section."""
    if competency_details and competency in competency_details and competency_details[competency]['task']:
        return f"Suggested guidance for {competency} tasks:\n{competency_details[competency]['task']}"

    prompts = {
        "Technical Problem Solving": "What technical challenge were you tasked with solving? What were the requirements or constraints?",
        # ... [rest of your existing prompts]
    }

    default = "Consider:\n- What was your specific responsibility?\n- What goals were you trying to achieve?\n- What challenges did you face?"

    return prompts.get(competency, default)

def get_competency_action_prompt(competency, competency_details=None):
    """Return competency-specific prompts for the action section."""
    if competency_details and competency in competency_details and competency_details[competency]['action']:
        return f"Suggested guidance for {competency} actions:\n{competency_details[competency]['action']}"

    prompts = {
        "Technical Problem Solving": "What specific technical approach did you take? How did you analyze the problem and implement your solution?",
        "Innovation": "What innovative steps did you take? How did you think differently or challenge conventional approaches?",
        # ... existing prompts ...
    }

    default = "Consider:\n- What specific actions did YOU take?\n- How did you approach the problem?\n- What skills or tools did you use?"

    return prompts.get(competency, default)

def get_competency_result_prompt(competency, competency_details=None):
    """Return competency-specific prompts for the result section."""
    if competency_details and competency in competency_details and competency_details[competency]['result']:
        return f"Suggested guidance for {competency} results:\n{competency_details[competency]['result']}"

    prompts = {
        "Technical Problem Solving": "What was the technical outcome? How did it impact performance, reliability, or scalability? Can you quantify the results?",
        "Innovation": "What resulted from your innovative approach? How was it received by users or stakeholders? What impact did it have?",
        "Collaboration": "What did your collaborative approach achieve? How did working together lead to better outcomes than working alone?",
        "Communication": "What was the impact of your communication? How did it improve understanding or influence others?",
        "Customer Focus": "How did your actions improve the customer experience? What customer feedback or metrics demonstrate this?",
        "Strategic Thinking": "What strategic outcomes resulted? How did your approach contribute to long-term goals or vision?",
        "User-Centered Design": "How did users respond to your design? What improvements in user experience or metrics can you point to?",
        "Cross-Functional Leadership": "What did your leadership across teams achieve? How did it overcome organizational silos?",
        "Business Acumen": "What business results did you achieve? Can you quantify the impact in terms of revenue, cost savings, or efficiency?",
        "Execution Excellence": "What quality outcomes resulted from your execution? How did you meet or exceed expectations?",
        "Analytical Thinking": "What insights or conclusions did your analysis produce? How did these findings drive decisions or actions?",
        "Statistical Modeling": "How accurate or useful was your model? What business decisions did it enable?",
        "Programming Skills": "How did your code perform? What improvements in functionality, performance, or reliability resulted?",
        "Process Improvement": "How much more efficient or effective was the process after your changes? Can you quantify the improvement?",
        "Attention to Detail": "How did your thoroughness contribute to quality outcomes? What errors or issues were prevented?",
        "Adaptability": "How did your flexibility lead to positive outcomes? What would have happened without your adaptability?",
        "Design Thinking": "What resulted from your design thinking approach? How did the solution meet user needs in a unique way?",
        "Visual Communication": "How effective was your visual communication? What feedback or metrics show it achieved its purpose?",
        "Prototyping Skills": "What did you learn from your prototypes? How did they influence the final product?",
        "User Empathy": "How did your empathetic approach improve the solution for users? What positive user feedback resulted?",
        "Time Management": "How did you meet your deadlines? What would have happened without your effective time management?",
        "Problem Solving": "What was the outcome of your solution? How effective was it in addressing the core problem?",
        "Communication of Complex Ideas": "How did your audience respond to your communication? Did they understand and act on the complex information?",
        "Business Impact": "What specific business results did you achieve? How did these results align with organizational goals?"
    }
    
    default = "Consider:\n- What was the outcome?\n- What impact did you have?\n- Can you quantify the results?\n- What did you learn?"
    
    return prompts.get(competency, default)

def get_situation_clarifying_questions(competency, situation):
    """Generate clarifying questions for the situation based on the competency."""
    questions = {
        "Technical Problem Solving": [
            "What technologies or systems were specifically involved?",
            "What made this problem particularly challenging from a technical perspective?"
        ],
        "Innovation": [
            "What aspects of the situation required fresh thinking?",
            "What constraints or limitations were you working with?"
        ],
        "Collaboration": [
            "Who were the key stakeholders or team members involved?",
            "What were the team dynamics or challenges that existed?"
        ],
        "Communication": [
            "What communication challenges existed in this situation?",
            "Who was your audience or who did you need to communicate with?"
        ],
        "Customer Focus": [
            "What customer needs or pain points were present in this situation?",
            "What was at stake for the customer experience?"
        ]
    }
    
    # Return specific questions for the competency or a default question
    return questions.get(competency, ["Can you add more specifics about the context and challenges?"])

def get_task_clarifying_questions(competency, task):
    """Generate clarifying questions for the task based on the competency."""
    questions = {
        "Technical Problem Solving": [
            "What specific technical requirements or constraints did you need to consider?",
            "What was the technical goal you needed to achieve?"
        ],
        "Innovation": [
            "Why couldn't this task be solved with conventional approaches?",
            "What objectives required creative thinking?"
        ],
        "Collaboration": [
            "What was your specific role within the team?",
            "What dependencies existed between your work and others'?"
        ],
        "Strategic Thinking": [
            "What business objectives were you trying to support?",
            "What was the strategic importance of this task?"
        ],
        "User-Centered Design": [
            "What user needs were you specifically responsible for addressing?",
            "What user experience goals were you tasked with achieving?"
        ]
    }
    
    return questions.get(competency, ["What specific responsibility or goal was assigned to you?"])

def get_action_clarifying_questions(competency, action):
    """Generate clarifying questions for the action based on the competency."""
    questions = {
        "Technical Problem Solving": [
            "What specific technical approach or methodology did you use?",
            "How did you test or validate your solution?"
        ],
        "Innovation": [
            "What made your approach innovative or different from conventional solutions?",
            "How did you develop or refine your innovative idea?"
        ],
        "Collaboration": [
            "How did you specifically facilitate collaboration or overcome collaboration challenges?",
            "What communication strategies did you employ?"
        ],
        "Communication": [
            "How did you tailor your communication to your audience?",
            "What specific communication techniques did you use?"
        ],
        "User-Centered Design": [
            "How did you incorporate user feedback or research into your actions?",
            "What design methodologies did you employ?"
        ]
    }
    
    return questions.get(competency, ["What specific steps did you personally take?", "How did you overcome challenges?"])

def get_result_clarifying_questions(competency, result):
    """Generate clarifying questions for the result based on the competency."""
    questions = {
        "Technical Problem Solving": [
            "Can you quantify the technical improvements (speed, reliability, etc.)?",
            "What long-term technical benefits resulted from your solution?"
        ],
        "Innovation": [
            "How was your innovation received by users or stakeholders?",
            "Did your innovation lead to any broader changes or improvements?"
        ],
        "Collaboration": [
            "How did your collaborative approach contribute to the team's success?",
            "What feedback did you receive about your collaboration skills?"
        ],
        "Business Impact": [
            "Can you quantify the business impact in terms of revenue, cost savings, or efficiency?",
            "How did your work align with broader business goals?"
        ],
        "User-Centered Design": [
            "How did users respond to your solution?",
            "What measurable improvements in user experience resulted from your work?"
        ]
    }
    
    return questions.get(competency, ["Can you quantify the impact or results?", "What did you personally learn from this experience?"])

def generate_talented_response(story, competency, competency_details=None):
    """
    Generate a "Talented" level response based on the user's inputs and the target competency.
    Uses competency details if available to provide more tailored enhancements.
    """
    enhanced = {}
    
    # Apply enhancements based on competency
    enhanced['situation'] = enhance_text(story['situation'], competency, "situation", competency_details)
    enhanced['task'] = enhance_text(story['task'], competency, "task", competency_details)
    enhanced['action'] = enhance_text(story['action'], competency, "action", competency_details)
    enhanced['result'] = enhance_text(story['result'], competency, "result", competency_details)
    
    return enhanced

def enhance_text(text, competency, section, competency_details=None):
    """
    Enhance text based on competency and section.
    Uses competency details if available to provide more tailored enhancements.
    """
    word_count_val = word_count(text)

    if word_count_val < 20:
        note = f"[Note: Consider expanding this section with more specific details relevant to {competency}."
        if competency_details and competency in competency_details and competency_details[competency][section]:
            examples = competency_details[competency][section]
            note += f" Example: {examples[:100]}...]"
        else:
            note += "]"
        return text + " " + note
    return text

def word_count(text):
    """Count the number of words in text."""
    return len(text.split())

def save_enhanced_story(story, question, competency, filename="star_stories.txt"):
    """Save the enhanced STAR story to a file."""
    import datetime
    with open(filename, "a") as file:
        file.write(f"\n{'=' * 60}\n")
        file.write(f"DATE: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        file.write(f"QUESTION: {question}\n")
        file.write(f"COMPETENCY: {competency}\n\n")
        file.write(f"SITUATION:\n{story['situation']}\n\n")
        file.write(f"TASK:\n{story['task']}\n\n")
        file.write(f"ACTION:\n{story['action']}\n\n")
        file.write(f"RESULT:\n{story['result']}\n\n")
        file.write(f"{'=' * 60}\\n")
    return filename

# def load_apple_competencies_from_pdfs():
def load_role_competencies_from_pdfs(): # Renamed function
    """
    Load role-specific competencies from PDF files in the directory.
    Returns a dictionary mapping roles to their competencies and descriptions.
    """
    try:
        competencies = defaultdict(list)
        competency_details = {}

        # Path to directory containing PDFs
        pdf_dir = os.path.dirname(os.path.abspath(__file__))

        # Try to parse the roles_competencies.pdf for role mappings
        roles_pdf_path = os.path.join(pdf_dir, "roles_competencies.pdf")
        if not os.path.exists(roles_pdf_path):
            # Try alternative path formats
            roles_pdf_path = os.path.join(pdf_dir, "Roles", "Competencies.pdf")
            if not os.path.exists(roles_pdf_path):
                roles_pdf_path = os.path.join(pdf_dir, "Roles_Competencies.pdf")

        if os.path.exists(roles_pdf_path):
            try:
                with open(roles_pdf_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()

                    # Look for role headings and their associated competencies
                    role_pattern = r'([A-Za-z\s]+) Role:?'
                    roles = re.findall(role_pattern, text)

                    for role in roles:
                        role_clean = role.strip()
                        # Find the section for this role
                        role_section_pattern = f"{role}[\\s]*Role:?([\\s\\S]*?)(?=(?:[A-Za-z\\s]+Role:?)|$)"
                        role_section_match = re.search(role_section_pattern, text)

                        if role_section_match:
                            role_text = role_section_match.group(1)
                            # Extract competencies, adjust pattern based on PDF formatting
                            comp_pattern = r'[•\-★]\s*([A-Za-z\s\-]+)(?::|$)'
                            role_competencies = re.findall(comp_pattern, role_text)
                            competencies[role_clean] = [comp.strip() for comp in role_competencies if comp.strip()]

                print(f"Successfully loaded role mappings from {roles_pdf_path}")

                # Print the extracted competencies for verification
                for role, comps in competencies.items():
                    print(f"Role: {role}")
                    for comp in comps:
                        print(f"  - {comp}")

            except Exception as e:
                print(f"Error parsing roles PDF: {e}")
                print("Falling back to hardcoded competencies")
                # return load_apple_competencies_fallback()
                return load_role_competencies_fallback() # Changed here
        else:
            print(f"Could not find competencies PDF at {roles_pdf_path}")
            # return load_apple_competencies_fallback()
            return load_role_competencies_fallback() # Changed here

        # Then parse individual competency PDFs for detailed descriptions
        for root, _, files in os.walk(pdf_dir):
            for file in files:
                if file.endswith('.pdf') and file != "Competencies.pdf":
                    try:
                        competency_name = os.path.splitext(file)[0].replace('_', ' ')
                        pdf_path = os.path.join(root, file)

                        with open(pdf_path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            text = ""
                            for page in pdf_reader.pages:
                                text += page.extract_text()

                            description_match = re.search(r'Description:(.*?)(?=Situation|$)', text, re.DOTALL)
                            situation_match = re.search(r'Situation Examples:(.*?)(?=Task|$)', text, re.DOTALL)
                            task_match = re.search(r'Task Examples:(.*?)(?=Action|$)', text, re.DOTALL)
                            action_match = re.search(r'Action Examples:(.*?)(?=Result|$)', text, re.DOTALL)
                            result_match = re.search(r'Result Examples:(.*?)(?=$)', text, re.DOTALL)

                            competency_details[competency_name] = {
                                'description': description_match.group(1).strip() if description_match else "",
                                'situation': situation_match.group(1).strip() if situation_match else "",
                                'task': task_match.group(1).strip() if task_match else "",
                                'action': action_match.group(1).strip() if action_match else "",
                                'result': result_match.group(1).strip() if result_match else ""
                            }
                    except Exception as e:
                        print(f"Could not process {file}: {e}")

        if not competencies:
            # return load_apple_competencies_fallback()
            return load_role_competencies_fallback() # Changed here

        return {
            'roles_competencies': dict(competencies),
            'competency_details': competency_details
        }
    except Exception as e:
        # print(f"Error parsing competency PDF: {e}") # Original
        # print("Falling back to official competency data") # Original
        # return load_apple_competencies_fallback() # Original
        print(f"Error parsing competency PDFs: {e}") # Changed to match user's version
        print("Falling back to example competency data.") # Changed to match user's version
        return load_role_competencies_fallback() # Changed here


# def load_apple_competencies_fallback():
def load_role_competencies_fallback(): # Renamed function
    """Fallback function that returns example role competencies if PDF parsing fails."""
    # print("Using official Apple competency data") # Original
    print("Using example role competency data.") # Changed to match user's version
    return {
        'roles_competencies': {
            "Technical Specialist": [
                "Customer Focus",
                "Manages Ambiguity",
                "Tech Savvy",
                "Action Oriented",
                "Manages Conflict",
                "Manages Complexity"
            ],
            "Technical Expert": [
                "Drives Results",
                "Communicates Effectively",
                "Tech Savvy",
                "Decision Quality",
                "Manages Complexity",
                "Collaborates"
            ],
            "Genius": [
                "Being Resilient",
                "Decision Quality",
                "Tech Savvy",
                "Action Oriented",
                "Situational Adaptability",
                "Managing Complexity"
            ],
            "Genius Admin": [
                "Customer Focus",
                "Action Oriented",
                "Resourcefulness",
                "Interpersonal Savvy",
                "Managing Complexity",
                "Communicates Effectively"
            ],
            "Business Expert": [
                "Business Insight",
                "Customer Focus",
                "Drives Results",
                "Action Oriented",
                "Organizational Savvy",
                "Collaborates",
                "Tech Savvy"
            ],
            "Business Pro": [
                "Decision Quality",
                "Communicates Effectively",
                "Plans and Aligns",
                "Collaborates",
                "Persuades",
                "Resourcefulness",
                "Business Insight"
            ],
            "Operations Specialist": [
                "Action Oriented",
                "Manages Ambiguity",
                "Customer Focus",
                "Interpersonal Savvy",
                "Nimble Learning",
                "Plans and Aligns"
            ],
            "Operations Expert": [
                "Decision Quality",
                "Manages Complexity",
                "Drives Results",
                "Resourcefulness",
                "Action Oriented",
                "Interpersonal Savvy"
            ],
            "Ops Lead": [
                "Ensures Accountability",
                "Manages Complexity",
                "Drives Results",
                "Optimizes Work Processes",
                "Manages Ambiguity",
                "Collaborates",
                "Interpersonal Savvy"
            ],
            "Specialist": [
                "Drives Results",
                "Manages Ambiguity",
                "Nimble Learning",
                "Customer Focus",
                "Self Development"
            ],
            "Expert": [
                "Drives Results",
                "Communicates Effectively",
                "Tech Savvy",
                "Decision Quality",
                "Manages Complexity",
                "Collaborates"
            ],
            "Lead": [
                "Manages Complexity",
                "Manages Conflict",
                "Decision Quality",
                "Optimizes Work Processes",
                "Manages Ambiguity",
                "Collaborates",
                "Interpersonal Savvy",
                "Drives Results"
            ],
            "Creative Pro": [
                "Tech Savvy",
                "Collaborates",
                "Drives Results",
                "Communicates Effectively",
                "Decision Quality"
            ],
            "Creative": [
                "Communicates Effectively",
                "Tech Savvy",
                "Action Oriented",
                "Drives Results",
                "Nimble Learning",
                "Interpersonal Savvy"
            ],
            "Lead Genius": [
                "Tech Savvy",
                "Optimizes Work Processes",
                "Manages Conflict",
                "Decision Quality",
                "Collaborates",
                "Interpersonal Savvy"
            ]
        },
        'competency_details': {
            "Customer Focus": {
                "description": "Building strong customer relationships and delivering customer-centric solutions.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Manages Ambiguity": {
                "description": "Operating effectively, even when things are not certain or the way forward is not clear.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Tech Savvy": {
                "description": "Anticipating and adopting innovations in business-building digital and technology applications.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Action Oriented": {
                "description": "Taking on new opportunities and tough challenges with a sense of urgency, high energy, and enthusiasm.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Manages Conflict": {
                "description": "Handling conflict situations effectively, with a minimum of noise.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Manages Complexity": {
                "description": "Making sense of complex, high quantity, and sometimes contradictory information to effectively solve problems.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Drives Results": {
                "description": "Consistently achieving results, even under tough circumstances.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Communicates Effectively": {
                "description": "Developing and delivering multi-mode communications that convey a clear understanding of the unique needs of different audiences.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Decision Quality": {
                "description": "Making good and timely decisions that keep the organization moving forward.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Collaborates": {
                "description": "Building partnerships and working collaboratively with others to meet shared objectives.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Being Resilient": {
                "description": "Rebounding from setbacks and adversity when facing difficult situations.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Situational Adaptability": {
                "description": "Adapting approach and demeanor in real time to match the shifting demands of different situations.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Managing Complexity": {
                "description": "Making sense of complex, high quantity, and sometimes contradictory information to effectively solve problems.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Resourcefulness": {
                "description": "Securing and deploying resources effectively and efficiently.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Interpersonal Savvy": {
                "description": "Relating openly and comfortably with diverse groups of people.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Business Insight": {
                "description": "Applying knowledge of business and the marketplace to advance the organization's goals.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Organizational Savvy": {
                "description": "Maneuvering comfortably through complex policy, process, and people-related organizational dynamics.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Plans and Aligns": {
                "description": "Planning and prioritizing work to meet commitments aligned with organizational goals.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Persuades": {
                "description": "Using compelling arguments to gain the support and commitment of others.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Nimble Learning": {
                "description": "Actively learning through experimentation when tackling new problems, using both successes and failures as learning fodder.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Ensures Accountability": {
                "description": "Holding self and others accountable to meet commitments.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Optimizes Work Processes": {
                "description": "Knowing the most effective and efficient processes to get things done, with a focus on continuous improvement.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            },
            "Self Development": {
                "description": "Actively seeking new ways to grow and be challenged using both formal and informal development channels.",
                "situation": "",
                "task": "",
                "action": "",
                "result": ""
            }
        }
    }

def visualize_competency_data(competency_data):
    """
    Display the extracted competency data in a readable format.
    Useful for debugging and confirming correct PDF parsing.
    """
    print("\n" + "="*50)
    print("EXTRACTED COMPETENCY DATA")
    print("="*50)

    roles_competencies = competency_data['roles_competencies']

    if not roles_competencies:
        print("No roles or competencies were extracted from the PDF!")
        print("Check that the PDF is in the correct location and format.")
        return

    for role, competencies in roles_competencies.items():
        print(f"\nRole: {role}")
        if not competencies:
            print("  No competencies found for this role!")
        else:
            for comp in competencies:
                print(f"  - {comp}")

    # Check competency details
    details = competency_data['competency_details']
    if details:
        print("\nCompetency details extracted:")
        for comp, detail in details.items():
            print(f"  - {comp}: {'Description available' if detail.get('description') else 'No description'}")
    else:
        print("\nNo competency details were extracted.")

    print("\n" + "="*50)

if __name__ == "__main__":
    star_story_builder()