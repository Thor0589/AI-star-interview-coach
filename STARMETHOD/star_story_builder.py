import os # Needed for path joining if you make the filename more robust
import subprocess
from datetime import datetime

# --- Constants ---
DEFAULT_SAVE_FILENAME = "star_stories.txt"
STORY_FOLDER = "/Users/fernandoceja/Documents/Documents/VSCODEINSIDERS/Test/STARMETHOD/Stories"
STAR_PARTS = ["situation", "task", "action", "result"]

SUGGESTED_TAGS = {
    "leadership": ["Drives_Results", "Collaborates", "Communicates_Effectively"],
    "deal with a difficult customer": ["Customer_Focus", "Communicates_Effectively", "Being_Resilient"],
    "meet a tight deadline": ["Drives_Results", "Action_Oriented", "Plans_and_Aligns"],
    "solve a complex problem": ["Manages_Complexity", "Decision_Quality", "Tech_Savvy"],
    "failed": ["Nimble_Learning", "Being_Resilient", "Self_Development"],
}

# --- Helper Functions ---

def print_introduction():
    """Prints the welcome message and STAR explanation."""
    print("\\nWelcome to the Interview STAR Story Builder!")
    print("This program will help you structure your answers using the STAR method.")
    print("\\n**The STAR Method:**")
    print("S - Situation: Describe the context and background.")
    print("T - Task: Explain your responsibility and objectives.")
    print("A - Action: Detail the steps you took to address the situation.")
    print("R - Result: Highlight the outcomes and what you learned.")
    print("\nLet's get started!")

def get_star_input():
    """Guides the user through entering S, T, A, R components."""
    story = {}
    prompts = {
        "situation": [
            "**S - Situation:** Set the scene. Think about:",
            "- What was the context of the situation?",
            "- Where and when did this happen?",
            "- Who was involved?",
            "Describe the Situation:\n"
        ],
        "task": [
            "\n**T - Task:**  What was your role and objective? Think about:",
            "- What was your specific responsibility?",
            "- What goal were you trying to achieve?",
            "- What challenges or constraints did you face?",
            "Describe the Task:\n"
        ],
        "action": [
            "\n**A - Action:** Detail the steps you took. Be specific and focus on *your* actions. Think about:",
            "- What exactly did you do?",
            "- How did you approach the problem or task?",
            "- What skills or tools did you use?",
            "Describe the Action:\n"
        ],
        "result": [
            "\n**R - Result:** What was the outcome? Focus on quantifiable results and learnings. Think about:",
            "- What was the outcome of your actions?",
            "- What impact did you have?",
            "- What did you learn from this experience?",
            "- (Ideally) Quantify your results with numbers or specific examples.",
            "Describe the Result:\n"
        ]
    }

    for part in STAR_PARTS:
        print("\n".join(prompts[part][:-1])) # Print guiding prompts
        story[part] = input(prompts[part][-1]) # Get user input
        print(f"Word count: {word_count(story[part])} words")
    return story

def display_story(story, question):
    """Prints the formatted STAR story."""
    print("\n**Your STAR Story Outline:**")
    print(f"**Question:** {question}\n")
    print(f"**S - Situation:**\n{story.get('situation', '')}")
    print(f"\n**T - Task:**\n{story.get('task', '')}")
    print(f"\n**A - Action:**\n{story.get('action', '')}")
    print(f"\n**R - Result:**\n{story.get('result', '')}")

def refine_story(story):
    """Handles the story refinement loop."""
    while True:
        refine_part = input("\nWhich part do you want to refine (situation, task, action, result, or done)? ").lower()
        if refine_part in STAR_PARTS:
            print(f"\nCurrent {refine_part.capitalize()}:\n{story[refine_part]}") # Show current text
            story[refine_part] = input(f"New {refine_part.capitalize()} description:\n")
            print(f"Word count: {word_count(story[refine_part])} words")
        elif refine_part == 'done':
            break
        else:
            print("Invalid part. Please choose from situation, task, action, result, or done.")
    return story # Return the potentially modified story

