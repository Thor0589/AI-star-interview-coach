#!/usr/bin/env python3
"""
Unified STAR Method Coach

A comprehensive program that combines multiple STAR method tools:
1. General STAR Method Coach with scoring and feedback
2. Quick STAR Story Builder for simple practice

This program helps users prepare for interviews by crafting effective STAR method stories.
"""

import os
import json
from datetime import datetime
from colorama import Fore, Style, init
from openai import OpenAI

# Initialize colorama
init(autoreset=True)


class UnifiedSTARCoach:
    """
    A comprehensive STAR method interview preparation tool that combines:
    1. General STAR Method coaching with scoring and feedback
    2. Simple STAR story building for quick practice
    """
    
    def __init__(self, competency_file='competencies.json'): # Retaining competency_file for potential future use
        """Initialize the Unified STAR Coach with all competency frameworks and scoring criteria."""
        init(autoreset=True)  # Initialize colorama
        self.api_client = OpenAI()  # Initialize OpenAI client
        
        # Load general competencies by calling the method defined in the class
        self.general_competencies = self.load_general_competencies() 
        
        self.stories = []
        self.current_story = {}

        # Scoring criteria
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
        """Loads general competencies from a structured format (e.g., JSON, YAML, or Python dict)."""
        # This is a placeholder. In a real application, you'd load this from a file.
        return {
            "Problem Solving": {
                "description": "Identifies and resolves problems in a timely manner; Gathers and analyzes information skillfully; Develops alternative solutions; Works well in group problem-solving situations.",
                "scoring_criteria": {
                    "Clarity of Problem Definition": "Did the user clearly define the problem they were facing?",
                    "Analysis of Root Cause": "Did the user analyze the root cause of the problem effectively?",
                    "Generation of Solutions": "Did the user generate multiple viable solutions?",
                    "Decision-Making Process": "Was the decision-making process for selecting a solution sound?",
                    "Implementation of Solution": "Was the solution implemented effectively?",
                    "Impact of Solution": "What was the measurable impact of the solution?"
                },
                "example_questions": [
                    "Describe a complex problem you had to solve. How did you approach it?",
                    "Tell me about a time you identified a potential problem and took steps to prevent it."
                ]
            },
            "Teamwork": {
                "description": "Balances team and individual responsibilities; Exhibits objectivity and openness to others' views; Gives and welcomes feedback; Contributes to building a positive team spirit; Puts success of team above own interests.",
                "scoring_criteria": {
                    "Collaboration with Others": "Did the user effectively collaborate with team members?",
                    "Contribution to Team Goals": "How did the user's actions contribute to team goals?",
                    "Handling of Conflict (if any)": "If there was conflict, how was it handled?",
                    "Support of Team Members": "Did the user support other team members?",
                    "Communication within Team": "Was communication within the team clear and effective?"
                },
                "example_questions": [
                    "Tell me about a time you worked effectively as part of a team.",
                    "Describe a situation where you had to work with a difficult team member."
                ]
            },
            "Communication": {
                "description": "Speaks clearly and persuasively in positive or negative situations; Listens and gets clarification; Responds well to questions; Demonstrates group presentation skills; Writes clearly and informatively.",
                "scoring_criteria": {
                    "Clarity of Communication": "Was the information conveyed clearly and concisely?",
                    "Audience Awareness": "Did the user tailor their communication to the audience?",
                    "Listening Skills": "Did the user demonstrate good listening skills?",
                    "Non-Verbal Communication (if applicable)": "How was non-verbal communication used?",
                    "Impact of Communication": "What was the outcome of the communication?"
                },
                "example_questions": [
                    "Describe a time you had to explain a complex topic to someone with less expertise.",
                    "Tell me about a situation where your communication skills made a difference."
                ]
            },
            "Leadership": {
                "description": "Inspires and motivates others to perform well; Effectively influences actions and opinions of others; Accepts feedback from others; Gives appropriate recognition to others.",
                "scoring_criteria": {
                    "Vision and Goal Setting": "Did the user articulate a clear vision or set clear goals?",
                    "Motivation of Others": "How did the user motivate others?",
                    "Decision Making": "Were decisions made effectively and in a timely manner?",
                    "Delegation (if applicable)": "How was delegation handled?",
                    "Conflict Resolution": "How were conflicts within the team resolved?"
                },
                "example_questions": [
                    "Tell me about a time you took a leadership role.",
                    "Describe a situation where you had to motivate a team or individual."
                ]
            },
            "Adaptability": {
                "description": "Adapts to changes in the work environment; Manages competing demands; Changes approach or method to best fit the situation; Deals with frequent change, delays, or unexpected events.",
                "scoring_criteria": {
                    "Response to Change": "How did the user respond to unexpected changes or challenges?",
                    "Flexibility": "Did the user demonstrate flexibility in their approach?",
                    "Problem Solving under Pressure": "How did the user handle problem-solving under pressure?",
                    "Learning from Experience": "Did the user learn from the experience and adapt for the future?"
                },
                "example_questions": [
                    "Tell me about a time you had to adapt to a significant change at work.",
                    "Describe a situation where you had to change your approach mid-project."
                ]
            }
        }
    # End of load_general_competencies

    def run(self):
        """Main execution method for the Unified STAR Coach."""
        self.print_welcome_message()
        while True:
            print("\n" + "="*80)
            print("What would you like to do?")
            print("1. General STAR Method Coach (with scoring and feedback)")
            print("2. Quick STAR Story Builder (simple practice)")
            print("3. Review a saved STAR story")
            print("4. Load and display a saved STAR story")
            print("5. Exit")
            choice = input("\nEnter your choice (1-5): ")

            if choice == '1':
                self.run_general_coach()
            elif choice == '2':
                self.run_quick_builder()
            elif choice == '3':
                self.review_saved_stories()
            elif choice == '4':
                self.load_story()
            elif choice == '5':
                print("\nThank you for using the Unified STAR Method Coach. Good luck with your interviews!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 5.")

    def print_welcome_message(self):
        """Prints the welcome message for the Unified STAR Coach."""
        print("="*80)
        print("🌟 WELCOME TO THE UNIFIED STAR METHOD INTERVIEW COACH! 🌟")
        print("="*80)
        print("This coach helps you practice and refine your interview stories using the STAR method.")
        print("You can choose between:")
        print("  - General STAR Coaching: Get feedback on stories for common competencies.")
        print("  - Quick Story Building: Quickly draft stories without immediate detailed feedback.")
        print("  - Story Review: Load and review your previously saved stories.")
        print("\nLet's begin!")

    #
    # General STAR Method Coach (from star_method_coach.py)
    #
    def run_general_coach(self):
        """Run the general STAR method coach with scoring and feedback."""
        print("\n" + "="*80)
        print("GENERAL STAR METHOD COACH")
        print("This mode helps you craft and get feedback on STAR stories for general competencies.")

        competencies = list(self.general_competencies.keys())
        print("\nAvailable competencies:")
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

        print(f"\nSelected Competency: {self.current_competency}")
        comp_details = self.general_competencies[self.current_competency]
        print(f"Description: {comp_details['description']}")

        # Display example questions for the selected competency
        if comp_details.get('example_questions'):
            print("\nExample interview questions for this competency:")
            for q_example in comp_details['example_questions']:
                print(f"- {q_example}")
        
        # Optionally, display a full example STAR story for this competency
        if input("\nWould you like to see an example STAR story for this competency? (yes/no): ").lower() in ['yes', 'y']:
            self.display_example_star_story(self.current_competency)
        print("Now you're ready to craft your STAR story!")
        # Set up the story dict for general context and launch STAR crafting
        self.story = {
            'competency': self.current_competency,
            'question': input("\nEnter the interview question you are answering: ")
        }
        self.craft_star_story()
        self.provide_feedback_and_score() # Provide feedback after crafting

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
        if story is None:
            story = self.story
        if not story or not all([story.get('situation'), story.get('task'), story.get('action'), story.get('result'), story.get('competency'), story.get('question')]):
            print("\nCannot save an incomplete story.")
            return
        story['timestamp'] = datetime.now().isoformat()
        save_dir = "Stories"
        os.makedirs(save_dir, exist_ok=True)
        safe_question = "_".join(story['question'].split()).replace("?", "")
        safe_comp = "_".join(story['competency'].split())
        filename = os.path.join(save_dir, f"{safe_question}_{safe_comp}.json")
        # If JSON exists, load list; else start new
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if not isinstance(data, list):
                    data = [data]
            except json.JSONDecodeError:
                data = []
        else:
            data = []
        data.append(story)
        with open(filename, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        print(f"\nStory saved to {filename}")

    def list_saved_stories(self):
        """List all saved STAR stories in the Stories directory."""
        save_dir = "Stories"
        if not os.path.exists(save_dir):
            print("No saved stories found.")
            return []
        files = [f for f in os.listdir(save_dir) if f.endswith('.json')]
        if not files:
            print("No saved stories found.")
            return []
        print("\nSaved STAR Stories:")
        for idx, file in enumerate(files, 1):
            print(f"{idx}. {file}")
        return files

    def load_story(self):
        """Load and display a saved STAR story."""
        files = self.list_saved_stories()
        if not files:
            return
        try:
            idx = int(input("\nEnter the number of the story to load: ")) - 1
            if 0 <= idx < len(files):
                with open(os.path.join("Stories", files[idx]), "r", encoding="utf-8") as fh:
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
                with open(os.path.join("Stories", files[idx]), "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                story = data[-1] if isinstance(data, list) else data
                self.story = story
                self.score_story()
            else:
                print("Invalid selection.")
        except Exception as e:
            print(f"Error reviewing story: {e}")

    def score_story(self):
        """
        Scores the STAR story in self.story based on competency criteria 
        and provides actionable feedback including AI suggestions.
        Expects self.story to be populated with:
        'situation', 'task', 'action', 'result', 'competency', 'question'.
        Returns a tuple: (score_str, score_description_str, ai_feedback_str)
        or (None, None, error_message_str) if scoring cannot proceed.
        """
        story = self.story
        if not story:
            return None, None, "Story object not found in coach."

        required_keys = ['situation', 'task', 'action', 'result', 'competency', 'question']
        missing_keys = [key for key in required_keys if not story.get(key)] # Checks for presence and non-empty
        if missing_keys:
            return None, None, f"Cannot score story: The following keys are missing or empty: {', '.join(missing_keys)}."

        competency = story['competency']

        if competency not in self.general_competencies:
            return None, None, f"Error: Competency '{competency}' not recognized for scoring. Available competencies: {list(self.general_competencies.keys())}"

        # Scoring logic based on story components
        situation_text = story.get('situation', '')
        action_text = story.get('action', '')
        result_text = story.get('result', '')

        situation_length = len(situation_text.split())
        action_length = len(action_text.split())
        result_length = len(result_text.split())
        has_quantifiable_results = any(char.isdigit() for char in result_text)
        
        personal_action_lower = action_text.lower()
        personal_action = ('i ' in personal_action_lower or 
                           'my ' in personal_action_lower or 
                           'me ' in personal_action_lower)

        # Safely get skilled_signs and unskilled_signs
        competency_details = self.general_competencies[competency]
        skilled_signs = competency_details.get('skilled_signs', [])
        unskilled_signs = competency_details.get('unskilled_signs', [])

        skilled_alignment = 0
        if skilled_signs: # Only calculate if skilled_signs are defined
            skilled_alignment = sum(1 for sign in skilled_signs if any(word in action_text.lower() or word in result_text.lower() for word in sign.lower().split()))
        
        unskilled_alignment = 0
        if unskilled_signs: # Only calculate if unskilled_signs are defined
            unskilled_alignment = sum(1 for sign in unskilled_signs if any(word in action_text.lower() or word in result_text.lower() for word in sign.lower().split()))
        
        # Determine score
        score = "Skilled"  # Default score
        if situation_length < 20 or action_length < 30 or result_length < 20:
            score = "Unskilled"
        elif not personal_action:
            score = "Unskilled"
        elif action_length > 200 and result_length < 50: 
            score = "Overused"
        elif skilled_signs and skilled_alignment > 2 and has_quantifiable_results and personal_action and action_length > 50:
            score = "Talented"
        elif unskilled_signs and unskilled_alignment > 2:
            score = "Unskilled"
        
        story['score'] = score 
        score_description = self.scoring_criteria[score]['description']

        ai_feedback = self.provide_feedback(
            score=score, 
            situation=situation_text,
            task=story.get('task', ''),
            action=action_text,
            result=result_text,
            competency=competency,
            question=story.get('question', '')
        )
        
        return score, score_description, ai_feedback

    def provide_feedback(self, score=None, situation=None, task=None, action=None, result=None, competency=None, question=None):
        # Determine data source for AI prompt: passed parameters take precedence (for app.py)
        # For console output (prints below), it will still primarily use self.story if set and score is passed.
        
        situation_for_ai = situation if situation is not None else (self.story.get('situation', '') if hasattr(self, 'story') else '')
        task_for_ai = task if task is not None else (self.story.get('task', '') if hasattr(self, 'story') else '')
        action_for_ai = action if action is not None else (self.story.get('action', '') if hasattr(self, 'story') else '')
        result_for_ai = result if result is not None else (self.story.get('result', '') if hasattr(self, 'story') else '')
        competency_for_ai = competency if competency is not None else (self.story.get('competency', 'N/A') if hasattr(self, 'story') else 'N/A')
        question_for_ai = question if question is not None else (self.story.get('question', 'N/A') if hasattr(self, 'story') else 'N/A')

        # Console-specific feedback (relies on self.story and score if called from score_story)
        if score and hasattr(self, 'story'):
            story_data_for_console = self.story # Use self.story for console logic
            situation_length = len(story_data_for_console.get('situation', '').split())
            task_length = len(story_data_for_console.get('task', '').split())
            action_length = len(story_data_for_console.get('action', '').split())
            result_length = len(story_data_for_console.get('result', '').split())
            has_quantifiable_results = any(char.isdigit() for char in story_data_for_console.get('result', ''))
            personal_action = ('i ' in story_data_for_console.get('action', '').lower() or 
                               'my ' in story_data_for_console.get('action', '').lower() or 
                               'me ' in story_data_for_console.get('action', '').lower())
            
            print(Fore.GREEN + "\\nFEEDBACK:" + Style.RESET_ALL)
            if score == "Talented":
                print(Fore.YELLOW + "Your story demonstrates excellent mastery of this competency. It's detailed, focused, and shows significant impact." + Style.RESET_ALL)
            elif score == "Skilled":
                print(Fore.YELLOW + "Your story effectively demonstrates this competency. It provides a clear example with appropriate detail and positive outcomes." + Style.RESET_ALL)
            elif score == "Unskilled":
                print(Fore.RED + "Your story needs improvement to effectively demonstrate this competency. It lacks some key elements that would make it more convincing." + Style.RESET_ALL)
            elif score == "Overused":
                print(Fore.MAGENTA + "Your story shows an overemphasis on certain aspects of the competency, potentially at the expense of balance and effectiveness." + Style.RESET_ALL)
            
            print(Fore.BLUE + "\\nSpecific suggestions for improvement:" + Style.RESET_ALL)
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
            if action_length > 200 and result_length < 50: # This condition was from score_story, might be redundant here
                print(Fore.YELLOW + "- Balance your story by focusing more on results and less on listing every action step." + Style.RESET_ALL)

            console_competency = story_data_for_console.get('competency', 'N/A') # Use competency from self.story for console
            print(Fore.CYAN + f"\\nCompetency-specific feedback for '{console_competency}':" + Style.RESET_ALL)
            if score in ["Unskilled", "Overused"]:
                print(Fore.YELLOW + "Consider incorporating these elements that demonstrate skill in this competency:" + Style.RESET_ALL)
                # Ensure console_competency is valid before accessing general_competencies
                if console_competency and console_competency in self.general_competencies:
                    skilled_signs_list = self.general_competencies[console_competency].get('skilled_signs', [])
                    for sign in skilled_signs_list[:2]:
                        print(Fore.YELLOW + f"- {sign}" + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + f"- (Could not load specific skilled signs for competency: {console_competency})" + Style.RESET_ALL)
            else: # Skilled or Talented
                print(Fore.GREEN + "To further strengthen your story for this competency, consider:" + Style.RESET_ALL)
                # ... (competency specific console suggestions remain unchanged, using console_competency)
                if console_competency == "Action Oriented":
                    print("- Emphasizing how quickly you took initiative without excessive planning")
                    print("- Highlighting your eagerness to tackle challenges head-on")
                elif console_competency == "Being Resilient":
                    print("- Focusing more on how you maintained composure under pressure")
                    print("- Emphasizing what you learned from overcoming adversity")
                # ... (rest of the competency specific console suggestions) ...
                elif console_competency == "Collaborates":
                    print("- Detailing how you balanced your interests with those of others")
                    print("- Explaining how you recognized others' contributions")
                elif console_competency == "Communicates Effectively":
                    print("- Highlighting how you adapted your communication style to different audiences")
                    print("- Showing how you ensured your message was clearly understood")
                elif console_competency == "Customer Focus":
                    print("- Emphasizing how you gained insight into customer needs")
                    print("- Detailing how you built a strong customer relationship")
                elif console_competency == "Decision Quality":
                    print("- Highlighting the factors you considered in your decision-making process")
                    print("- Showing how you made decisions with incomplete information")
                elif console_competency == "Drives Results":
                    print("- Emphasizing your persistence despite obstacles")
                    print("- Highlighting how you exceeded expectations or goals")
                elif console_competency == "Strategic Mindset":
                    print("- Emphasizing how you anticipated future trends or implications")
                    print("- Showing how your approach aligned with broader objectives")


        # AI-Powered Feedback Section - uses the _for_ai variables
        ai_feedback_result = None
        print(Fore.MAGENTA + "\\n✨ AI-Powered Suggestions: ✨" + Style.RESET_ALL) # This print is for console mode
        try:
            if not self.api_client:
                error_msg = "OpenAI API client is not initialized. Skipping AI feedback."
                print(Fore.RED + error_msg + Style.RESET_ALL) # Console
                return f"[AI Error: {error_msg}]" # Return for app.py

            prompt_text = (
                f"You are an expert interview coach. A user has provided the following STAR story for the competency '{competency_for_ai}'. "
                f"The interview question asked was: '{question_for_ai}'\\n\\n"
                f"Situation: {situation_for_ai}\\n"
                f"Task: {task_for_ai}\\n"
                f"Action: {action_for_ai}\\n"
                f"Result: {result_for_ai}\\n\\n"
                "Please provide 2-3 specific, actionable suggestions to improve this story. Focus on clarity, impact, and how well it demonstrates the competency. Keep the feedback concise and constructive."
            )
            
            response = self.api_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert interview coach providing feedback on STAR stories."},
                    {"role": "user", "content": prompt_text}
                ],
                max_tokens=200, # Increased slightly for potentially more detailed feedback
                temperature=0.7
            )
            
            ai_feedback_result = response.choices[0].message.content.strip()
            print(Fore.CYAN + ai_feedback_result + Style.RESET_ALL) # Console print

        except Exception as e:
            error_msg = f"Could not retrieve AI-powered feedback at this time: {e}"
            print(Fore.RED + error_msg + Style.RESET_ALL) # Console
            print(Fore.YELLOW + "Please ensure your OpenAI API key is correctly configured as an environment variable (OPENAI_API_KEY)." + Style.RESET_ALL) # Console
            ai_feedback_result = f"[AI Error: {error_msg}]" # Return for app.py
        
        return ai_feedback_result

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
