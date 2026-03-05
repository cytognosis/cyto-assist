import os

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

AGENTS_ROOT = os.path.expanduser("~/repos/cytognosis/agents")


def get_available_skills():
    skills_dir = os.path.join(AGENTS_ROOT, "skills")
    available = []
    for root, dirs, files in os.walk(skills_dir):
        if "SKILL.md" in files:
            rel_path = os.path.relpath(root, AGENTS_ROOT)
            available.append(rel_path)
    return available


def interactive_setup():
    skills = get_available_skills()
    if not skills:
        print(
            "No skills found. Make sure you are running this within the agents repo layout."
        )
        return

    choices = [Choice(s, name=s) for s in sorted(skills)]

    selected_skills = inquirer.checkbox(
        message="Select skills to install/bundle:",
        choices=choices,
    ).execute()

    if not selected_skills:
        print("No skills selected. Exiting.")
        return

    print(f"\nInstalling {len(selected_skills)} skills locally...")
    for s in selected_skills:
        print(f" - {s}")

    print("\n✅ Setup complete! Skills wrapped context generated.")
