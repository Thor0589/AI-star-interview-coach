import json
from pathlib import Path
from models import Story
from datetime import datetime


class STARMethodCoach:
    """
    A comprehensive STAR method interview coach that helps users craft exceptional
    interview stories, provides scoring, and offers actionable feedback.
    """

    def __init__(self):
        """Initialize the STAR Method Coach with competency frameworks and scoring criteria."""
        self.competencies = self.load_competencies()
        self.story = None  # Will be a Story instance
        self.current_competency = None
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

    def load_competencies(self):
        """Load competencies and associated interview questions."""
        # This is a simplified version of the competencies from the RTF file
        return {
            "Action Oriented": {
                "description": "Taking on new opportunities and tough challenges with a sense of urgency, high energy, and enthusiasm.",
                "questions": [
                    "Explain what you did when faced with a difficult and urgent problem.",
                    "Tell me about a time you had to take over someone else's challenging project.",
                    "Tell me about a situation that required an enormous amount of energy and effort.",
                    "Describe a time you seized an opportunity and moved forward with purpose.",
                    "Tell me about a time you were the first person to take action on something.",
                    "Describe a time when you were proactive in addressing a potential problem.",
                    "Tell me about a time you took a calculated risk and it paid off.",
                    "Explain a situation where you had to juggle multiple high-priority tasks."
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
                    "Tell me about a time when someone or something caught you by surprise and caused you to be blocked.",
                    "Describe a time when you had to adapt to a significant change at work.",
                    "Tell me about a time you received constructive criticism and how you handled it.",
                    "Explain a situation where you had to maintain your composure in a challenging circumstance."
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
                    "Tell me about a time you succeeded in an initiative by collaborating with others.",
                    "Explain a situation where you had to work with a difficult colleague and how you handled it.",
                    "Describe a time when you had to coordinate with multiple teams to achieve a goal.",
                    "Tell me about a time you had to manage conflicting priorities from different stakeholders."
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
                    "Describe a time you had to convey the same message through different methods of communication.",
                    "Explain a situation where you had to adjust your communication style to suit the audience.",
                    "Tell me about a time when you used data or evidence to support your message.",
                    "Describe a time when you had to persuade someone to see things your way."
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
                    "Tell me about a time when you changed your approach to better meet a customer's needs.",
                    "Describe a time when you gathered customer feedback and how you used it.",
                    "Tell me about a time you had to manage a customer's expectations.",
                    "Explain a situation where you turned an unhappy customer into a satisfied one."
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
                    "Describe a time when you received useful feedback on a decision you made.",
                    "Tell me about a time when you had to decide between two equally qualified candidates.",
                    "Explain a situation where you had to make a decision with incomplete information.",
                    "Describe a time when you changed your mind about a decision and what prompted the change."
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
                    "Talk about a time you were assigned to a fix-it or turnaround project.",
                    "Explain a situation where you had to overcome significant obstacles to achieve a goal.",
                    "Describe a time when your persistence paid off in achieving a difficult objective.",
                    "Tell me about a time you had to motivate others to achieve results."
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
                    "Describe a time you had to develop a strategy that would create value for your organization or customers.",
                    "Explain a situation where you had to align your team's goals with the organization's strategic objectives.",
                    "Tell me about a time when you identified a long-term opportunity and acted on it.",
                    "Describe a time when you had to convince others to buy into your strategic vision."
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

    def run(self):
        """Main execution method for the STAR Method Coach."""
        self.print_welcome_message()

        while True:
            print("\n" + "="*80)
            print("What would you like to do?")
            print("1. Select a competency and interview question")
            print("2. Craft a STAR story")
            print("3. Review and score an existing story")
            print("4. Exit")

            choice = input("\nEnter your choice (1-4): ")

            if choice == '1':
                self.select_competency_and_question()
            elif choice == '2':
                self.craft_star_story()
            elif choice == '3':
                self.review_and_score_story()
            elif choice == '4':
                print("\nThank you for using the STAR Method Coach. Good luck with your interviews!")
                break
            else:
                print("Invalid choice. Please try again.")

    def print_welcome_message(self):
        """Display the welcome message and introduction to the STAR Method."""
        print("\n" + "="*80)
        print("Welcome to the STAR Method Interview Coach!")
        print("This program will help you craft exceptional interview stories using the STAR method.")
        print("\nThe STAR Method stands for:")
        print("S - Situation: Set the scene and provide context.")
        print("T - Task: Explain your responsibility or challenge.")
        print("A - Action: Detail the specific steps you took.")
        print("R - Result: Share the outcomes of your actions and what you learned.")
        print("\nAfter crafting your story, you'll receive a score and personalized feedback.")

    def select_competency_and_question(self):
        """Guide the user to select a competency and related interview question."""
        print("\n" + "="*80)
        print("STEP 1: SELECT A COMPETENCY AND INTERVIEW QUESTION")
        print("\nAvailable competencies:")

        # Display competencies
        competency_list = list(self.competencies.keys())
        for i, competency in enumerate(competency_list, 1):
            print(f"{i}. {competency}: {self.competencies[competency]['description']}")

        # Get competency selection
        while True:
            try:
                comp_idx = int(input("\nSelect a competency (enter number): ")) - 1
                if 0 <= comp_idx < len(competency_list):
                    self.current_competency = competency_list[comp_idx]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(competency_list)}.")
            except ValueError:
                print("Please enter a valid number.")

        # Display questions for the selected competency
        print(f"\nInterview questions for '{self.current_competency}':")
        questions = self.competencies[self.current_competency]['questions']
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")

        # Get question selection or custom question
        print("\nSelect an interview question from the list above, or enter '0' to provide your own:")
        while True:
            try:
                q_idx = int(input("Enter your choice: "))
                if 1 <= q_idx <= len(questions):
                    self.story = {
                        'question': questions[q_idx - 1]
                    }
                    break
                elif q_idx == 0:
                    self.story = {
                        'question': input("Enter your custom interview question: ")
                    }
                    break
                else:
                    print(f"Please enter a number between 0 and {len(questions)}.")
            except ValueError:
                print("Please enter a valid number.")

        # Store the selected competency
        self.story = Story(
            competency=self.current_competency,
            question=self.story['question'],
            situation="",
            task="",
            action="",
            result=""
        )

        print(f"\nYou've selected: {self.story.competency}")
        print(f"Interview Question: {self.story.question}")
        print("Now you're ready to craft your STAR story!")

    def craft_star_story(self):
        """Guide the user through crafting a STAR method story."""
        if not self.story or not self.story.competency or not self.story.question:
            print("\nPlease select a competency and interview question first.")
            return

        print("\n" + "="*80)
        print("STEP 2: CRAFT YOUR STAR STORY")
        print(f"\nCompetency: {self.story.competency}")
        print(f"Question: {self.story.question}")

        # Situation
        print("\n" + "="*40)
        print("S - SITUATION: Set the scene and provide context")
        print("Tips:")
        print("- Describe the specific context/background")
        print("- Explain when and where this happened")
        print("- Identify key stakeholders involved")
        print("- Be concise yet detailed enough to set the stage")
        self.story.situation = input("\nDescribe the Situation:\n")

        # Task
        print("\n" + "="*40)
        print("T - TASK: Explain your responsibility or challenge")
        print("Tips:")
        print("- Clarify your specific role or responsibility")
        print("- Explain what you were trying to accomplish")
        print("- Highlight challenges or constraints you faced")
        print("- Focus on YOUR task, not the team's general task")
        self.story.task = input("\nDescribe the Task:\n")

        # Action
        print("\n" + "="*40)
        print("A - ACTION: Detail the specific steps you took")
        print("Tips:")
        print("- Focus on YOUR actions (use 'I' statements)")
        print("- Be specific about the steps you took")
        print("- Explain your thought process and decisions")
        print("- Highlight skills relevant to the competency")
        print("- Describe how you overcame obstacles")
        self.story.action = input("\nDescribe the Action:\n")

        # Result
        print("\n" + "="*40)
        print("R - RESULT: Share the outcomes of your actions")
        print("Tips:")
        print("- Quantify results whenever possible (%, $, time saved)")
        print("- Describe the impact on the organization/team/customers")
        print("- Include what you learned from the experience")
        print("- Connect the outcome back to the original situation/task")
        self.story.result = input("\nDescribe the Result:\n")

        # Story refinement option
        print("\n" + "="*40)
        print("Would you like to refine any part of your story?")
        while True:
            refine_choice = input("Enter the part to refine (situation, task, action, result) or 'done' to continue: ").lower()
            if refine_choice == 'done':
                break
            elif refine_choice in ['situation', 'task', 'action', 'result']:
                print(f"\nCurrent {refine_choice.capitalize()}:")
                print(getattr(self.story, refine_choice))
                setattr(self.story, refine_choice, input(f"\nUpdated {refine_choice.capitalize()}:\n"))
            else:
                print("Invalid input. Please enter 'situation', 'task', 'action', 'result', or 'done'.")

        # Review the complete story
        self.display_story()

        # Score the story
        self.score_story()

    def display_story(self):
        """Display the complete STAR story."""
        if not self.story or not all([self.story.situation, self.story.task, self.story.action, self.story.result]):
            print("\nThe story is incomplete. Please complete all sections first.")
            return

        print("\n" + "="*80)
        print("COMPLETE STAR STORY")
        print(f"\nCompetency: {self.story.competency}")
        print(f"Question: {self.story.question}")
        print("\nS - SITUATION:")
        print(self.story.situation)
        print("\nT - TASK:")
        print(self.story.task)
        print("\nA - ACTION:")
        print(self.story.action)
        print("\nR - RESULT:")
        print(self.story.result)

    def score_story(self):
        """Score the STAR story based on competency criteria."""
        if not self.story or not all([self.story.situation, self.story.task, self.story.action, self.story.result, self.story.competency]):
            print("\nCannot score an incomplete story.")
            return

        print("\n" + "="*80)
        print("STORY ASSESSMENT")

        # Simple scoring algorithm
        competency = self.story.competency

        # Extract key aspects of the story
        situation_length = len(self.story.situation.split())
        action_length = len(self.story.action.split())
        result_length = len(self.story.result.split())

        # Check for quantifiable results
        has_quantifiable_results = any(char.isdigit() for char in self.story.result)

        # Check for personal pronouns in action section
        personal_action = ('i ' in self.story.action.lower() or
                          'my ' in self.story.action.lower() or
                          'me ' in self.story.action.lower())

        # Check for alignment with competency
        skilled_signs = self.competencies[competency]['skilled_signs']
        unskilled_signs = self.competencies[competency]['unskilled_signs']

        skilled_alignment = sum(1 for sign in skilled_signs if any(word in self.story.action.lower() or word in self.story.result.lower()
                                                                  for word in sign.lower().split()))

        unskilled_alignment = sum(1 for sign in unskilled_signs if any(word in self.story.action.lower() or word in self.story.result.lower()
                                                                      for word in sign.lower().split()))

        # Determine the score
        score = "Skilled"  # Default score

        # Advanced scoring criteria
        if situation_length < 20 or action_length < 30 or result_length < 20:
            score = "Unskilled"
        elif not personal_action:
            score = "Unskilled"
        elif not has_quantifiable_results:
            score = "Skilled"  # Still skilled but could be improved
        elif action_length > 200 and result_length < 50:
            score = "Overused"  # Too much focus on action, not enough on results
        elif skilled_alignment > 2 and has_quantifiable_results and personal_action and action_length > 50:
            score = "Talented"
        elif unskilled_alignment > 2:
            score = "Unskilled"

        self.story.score = score

        # Display the score and provide feedback
        print(f"\nSCORE: {score}")
        print(f"\nScore Description: {self.scoring_criteria[score]['description']}")

        print("\nFEEDBACK:")
        self.provide_feedback(score)

        # Ask about saving the story
        save_choice = input("\nWould you like to save this story? (yes/no): ").lower()
        if save_choice in ['yes', 'y']:
            self.save_story()

    def provide_feedback(self, score):
        """Provide specific feedback based on the score and story content."""
        competency = self.story.competency
        situation_length = len(self.story.situation.split())
        task_length = len(self.story.task.split())
        action_length = len(self.story.action.split())
        result_length = len(self.story.result.split())

        # Check for specific patterns that need improvement
        has_quantifiable_results = any(char.isdigit() for char in self.story.result)
        personal_action = ('i ' in self.story.action.lower() or
                          'my ' in self.story.action.lower() or
                          'me ' in self.story.action.lower())

        # Provide general feedback based on score
        if score == "Talented":
            print("Your story demonstrates excellent mastery of this competency. It's detailed, focused, and shows significant impact.")
        elif score == "Skilled":
            print("Your story effectively demonstrates this competency. It provides a clear example with appropriate detail and positive outcomes.")
        elif score == "Unskilled":
            print("Your story needs improvement to effectively demonstrate this competency. It lacks some key elements that would make it more convincing.")
        elif score == "Overused":
            print("Your story shows an overemphasis on certain aspects of the competency, potentially at the expense of balance and effectiveness.")

        # Specific improvement suggestions
        print("\nSpecific suggestions for improvement:")

        if situation_length < 20:
            print("- Add more context to your situation to set the stage more effectively.")

        if task_length < 20:
            print("- Clarify your specific responsibility or challenge in more detail.")

        if not personal_action:
            print("- Focus more on YOUR actions by using 'I' statements rather than 'we' or passive voice.")

        if action_length < 50:
            print("- Provide more specific details about the steps you took and your decision-making process.")

        if result_length < 20:
            print("- Expand on the outcomes and impact of your actions.")

        if not has_quantifiable_results:
            print("- Include specific numbers or metrics to quantify your results (%, $, time saved, etc.).")

        if action_length > 200 and result_length < 50:
            print("- Balance your story by focusing more on results and less on listing every action step.")

        # Competency-specific feedback
        print(f"\nCompetency-specific feedback for '{competency}':")

        if score in ["Unskilled", "Overused"]:
            print("Consider incorporating these elements that demonstrate skill in this competency:")
            for sign in self.competencies[competency]['skilled_signs'][:2]:
                print(f"- {sign}")
        else:
            print("To further strengthen your story for this competency, consider:")
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

    def review_and_score_story(self):
        """Review and score an existing story (input by the user)."""
        print("\n" + "="*80)
        print("REVIEW AND SCORE AN EXISTING STORY")

        # Reset story
        self.story = {}

        # Get competency
        print("\nAvailable competencies:")
        competency_list = list(self.competencies.keys())
        for i, competency in enumerate(competency_list, 1):
            print(f"{i}. {competency}")

        while True:
            try:
                comp_idx = int(input("\nSelect the competency this story demonstrates (enter number): ")) - 1
                if 0 <= comp_idx < len(competency_list):
                    self.story['competency'] = competency_list[comp_idx]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(competency_list)}.")
            except ValueError:
                print("Please enter a valid number.")

        # Get interview question
        self.story['question'] = input("\nEnter the interview question this story addresses: ")

        # Get STAR elements
        print("\nEnter each element of your STAR story:")

        print("\nS - SITUATION: Set the scene and provide context")
        self.story['situation'] = input("Situation: ")

        print("\nT - TASK: Explain your responsibility or challenge")
        self.story['task'] = input("Task: ")

        print("\nA - ACTION: Detail the specific steps you took")
        self.story['action'] = input("Action: ")

        print("\nR - RESULT: Share the outcomes of your actions")
        self.story['result'] = input("Result: ")

        # Display and score the story
        # Convert dict to Story instance before displaying/scoring
        self.story = Story(
            competency=self.story['competency'],
            question=self.story['question'],
            situation=self.story['situation'],
            task=self.story['task'],
            action=self.story['action'],
            result=self.story['result']
        )
        self.display_story()
        self.score_story()

    def save_story(self):
        """Save the current Story instance to a JSON file in the Stories folder."""
        # Ensure we have a fully‑populated Story
        if not self.story or not all([
            self.story.situation, self.story.task, self.story.action, self.story.result,
            self.story.competency, self.story.question, self.story.score
        ]):
            print("\nCannot save an incomplete story.")
            return

        # Timestamp
        self.story.timestamp = datetime.now().isoformat()

        # Directory setup
        save_dir = Path("/Users/fernandoceja/Documents/Documents/VSCODEINSIDERS/Test/STARMETHOD/Stories")
        save_dir.mkdir(exist_ok=True)

        # File name based on question + competency
        safe_question = "_".join(self.story.question.split()).replace("?", "")
        safe_comp = "_".join(self.story.competency.split())
        filename = save_dir / f"{safe_question}_{safe_comp}.json"

        # Convert Story dataclass to dict
        story_dict = {
            "competency": self.story.competency,
            "question": self.story.question,
            "situation": self.story.situation,
            "task": self.story.task,
            "action": self.story.action,
            "result": self.story.result,
            "score": self.story.score,
            "timestamp": self.story.timestamp,
        }

        # If JSON exists, load list; else start new
        if filename.exists():
            try:
                with filename.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if not isinstance(data, list):
                    # Corrupt or legacy data; start fresh list
                    data = [data]
            except json.JSONDecodeError:
                data = []
        else:
            data = []

        # Append and write back
        data.append(story_dict)
        with filename.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

        print(f"\nStory saved to {filename}")


if __name__ == "__main__":
    coach = STARMethodCoach()
    coach.run()
