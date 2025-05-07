#!/usr/bin/env python3
"""
Unified STAR Method Coach

A comprehensive program that combines multiple STAR method tools:
1. General STAR Method Coach with scoring and feedback
2. Apple Interview STAR Builder with role-specific competencies
3. Quick STAR Story Builder for simple practice

This program helps users prepare for interviews by crafting effective STAR method stories.
"""

import os
import re
import datetime
from collections import defaultdict
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    class DummyColor:
        RESET = RED = GREEN = YELLOW = CYAN = MAGENTA = BLUE = WHITE = ''
    Fore = Style = DummyColor()


try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("PyPDF2 not installed. PDF functionality will be limited.")
    print("To enable full PDF support, install PyPDF2 with: pip install PyPDF2")


class UnifiedSTARCoach:
    """
    A comprehensive STAR method interview preparation tool that combines:
    1. General STAR Method coaching with scoring and feedback
    2. Apple-specific STAR story building with competency frameworks
    3. Simple STAR story building for quick practice
    """
    
    def __init__(self):
        """Initialize the Unified STAR Coach with all competency frameworks and scoring criteria."""
        # Load competency frameworks
        self.general_competencies = self.load_general_competencies()
        self.apple_competency_data = self.load_apple_competencies()
        
        # Initialize story data
        self.story = {}
        self.current_competency = None
        self.current_role = None
        
        # Scoring criteria from star_method_coach.py
        self.scoring_criteria = {
            "Talented": {
                "description": "Exceptional demonstration of the competency, going beyond expectations",
                "criteria": [
                    "Provides specific, detailed examples with measurable outcomes",
                    "Shows initiative and leadership beyond the immediate task",
                    "Demonstrates complex problem-solving and creative thinking",
                    "Exhibits high impact results that benefited multiple stakeholders",
                    "Shows clear personal ownership and accountability"
                ]
            },
            "Skilled": {
                "description": "Effective demonstration of the competency, meeting expectations",
                "criteria": [
                    "Provides clear examples with concrete outcomes",
                    "Shows appropriate action steps relevant to the situation",
                    "Demonstrates logical problem-solving approach",
                    "Exhibits positive results that achieved objectives",
                    "Shows personal contribution to the outcome"
                ]
            },
            "Unskilled": {
                "description": "Limited demonstration of the competency, below expectations",
                "criteria": [
                    "Provides vague or generic examples without specifics",
                    "Shows minimal action or reactive rather than proactive approach",
                    "Demonstrates limited problem-solving or decision making",
                    "Exhibits unclear or minimal results",
                    "Shows little personal responsibility or ownership"
                ]
            },
            "Overused": {
                "description": "Excessive or inappropriate application of the competency",
                "criteria": [
                    "Demonstrates overkill or disproportionate response to the situation",
                    "Shows rigid adherence to a strength that became counterproductive",
                    "Exhibits tunnel vision or ignoring of other important factors",
                    "Demonstrates perfectionism or micromanagement",
                    "Shows inability to adapt approach when needed"
                ]
            }
        }
    
    def load_general_competencies(self):
        """Load general competencies and associated interview questions from star_method_coach.py."""
        return {
            "Action Oriented": {
                "description": "Taking on new opportunities and tough challenges with a sense of urgency, high energy, and enthusiasm.",
                "questions": [
                    "Explain what you did when faced with a difficult and urgent problem.",
                    "Tell me about a time you had to take over someone else's challenging project.",
                    "Tell me about a situation that required an enormous amount of energy and effort.",
                    "Describe a time you seized an opportunity and moved forward with purpose.",
                    "Tell me about a time you were the first person to take action on something."
                ],
                "skilled_signs": [
                    "Readily takes action on challenges, without unnecessary planning",
                    "Identifies and seizes new opportunities",
                    "Displays a can-do attitude in good and bad times",
                    "Steps up to handle tough issues"
                ],
                "unskilled_signs": [
                    "Is slow to act on an opportunity",
                    "Spends too much time planning and looking for information",
                    "May be overly methodical, taking too long to act on a problem",
                    "Is reluctant to step up to challenges; waits for someone else to take action"
                ]
            },
            "Being Resilient": {
                "description": "Rebounding from setbacks and adversity when facing difficult situations.",
                "questions": [
                    "Describe a crisis you had to handle.",
                    "Give me an example of how you managed an emergency situation.",
                    "Tell me about a time when you felt under extreme pressure but managed to carry on.",
                    "Tell me about a time when a project or initiative seemed like it was going nowhere.",
                    "Tell me about a time when someone or something caught you by surprise and caused you to be blocked."
                ],
                "skilled_signs": [
                    "Is confident under pressure",
                    "Handles and manages crises effectively",
                    "Maintains a positive attitude despite adversity",
                    "Bounces back from setbacks",
                    "Grows from hardships and negative experiences"
                ],
                "unskilled_signs": [
                    "Gets easily rattled in high-pressure situations",
                    "Exhibits low energy and motivation during times of stress and worry",
                    "Acts defensively when faced with criticism or roadblocks",
                    "Takes too long to recover from setbacks"
                ]
            },
            "Collaborates": {
                "description": "Building partnerships and working collaboratively with others to meet shared objectives.",
                "questions": [
                    "Tell me about a time when you built strong relationships where none previously existed.",
                    "Describe a time you had to build partnerships to achieve a shared objective.",
                    "Tell me about a successful experience you had implementing something across organizational boundaries.",
                    "Describe a time when a team or group did not get their share of credit.",
                    "Tell me about a time you succeeded in an initiative by collaborating with others."
                ],
                "skilled_signs": [
                    "Works cooperatively with others across the organization to achieve shared objectives",
                    "Represents own interests while being fair to others and their areas",
                    "Partners with others to get work done and recognizes their contributions",
                    "Gains trust and support of others"
                ],
                "unskilled_signs": [
                    "Overlooks opportunities to work collaboratively with others",
                    "Puts own interests above others'",
                    "Shuts down lines of communication across groups",
                    "Prefers to work alone and be accountable only for individual contributions"
                ]
            },
            "Communicates Effectively": {
                "description": "Developing and delivering multi-mode communications that convey a clear understanding of the unique needs of different audiences.",
                "questions": [
                    "Tell me about a time when you had to explain something important to someone who did not understand your industry or function's language or work.",
                    "Describe the best presentation you've ever given.",
                    "Tell me about a time when others were missing the key points in a discussion and you helped get things back on track.",
                    "Tell me about a time you had to shut off a person in the middle of a meeting or who was talking too much or interrupting.",
                    "Describe a time you had to convey the same message through different methods of communication."
                ],
                "skilled_signs": [
                    "Is effective in a variety of communication settings",
                    "Attentively listens to others",
                    "Adjusts to fit the audience and the message",
                    "Provides timely and helpful information to others",
                    "Encourages the open expression of diverse ideas and opinions"
                ],
                "unskilled_signs": [
                    "Has difficulty communicating clear written and verbal messages",
                    "Tends to always communicate the same way without adjusting to diverse audiences",
                    "Doesn't take the time to listen or understand others' viewpoints",
                    "Doesn't consistently share information others need to do their jobs"
                ]
            },
            "Customer Focus": {
                "description": "Building strong customer relationships and delivering customer-centric solutions.",
                "questions": [
                    "Describe a time you obtained up-to-date information from a customer, and what you did with it.",
                    "Tell me about a time when you went the extra mile for a challenging customer.",
                    "Tell me about a time you were confronted with an internal or external customer problem.",
                    "Tell me about a time when you almost lost a customer and had to win them back.",
                    "Tell me about a time when you changed your approach to better meet a customer's needs."
                ],
                "skilled_signs": [
                    "Gains insight into customer needs",
                    "Identifies opportunities that benefit both the customer and the organization",
                    "Builds and delivers solutions that meet customer expectations",
                    "Establishes and maintains effective customer relationships"
                ],
                "unskilled_signs": [
                    "Thinks they already know what the customer needs",
                    "Doesn't consider customer feedback important",
                    "Doesn't dedicate enough time to building relationships with customers",
                    "Focuses on internal activities instead of the customer"
                ]
            },
            "Decision Quality": {
                "description": "Making good and timely decisions that keep the organization moving forward.",
                "questions": [
                    "Describe a time you had to make a quick decision and gather a lot of information in a short time frame.",
                    "Give me an example of a difficult problem you worked on and walk me through your decision-making process.",
                    "Describe a time when you made a major decision and were really pleased with the outcome.",
                    "Tell me about a quick decision you made that turned out to be a good one.",
                    "Describe a time when you received useful feedback on a decision you made."
                ],
                "skilled_signs": [
                    "Makes sound decisions, even in the absence of complete information",
                    "Relies on experience, analysis, and judgment when making decisions",
                    "Considers all relevant factors and uses appropriate decision-making criteria",
                    "Recognizes when a quick 80% solution will suffice"
                ],
                "unskilled_signs": [
                    "Approaches decisions haphazardly or delays decision making",
                    "Makes decisions based on incomplete data or inaccurate assumptions",
                    "Ignores different points of view",
                    "Makes decisions that impact short-term results at the expense of longer-term goals"
                ]
            },
            "Drives Results": {
                "description": "Consistently achieving results, even under tough circumstances.",
                "questions": [
                    "Describe a time you championed a cause that others had abandoned.",
                    "Tell me about a time you got results that far exceeded your own expectations.",
                    "Tell me about a time you got results even though some major factor changed, such as a budget cut.",
                    "Describe a time when you drove yourself harder than you were driving others.",
                    "Talk about a time you were assigned to a fix-it or turnaround project."
                ],
                "skilled_signs": [
                    "Has a strong bottom-line orientation",
                    "Persists in accomplishing objectives despite obstacles and setbacks",
                    "Has a track record of exceeding goals successfully",
                    "Pushes self and helps others achieve results"
                ],
                "unskilled_signs": [
                    "Is reluctant to push for results",
                    "Does the least to get by",
                    "Is an inconsistent performer",
                    "Gives up easily",
                    "Often misses deadlines"
                ]
            },
            "Strategic Mindset": {
                "description": "Seeing ahead to future possibilities and translating them into breakthrough strategies.",
                "questions": [
                    "Give me an example of working with a team and creating a new vision and strategy.",
                    "Give me an example of exploring various scenarios and possibilities when charting a course for the future.",
                    "Tell me about a time when your strategic vision or big-picture thinking was an asset.",
                    "Tell me about a time you were implementing a strategy and had to revise it mid-process due to changes in the environment.",
                    "Describe a time you had to develop a strategy that would create value for your organization or customers."
                ],
                "skilled_signs": [
                    "Anticipates future trends and implications accurately",
                    "Readily poses future scenarios",
                    "Articulates credible pictures and visions of possibilities",
                    "Creates competitive and breakthrough strategies"
                ],
                "unskilled_signs": [
                    "Is more comfortable in the tactical here and now",
                    "Spends little time thinking about strategic issues",
                    "Contributes little to strategic discussions",
                    "Lacks the disciplined thought processes to develop a coherent view"
                ]
            }
        }
    # End of load_general_competencies

    def load_apple_competencies(self):
        """Load Apple's competencies for different roles."""
        # Try to load from PDFs if PyPDF2 is available
        if PDF_SUPPORT:
            try:
                return self.load_apple_competencies_from_pdfs()
            except Exception as e:
                print(f"Error loading Apple competencies from PDFs: {e}")
                print("Falling back to built-in competency data")
        
        # Fallback to built-in data
        return self.load_apple_competencies_fallback()
    
    def load_apple_competencies_from_pdfs(self):
        """
        Load Apple's competencies from PDF files in the directory.
        Returns a dictionary mapping roles to their competencies and descriptions.
        """
        competencies = defaultdict(list)
        competency_details = {}
        
        # Path to directory containing PDFs
        pdf_dir = os.path.dirname(os.path.abspath(__file__))
        
        # First, try to parse the Roles/Competencies.pdf for role mappings
        roles_pdf_path = os.path.join(pdf_dir, "Roles:Competencies.pdf")
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
            except Exception as e:
                print(f"Error parsing roles PDF: {e}")
        
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
                            
                            # Extract description, situation examples, etc.
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
        
        # If we didn't find any roles or competencies, fall back to hardcoded values
        if not competencies:
            return self.load_apple_competencies_fallback()
        
        return {
            'roles_competencies': dict(competencies),
            'competency_details': competency_details
        }
    
    def load_apple_competencies_fallback(self):
        """Fallback function that returns accurate Apple competencies if PDF parsing fails."""
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
                ]
            },
            'competency_details': {
                "Customer Focus": {
                    "description": "Building strong customer relationships and delivering customer-centric solutions.",
                    "situation": "Look for situations where you identified customer needs or addressed customer issues.",
                    "task": "Focus on tasks where you were responsible for improving customer experience or satisfaction.",
                    "action": "Highlight actions that demonstrate how you listened to customers and tailored solutions.",
                    "result": "Emphasize measurable improvements in customer satisfaction, retention, or feedback."
                },
                "Tech Savvy": {
                    "description": "Anticipating and adopting innovations in business-building digital and technology applications.",
                    "situation": "Describe situations requiring technical innovation or digital solutions.",
                    "task": "Explain your responsibility to implement or leverage technology effectively.",
                    "action": "Detail how you researched, learned, or applied new technologies.",
                    "result": "Quantify the impact of your technical solution on efficiency, performance, or user experience."
                },
                "Technical Problem Solving": {
                    "description": "Applying analytical thinking to break down complex technical problems and develop effective solutions.",
                    "situation": "Describe complex technical challenges you faced.",
                    "task": "Explain the technical requirements and constraints you needed to work within.",
                    "action": "Detail your systematic approach to analyzing and solving the problem.",
                    "result": "Quantify improvements in performance, reliability, or other technical metrics."
                },
                "Innovation": {
                    "description": "Developing breakthrough ideas and implementing them to create value.",
                    "situation": "Describe situations requiring creative thinking or novel approaches.",
                    "task": "Explain why conventional solutions wouldn't work for your task.",
                    "action": "Detail your creative process and how you developed your innovative solution.",
                    "result": "Highlight how your innovation created value or solved problems in new ways."
                }
            }
        }
    
    def run(self):
        """Main execution method for the Unified STAR Coach."""
        self.print_welcome_message()
        while True:
            print("\n" + "="*80)
            print("What would you like to do?")
            print("1. General STAR Method Coach (with scoring and feedback)")
            print("2. Apple Interview STAR Builder (role-specific competencies)")
            print("3. Quick STAR Story Builder (simple practice)")
            print("4. Review a saved STAR story")
            print("5. Load and display a saved STAR story")
            print("6. Exit")
            choice = input("\nEnter your choice (1-6): ")
            if choice == '1':
                self.run_general_coach()
            elif choice == '2':
                self.run_apple_coach()
            elif choice == '3':
                self.run_quick_builder()
            elif choice == '4':
                self.review_saved_stories()
            elif choice == '5':
                self.load_story()
            elif choice == '6':
                print("\nThank you for using the Unified STAR Method Coach. Good luck with your interviews!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def print_welcome_message(self):
        """Display the welcome message and introduction to the STAR Method with color formatting."""
        print("\n" + Fore.CYAN + "="*80 + Style.RESET_ALL)
        print(Fore.GREEN + "Welcome to the Unified STAR Method Interview Coach!" + Style.RESET_ALL)
        print("This program combines multiple STAR method tools to help you prepare for interviews.")
        print("\nThe STAR Method stands for:")
        print(Fore.YELLOW + "S - Situation:" + Style.RESET_ALL + " Set the scene and provide context.")
        print(Fore.YELLOW + "T - Task:" + Style.RESET_ALL + " Explain your responsibility or challenge.")
        print(Fore.YELLOW + "A - Action:" + Style.RESET_ALL + " Detail the specific steps you took.")
        print(Fore.YELLOW + "R - Result:" + Style.RESET_ALL + " Share the outcomes of your actions and what you learned.")
    
    #
    # General STAR Method Coach (from star_method_coach.py)
    #
    def run_general_coach(self):
        """Run the general STAR method coach with scoring and feedback."""
        print("\n" + "="*80)
        print("GENERAL STAR METHOD COACH")
        print("This mode helps you craft and score interview stories based on competencies.")
        
        while True:
            print("\n" + "="*60)
            print("What would you like to do?")
            print("1. Select a competency and interview question")
            print("2. Craft a STAR story")
            print("3. Review and score an existing story")
            print("4. Return to main menu")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                self.select_competency_and_question()
            elif choice == '2':
                self.craft_star_story()
            elif choice == '3':
                self.review_and_score_story()
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def select_competency_and_question(self):
        """Guide the user to select a competency and related interview question, with back/exit options."""
        print("\n" + "="*60)
        print("STEP 1: SELECT A COMPETENCY AND INTERVIEW QUESTION")
        print("\nAvailable competencies:")
        competency_list = list(self.general_competencies.keys())
        for i, competency in enumerate(competency_list, 1):
            print(f"{i}. {competency}: {self.general_competencies[competency]['description']}")
        while True:
            user_input = input("\nSelect a competency (enter number, or type 'back' or 'exit'): ").strip().lower()
            if user_input == 'exit':
                exit()
            if user_input == 'back':
                return
            try:
                comp_idx = int(user_input) - 1
                if 0 <= comp_idx < len(competency_list):
                    self.current_competency = competency_list[comp_idx]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(competency_list)}.")
            except ValueError:
                print("Please enter a valid number, 'back', or 'exit'.")
        print(f"\nInterview questions for '{self.current_competency}':")
        questions = self.general_competencies[self.current_competency]['questions']
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")
        print("\nSelect an interview question from the list above, or enter '0' to provide your own:")
        while True:
            user_input = input("Enter your choice (number, 'back', or 'exit'): ").strip().lower()
            if user_input == 'exit':
                exit()
            if user_input == 'back':
                return self.select_competency_and_question()
            try:
                q_idx = int(user_input)
                if 1 <= q_idx <= len(questions):
                    self.story['question'] = questions[q_idx - 1]
                    break
                elif q_idx == 0:
                    custom_q = input("Enter your custom interview question (or type 'back' or 'exit'): ").strip()
                    if custom_q.lower() == 'exit':
                        exit()
                    if custom_q.lower() == 'back':
                        continue
                    self.story['question'] = custom_q
                    break
                else:
                    print(f"Please enter a number between 0 and {len(questions)}.")
            except ValueError:
                print("Please enter a valid number, 'back', or 'exit'.")
        # Store the selected competency
        self.story['competency'] = self.current_competency
        print(f"\nYou've selected: {self.story['competency']}")
        print(f"Interview Question: {self.story['question']}")
        # Offer to show an example STAR story
        show_example = input("Would you like to see an example STAR story for this competency? (yes/no): ").strip().lower()
        if show_example in ['yes', 'y']:
            self.display_example_star_story(self.current_competency)
        print("Now you're ready to craft your STAR story!")

    def run_apple_coach(self):
        """Run the Apple Interview STAR Builder (role-specific competencies)."""
        print("\n" + "="*80)
        print("APPLE INTERVIEW STAR BUILDER")
        print("This mode helps you craft STAR stories for Apple interviews using role-specific competencies.")
        roles = list(self.apple_competency_data['roles_competencies'].keys())
        if not roles:
            print("No Apple roles found. Please check your competency data.")
            return
        print("\nAvailable Apple roles:")
        for i, role in enumerate(roles, 1):
            print(f"{i}. {role}")
        while True:
            try:
                role_idx = int(input("\nSelect a role (enter number): ")) - 1
                if 0 <= role_idx < len(roles):
                    self.current_role = roles[role_idx]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(roles)}.")
            except ValueError:
                print("Please enter a valid number.")
        competencies = self.apple_competency_data['roles_competencies'][self.current_role]
        print(f"\nCompetencies for '{self.current_role}':")
        for i, comp in enumerate(competencies, 1):
            print(f"{i}. {comp}")
        while True:
            try:
                comp_idx = int(input("\nSelect a competency (enter number): ")) - 1
                if 0 <= comp_idx < len(competencies):
                    self.current_competency = competencies[comp_idx]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(competencies)}.")
            except ValueError:
                print("Please enter a valid number.")
        details = self.apple_competency_data.get('competency_details', {}).get(self.current_competency, {})
        print(f"\nSelected Competency: {self.current_competency}")
        if details:
            print(f"Description: {details.get('description', 'No description available.')}")
            print(f"Situation: {details.get('situation', 'N/A')}")
            print(f"Task: {details.get('task', 'N/A')}")
            print(f"Action: {details.get('action', 'N/A')}")
            print(f"Result: {details.get('result', 'N/A')}")
        else:
            print("No detailed information available for this competency.")
        print("\nNow you're ready to craft your STAR story for this Apple role and competency!")
        # Set up the story dict for Apple context and launch STAR crafting
        self.story = {
            'competency': self.current_competency,
            'question': f"Apple Interview: {self.current_competency} ({self.current_role})",
        }
        self.craft_star_story()

    def run_quick_builder(self):
        """Run the Quick STAR Story Builder for simple practice."""
        print("\n" + "="*80)
        print("QUICK STAR STORY BUILDER")
        print("This mode lets you quickly practice crafting a STAR story.")
        print("\nPlease enter your STAR story below:")
        situation = input("Situation: ")
        task = input("Task: ")
        action = input("Action: ")
        result = input("Result: ")
        print("\nYour STAR Story:")
        print(f"Situation: {situation}")
        print(f"Task: {task}")
        print(f"Action: {action}")
        print(f"Result: {result}")
        print("\nGreat job! Keep practicing to improve your STAR stories.")

    def save_story(self, story=None):
        """Save the current or provided STAR story as a JSON file in the Stories directory."""
        import json
        from pathlib import Path
        if story is None:
            story = self.story
        if not story or not all([story.get('situation'), story.get('task'), story.get('action'), story.get('result'), story.get('competency'), story.get('question')]):
            print("\nCannot save an incomplete story.")
            return
        story['timestamp'] = datetime.datetime.now().isoformat()
        save_dir = Path("Stories")
        save_dir.mkdir(exist_ok=True)
        safe_question = "_".join(story['question'].split()).replace("?", "")
        safe_comp = "_".join(story['competency'].split())
        filename = save_dir / f"{safe_question}_{safe_comp}.json"
        # If JSON exists, load list; else start new
        if filename.exists():
            try:
                with filename.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if not isinstance(data, list):
                    data = [data]
            except json.JSONDecodeError:
                data = []
        else:
            data = []
        data.append(story)
        with filename.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        print(f"\nStory saved to {filename}")

    def list_saved_stories(self):
        """List all saved STAR stories in the Stories directory."""
        from pathlib import Path
        save_dir = Path("Stories")
        if not save_dir.exists():
            print("No saved stories found.")
            return []
        files = list(save_dir.glob("*.json"))
        if not files:
            print("No saved stories found.")
            return []
        print("\nSaved STAR Stories:")
        for idx, file in enumerate(files, 1):
            print(f"{idx}. {file.name}")
        return files

    def load_story(self):
        """Load and display a saved STAR story."""
        files = self.list_saved_stories()
        if not files:
            return
        try:
            idx = int(input("\nEnter the number of the story to load: ")) - 1
            if 0 <= idx < len(files):
                import json
                with open(files[idx], "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                # Show the most recent story in the file
                story = data[-1] if isinstance(data, list) else data
                print("\nLoaded STAR Story:")
                for k, v in story.items():
                    print(f"{k.capitalize()}: {v}")
            else:
                print("Invalid selection.")
        except Exception as e:
            print(f"Error loading story: {e}")

    def review_saved_stories(self):
        """Review and score a saved STAR story."""
        files = self.list_saved_stories()
        if not files:
            return
        try:
            idx = int(input("\nEnter the number of the story to review: ")) - 1
            if 0 <= idx < len(files):
                import json
                with open(files[idx], "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                story = data[-1] if isinstance(data, list) else data
                self.story = story
                self.score_story()
            else:
                print("Invalid selection.")
        except Exception as e:
            print(f"Error reviewing story: {e}")

    def score_story(self):
        """Score the STAR story based on competency criteria and provide actionable feedback."""
        story = self.story
        if not story or not all([story.get('situation'), story.get('task'), story.get('action'), story.get('result'), story.get('competency')]):
            print("\nCannot score an incomplete story.")
            return
        print("\n" + "="*80)
        print("STORY ASSESSMENT")
        competency = story['competency']
        situation_length = len(story['situation'].split())
        action_length = len(story['action'].split())
        result_length = len(story['result'].split())
        has_quantifiable_results = any(char.isdigit() for char in story['result'])
        personal_action = ('i ' in story['action'].lower() or 'my ' in story['action'].lower() or 'me ' in story['action'].lower())
        skilled_signs = self.general_competencies[competency]['skilled_signs']
        unskilled_signs = self.general_competencies[competency]['unskilled_signs']
        skilled_alignment = sum(1 for sign in skilled_signs if any(word in story['action'].lower() or word in story['result'].lower() for word in sign.lower().split()))
        unskilled_alignment = sum(1 for sign in unskilled_signs if any(word in story['action'].lower() or word in story['result'].lower() for word in sign.lower().split()))
        score = "Skilled"
        if situation_length < 20 or action_length < 30 or result_length < 20:
            score = "Unskilled"
        elif not personal_action:
            score = "Unskilled"
        elif not has_quantifiable_results:
            score = "Skilled"
        elif action_length > 200 and result_length < 50:
            score = "Overused"
        elif skilled_alignment > 2 and has_quantifiable_results and personal_action and action_length > 50:
            score = "Talented"
        elif unskilled_alignment > 2:
            score = "Unskilled"
        story['score'] = score
        print(f"\nSCORE: {score}")
        print(f"\nScore Description: {self.scoring_criteria[score]['description']}")
        self.provide_feedback(score)
        save_choice = input("\nWould you like to save this story? (yes/no): ").lower()
        if save_choice in ['yes', 'y']:
            self.save_story(story)

    def provide_feedback(self, score):
        story = self.story
        competency = story['competency']
        situation_length = len(story['situation'].split())
        task_length = len(story['task'].split())
        action_length = len(story['action'].split())
        result_length = len(story['result'].split())
        has_quantifiable_results = any(char.isdigit() for char in story['result'])
        personal_action = ('i ' in story['action'].lower() or 'my ' in story['action'].lower() or 'me ' in story['action'].lower())
        # Color feedback header
        print(Fore.GREEN + "\nFEEDBACK:" + Style.RESET_ALL)
        if score == "Talented":
            print(Fore.YELLOW + "Your story demonstrates excellent mastery of this competency. It's detailed, focused, and shows significant impact." + Style.RESET_ALL)
        elif score == "Skilled":
            print(Fore.YELLOW + "Your story effectively demonstrates this competency. It provides a clear example with appropriate detail and positive outcomes." + Style.RESET_ALL)
        elif score == "Unskilled":
            print(Fore.RED + "Your story needs improvement to effectively demonstrate this competency. It lacks some key elements that would make it more convincing." + Style.RESET_ALL)
        elif score == "Overused":
            print(Fore.MAGENTA + "Your story shows an overemphasis on certain aspects of the competency, potentially at the expense of balance and effectiveness." + Style.RESET_ALL)
        print(Fore.BLUE + "\nSpecific suggestions for improvement:" + Style.RESET_ALL)
        if situation_length < 20:
            print(Fore.YELLOW + "- Add more context to your situation to set the stage more effectively." + Style.RESET_ALL)
        if task_length < 20:
            print(Fore.YELLOW + "- Clarify your specific responsibility or challenge in more detail." + Style.RESET_ALL)
        if not personal_action:
            print(Fore.YELLOW + "- Focus more on YOUR actions by using 'I' statements rather than 'we' or passive voice." + Style.RESET_ALL)
        if action_length < 50:
            print(Fore.YELLOW + "- Provide more specific details about the steps you took and your decision-making process." + Style.RESET_ALL)
        if result_length < 20:
            print(Fore.YELLOW + "- Expand on the outcomes and impact of your actions." + Style.RESET_ALL)
        if not has_quantifiable_results:
            print(Fore.YELLOW + "- Include specific numbers or metrics to quantify your results (%, $, time saved, etc.)." + Style.RESET_ALL)
        if action_length > 200 and result_length < 50:
            print(Fore.YELLOW + "- Balance your story by focusing more on results and less on listing every action step." + Style.RESET_ALL)
        print(Fore.CYAN + f"\nCompetency-specific feedback for '{competency}':" + Style.RESET_ALL)
        if score in ["Unskilled", "Overused"]:
            print(Fore.YELLOW + "Consider incorporating these elements that demonstrate skill in this competency:" + Style.RESET_ALL)
            for sign in self.general_competencies[competency]['skilled_signs'][:2]:
                print(Fore.YELLOW + f"- {sign}" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "To further strengthen your story for this competency, consider:" + Style.RESET_ALL)
            if competency == "Action Oriented":
                print("- Emphasizing how quickly you took initiative without excessive planning")
                print("- Highlighting your eagerness to tackle challenges head-on")
            elif competency == "Being Resilient":
                print("- Focusing more on how you maintained composure under pressure")
                print("- Emphasizing what you learned from overcoming adversity")
            elif competency == "Collaborates":
                print("- Detailing how you balanced your interests with those of others")
                print("- Explaining how you recognized others' contributions")
            elif competency == "Communicates Effectively":
                print("- Highlighting how you adapted your communication style to different audiences")
                print("- Showing how you ensured your message was clearly understood")
            elif competency == "Customer Focus":
                print("- Emphasizing how you gained insight into customer needs")
                print("- Detailing how you built a strong customer relationship")
            elif competency == "Decision Quality":
                print("- Highlighting the factors you considered in your decision-making process")
                print("- Showing how you made decisions with incomplete information")
            elif competency == "Drives Results":
                print("- Emphasizing your persistence despite obstacles")
                print("- Highlighting how you exceeded expectations or goals")
            elif competency == "Strategic Mindset":
                print("- Emphasizing how you anticipated future trends or implications")
                print("- Showing how your approach aligned with broader objectives")

    def craft_star_story(self):
        """Guide the user through crafting a STAR method story with navigation options and detailed tips, with color formatting."""
        if not self.story or not self.story.get('competency') or not self.story.get('question'):
            print("\nPlease select a competency and interview question first.")
            return
        competency = self.story['competency']
        print("\n" + Fore.CYAN + "="*80 + Style.RESET_ALL)
        print(Fore.GREEN + "STEP 2: CRAFT YOUR STAR STORY" + Style.RESET_ALL)
        print(f"\nCompetency: {Fore.YELLOW}{competency}{Style.RESET_ALL}")
        print(f"Question: {Fore.YELLOW}{self.story['question']}{Style.RESET_ALL}")
        # Situation
        print("\n" + Fore.CYAN + "="*40 + Style.RESET_ALL)
        print(Fore.MAGENTA + "S - SITUATION: Set the scene and provide context" + Style.RESET_ALL)
        print(Fore.BLUE + "Tips:" + Style.RESET_ALL)
        for tip in self.get_star_section_tips('situation', competency):
            print(Fore.YELLOW + f"- {tip}" + Style.RESET_ALL)
        print("- Describe the specific context/background")
        print("- Explain when and where this happened")
        print("- Identify key stakeholders involved")
        print("- Be concise yet detailed enough to set the stage")
        while True:
            s = input(Fore.CYAN + "\nDescribe the Situation (or type 'back' or 'exit'):\n" + Style.RESET_ALL).strip()
            if s.lower() == 'exit':
                exit()
            if s.lower() == 'back':
                return
            if s:
                self.story['situation'] = s
                break
        # Task
        print("\n" + Fore.CYAN + "="*40 + Style.RESET_ALL)
        print(Fore.MAGENTA + "T - TASK: Explain your responsibility or challenge" + Style.RESET_ALL)
        print(Fore.BLUE + "Tips:" + Style.RESET_ALL)
        for tip in self.get_star_section_tips('task', competency):
            print(Fore.YELLOW + f"- {tip}" + Style.RESET_ALL)
        print("- Clarify your specific role or responsibility")
        print("- Explain what you were trying to accomplish")
        print("- Highlight challenges or constraints you faced")
        print("- Focus on YOUR task, not the team's general task")
        while True:
            t = input(Fore.CYAN + "\nDescribe the Task (or type 'back' or 'exit'):\n" + Style.RESET_ALL).strip()
            if t.lower() == 'exit':
                exit()
            if t.lower() == 'back':
                return self.craft_star_story()
            if t:
                self.story['task'] = t
                break
        # Action
        print("\n" + Fore.CYAN + "="*40 + Style.RESET_ALL)
        print(Fore.MAGENTA + "A - ACTION: Detail the specific steps you took" + Style.RESET_ALL)
        print(Fore.BLUE + "Tips:" + Style.RESET_ALL)
        for tip in self.get_star_section_tips('action', competency):
            print(Fore.YELLOW + f"- {tip}" + Style.RESET_ALL)
        print("- Focus on YOUR actions (use 'I' statements)")
        print("- Be specific about the steps you took")
        print("- Explain your thought process and decisions")
        print("- Highlight skills relevant to the competency")
        print("- Describe how you overcame obstacles")
        while True:
            a = input(Fore.CYAN + "\nDescribe the Action (or type 'back' or 'exit'):\n" + Style.RESET_ALL).strip()
            if a.lower() == 'exit':
                exit()
            if a.lower() == 'back':
                return self.craft_star_story()
            if a:
                self.story['action'] = a
                break
        # Result
        print("\n" + Fore.CYAN + "="*40 + Style.RESET_ALL)
        print(Fore.MAGENTA + "R - RESULT: Share the outcomes of your actions" + Style.RESET_ALL)
        print(Fore.BLUE + "Tips:" + Style.RESET_ALL)
        for tip in self.get_star_section_tips('result', competency):
            print(Fore.YELLOW + f"- {tip}" + Style.RESET_ALL)
        print("- Quantify results whenever possible (%, $, time saved)")
        print("- Describe the impact on the organization/team/customers")
        print("- Include what you learned from the experience")
        print("- Connect the outcome back to the original situation/task")
        while True:
            r = input(Fore.CYAN + "\nDescribe the Result (or type 'back' or 'exit'):\n" + Style.RESET_ALL).strip()
            if r.lower() == 'exit':
                exit()
            if r.lower() == 'back':
                return self.craft_star_story()
            if r:
                self.story['result'] = r
                break
        # Story refinement option
        print("\n" + Fore.CYAN + "="*40 + Style.RESET_ALL)
        print(Fore.GREEN + "Would you like to refine any part of your story?" + Style.RESET_ALL)
        while True:
            refine_choice = input(Fore.CYAN + "Enter the part to refine (situation, task, action, result) or 'done' to continue: " + Style.RESET_ALL).lower()
            if refine_choice == 'done':
                break
            elif refine_choice in ['situation', 'task', 'action', 'result']:
                print(f"\nCurrent {refine_choice.capitalize()}:\n{self.story[refine_choice]}")
                updated = input(Fore.CYAN + f"\nUpdated {refine_choice.capitalize()} (or type 'back' or 'exit'):\n" + Style.RESET_ALL).strip()
                if updated.lower() == 'exit':
                    exit()
                if updated.lower() == 'back':
                    continue
                self.story[refine_choice] = updated
            else:
                print("Invalid input. Please enter 'situation', 'task', 'action', 'result', or 'done'.")
        self.display_story()
        self.score_story()

    def get_example_star_story(self, competency):
        """Return an example STAR story for the given competency, if available."""
        examples = {
            "Drives Results": {
                "question": "Tell me about a time you got results that far exceeded your own expectations.",
                "situation": "Last quarter, our team was struggling to meet our sales targets due to a sudden market downturn.",
                "task": "As the team lead, I was responsible for motivating the team and finding new ways to generate leads despite the challenging environment.",
                "action": "I organized daily stand-ups to share quick wins, introduced a new lead-tracking system, and personally coached team members on outreach techniques.",
                "result": "Within six weeks, our team exceeded the revised target by 30%, and two team members received company awards for their performance."
            },
            "Customer Focus": {
                "question": "Tell me about a time you went the extra mile for a challenging customer.",
                "situation": "A long-term client was unhappy with a recent product update and threatened to switch to a competitor.",
                "task": "I needed to address their concerns, restore their confidence, and retain their business.",
                "action": "I scheduled a face-to-face meeting, listened to their feedback, and worked with our product team to implement a custom solution.",
                "result": "The client renewed their contract for another year and provided a positive testimonial that helped us win new business."
            },
            "Action Oriented": {
                "question": "Tell me about a time you were the first person to take action on something.",
                "situation": "Our project was delayed because no one wanted to take the lead on a critical task.",
                "task": "I decided to step up and coordinate the team to get things moving.",
                "action": "I quickly organized a kickoff meeting, delegated tasks, and set clear deadlines.",
                "result": "The project was back on track within a week and delivered ahead of schedule."
            },
            "Being Resilient": {
                "question": "Tell me about a time when you felt under extreme pressure but managed to carry on.",
                "situation": "During a major system outage, I was responsible for restoring service under tight time constraints.",
                "task": "I had to troubleshoot the issue while keeping stakeholders informed and calm.",
                "action": "I methodically diagnosed the problem, communicated updates, and coordinated with the IT team.",
                "result": "Service was restored within two hours, and I received recognition for my composure and leadership."
            },
            "Collaborates": {
                "question": "Describe a time you had to build partnerships to achieve a shared objective.",
                "situation": "Our department needed to launch a new product, but we lacked marketing expertise.",
                "task": "I was tasked with building a cross-functional team to ensure a successful launch.",
                "action": "I reached out to the marketing team, set up regular meetings, and encouraged open communication.",
                "result": "The product launch exceeded sales targets, and both teams received positive feedback from leadership."
            },
            "Communicates Effectively": {
                "question": "Tell me about a time when you had to explain something important to someone who did not understand your industry or function's language or work.",
                "situation": "I had to present a technical solution to a group of non-technical stakeholders.",
                "task": "My goal was to ensure everyone understood the benefits and risks of the proposed solution.",
                "action": "I used simple analogies, visual aids, and encouraged questions throughout the presentation.",
                "result": "The stakeholders approved the solution, and the project moved forward smoothly."
            },
            "Decision Quality": {
                "question": "Describe a time you had to make a quick decision and gather a lot of information in a short time frame.",
                "situation": "A key supplier suddenly went out of business, threatening our production schedule.",
                "task": "I needed to find an alternative supplier quickly to avoid delays.",
                "action": "I gathered information from multiple vendors, evaluated their capabilities, and negotiated terms.",
                "result": "We secured a new supplier within 48 hours, and production continued without interruption."
            },
            "Strategic Mindset": {
                "question": "Give me an example of working with a team and creating a new vision and strategy.",
                "situation": "Our company was facing increased competition and declining market share.",
                "task": "I was part of a task force to develop a new growth strategy.",
                "action": "We analyzed market trends, identified new opportunities, and created a three-year strategic plan.",
                "result": "The new strategy led to a 20% increase in market share over two years."
            }
        }
        return examples.get(competency)

    def display_example_star_story(self, competency):
        """Display an example STAR story for the selected competency, if available."""
        example = self.get_example_star_story(competency)
        if example:
            print("\nExample STAR Story:")
            print(f"Question: {example['question']}")
            print(f"SITUATION: {example['situation']}")
            print(f"TASK: {example['task']}")
            print(f"ACTION: {example['action']}")
            print(f"RESULT: {example['result']}")
        else:
            print("\nNo example STAR story available for this competency yet.")

    def get_star_section_tips(self, section, competency):
        """Return detailed, competency-specific tips for each STAR section."""
        tips = {
            "Action Oriented": {
                "situation": [
                    "Describe a time when you faced a new or urgent challenge.",
                    "What was at stake if you didn't act quickly?"
                ],
                "task": [
                    "What was your specific responsibility in taking action?",
                    "Were you expected to lead or just participate?"
                ],
                "action": [
                    "How did you take initiative?",
                    "What did you do differently from others?"
                ],
                "result": [
                    "What was the outcome of your quick action?",
                    "Did you exceed expectations or set a new standard?"
                ]
            },
            "Customer Focus": {
                "situation": [
                    "Describe a situation where customer needs were unclear or changing.",
                    "What was the customer's main concern?"
                ],
                "task": [
                    "What was your responsibility in addressing the customer's needs?"
                ],
                "action": [
                    "How did you listen and adapt to the customer?",
                    "What steps did you take to ensure satisfaction?"
                ],
                "result": [
                    "How did your actions impact the customer?",
                    "Did you receive feedback or recognition?"
                ]
            },
            # ...add more for other competencies as needed...
        }
        comp_tips = tips.get(competency, {})
        return comp_tips.get(section, [])

    def display_story(self):
        """Display the complete STAR story with color formatting."""
        story = self.story
        if not story or not all([story.get('situation'), story.get('task'), story.get('action'), story.get('result')]):
            print(Fore.RED + "\nThe story is incomplete. Please complete all sections first." + Style.RESET_ALL)
            return
        print("\n" + Fore.CYAN + "="*80 + Style.RESET_ALL)
        print(Fore.GREEN + "COMPLETE STAR STORY" + Style.RESET_ALL)
        print(f"\nCompetency: {Fore.YELLOW}{story.get('competency', '')}{Style.RESET_ALL}")
        print(f"Question: {Fore.YELLOW}{story.get('question', '')}{Style.RESET_ALL}")
        print(Fore.MAGENTA + "\nS - SITUATION:" + Style.RESET_ALL)
        print(story.get('situation', ''))
        print(Fore.MAGENTA + "\nT - TASK:" + Style.RESET_ALL)
        print(story.get('task', ''))
        print(Fore.MAGENTA + "\nA - ACTION:" + Style.RESET_ALL)
        print(story.get('action', ''))
        print(Fore.MAGENTA + "\nR - RESULT:" + Style.RESET_ALL)
        print(story.get('result', ''))

if __name__ == "__main__":
    coach = UnifiedSTARCoach()
    coach.run()