def handle_saving(story, question, suggested_tags=None, filename=DEFAULT_SAVE_FILENAME):
    """Asks the user if they want to save and saves if yes."""
    base_filename = sanitize_filename(question)
    primary_tag = sanitize_filename(suggested_tags[0]) if suggested_tags else ""
    proposed_filename = f"{base_filename}_{primary_tag}" if primary_tag else base_filename
    print(f"\nProposed filename: {proposed_filename}")
    
    include_timestamp = input("Do you want to include a timestamp in the filename? (yes/no): ").lower()
    if include_timestamp in ['yes', 'y']:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        proposed_filename = f"{proposed_filename}_{timestamp}.txt"
    else:
        # Do not append ".txt" here; it will be handled in save_story_to_file for consistency.
        pass
    
    if suggested_tags:
        print(f"Suggested tags based on your story: {', '.join(suggested_tags)}")
    tags_input = input("Enter tags (comma-separated) or press Enter to accept suggestions: ")
    tags = tags_input or ",".join(suggested_tags) if suggested_tags else tags_input
    
    save_choice = input("\nDo you want to save this story? (yes/no): ").lower()
    if save_choice in ['yes', 'y']:
        try:
            saved_filename = save_story_to_file(story, question, proposed_filename, tags)
            print(f"Story saved to {saved_filename}")
            subprocess.run(["open", saved_filename])  # Open the file automatically
        except IOError as e:
            print(f"Error saving file: {e}") # Basic error handling
    else:
        print("Story not saved.")

def sanitize_filename(text):
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in text).rstrip().replace(" ", "_")

def save_story_to_file(story, question, filename=DEFAULT_SAVE_FILENAME, tags=None):
    """Appends the story to the specified file."""
    os.makedirs(STORY_FOLDER, exist_ok=True)
    if not filename.lower().endswith(".txt"):
        filename += ".txt"
    full_path = os.path.join(STORY_FOLDER, filename)
    
    with open(full_path, "a", encoding='utf-8') as file: # Added encoding
        file.write(f"\n{'=' * 50}\n")
        file.write(f"# QUESTION: {question}\n\n")
        if tags:
            file.write(f"# TAGS: {tags}\n\n")
        file.write(f"## SITUATION:\n{story.get('situation', '')}\n\n")
        file.write(f"## TASK:\n{story.get('task', '')}\n\n")
        file.write(f"## ACTION:\n{story.get('action', '')}\n\n")
        file.write(f"## RESULT:\n{story.get('result', '')}\n\n")
        file.write(f"{'=' * 50}\n")
    return full_path

def get_sample_questions():
    """Returns a list of sample interview questions."""
    return [
        "Tell me about a time you had to deal with a difficult customer or colleague.",
        "Describe a situation where you had to meet a tight deadline.",
        "Tell me about a time you showed leadership skills.",
        "Give an example of when you had to solve a complex problem.",
        "Tell me about a time you failed and what you learned from it."
    ]

def word_count(text):
    """Counts the words in a given string."""
    return len(text.split())

def print_word_count_summary(story):
    """Prints the word counts for each part of the story."""
    for part in STAR_PARTS:
        print(f"{part.capitalize()} word count: {word_count(story[part])} words")

# --- Main Application Logic ---

def star_story_builder():
    """
    Main function to run the STAR story builder application.
    """
    print_introduction()

    while True:
        question = input("\n**Enter your interview question (or type 'samples' or 'exit'):**\n")
        sample_questions = get_sample_questions()
        # If user entered a number corresponding to sample list, map it to the actual question text
        if question.isdigit():
            idx = int(question)
            if 1 <= idx <= len(sample_questions):
                question = sample_questions[idx - 1]

        if question.lower() == 'exit':
            print("\\nThank you for practicing! Good luck with your interview!")
            break

        if question.lower() == 'samples':
            print("\nSample Interview Questions:")
            for i, q in enumerate(sample_questions, 1):
                print(f"{i}. {q}")
            continue # Go back to ask for input again

        print(f"\nGreat question: \"{question}\"")
        print("Let's structure a STAR story for this.")

        # Derive suggested tags
        suggested_tags = []
        for key, tags in SUGGESTED_TAGS.items():
            if key.lower() in question.lower():
                suggested_tags = tags
                break

        # 1. Get STAR input
        story = get_star_input()

        # 2. Display initial story
        display_story(story, question)

        # 3. Offer refinement
        review_choice = input("\nDo you want to review and refine your story? (yes/no): ").lower()
        if review_choice in ['yes', 'y']:
            story = refine_story(story) # Update story with refinements
            print("\n**Refined STAR Story Outline:**")
            display_story(story, question) # Display refined story
        elif review_choice in ['no', 'n']:
            print("Moving on without refinement.")
        else:
            print("Invalid choice. Moving on without refinement.")

        # 4. Offer to save
        handle_saving(story, question, suggested_tags=suggested_tags)

        # Print word count summary
        print_word_count_summary(story)

        print("\n--- Story Building Complete for this question ---")

if __name__ == "__main__":
    star_story_builder()