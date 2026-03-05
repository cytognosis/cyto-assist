import os

import yaml

AGENTS_ROOT = os.path.expanduser("~/repos/cytognosis/agents")


def load_yaml(path: str) -> dict:
    if not os.path.isabs(path):
        if path.startswith("personas"):
            path = "configs/" + path
        path = os.path.join(AGENTS_ROOT, path)
        if not path.endswith(".yaml"):
            path += ".yaml"

    with open(path) as f:
        return yaml.safe_load(f)


def load_skill_md(skill_path: str) -> str:
    full_path = os.path.join(AGENTS_ROOT, skill_path, "SKILL.md")
    if not os.path.exists(full_path):
        return f"\n> [Warning] Skill markdown not found for {skill_path}\n"
    with open(full_path) as f:
        return f.read()


def resolve_inheritance(persona: dict, visited=None) -> list:
    if visited is None:
        visited = set()

    skills = []
    if "inherits" in persona:
        for inherited in persona["inherits"]:
            if inherited in visited:
                continue
            visited.add(inherited)

            if "personas/" in inherited:
                try:
                    p_path = (
                        inherited
                        if inherited.endswith(".yaml")
                        else inherited + ".yaml"
                    )
                    parent_persona = load_yaml(p_path)
                    skills.extend(resolve_inheritance(parent_persona, visited))
                except FileNotFoundError:
                    skills.append(
                        f"> [Warning] Missing Persona Inheritance: {inherited}"
                    )
            else:
                skills.append(inherited)

    return skills


def compile_persona(persona_yaml_path: str) -> str:
    try:
        persona_data = load_yaml(persona_yaml_path)
    except FileNotFoundError:
        return f"Error: Persona file {persona_yaml_path} not found."

    all_skills = resolve_inheritance(persona_data)
    importance = persona_data.get("importance", {})

    prompt = f"# Persona: {persona_data.get('name', 'Unknown')}\n\n"
    prompt += "## Inherited Skills & Knowledge\n"

    for skill in all_skills:
        if isinstance(skill, str) and skill.startswith("> ["):
            prompt += skill + "\n"
            continue

        score = importance.get(skill, "")
        if score:
            prompt += f"\n### Sub-Skill: {skill} (Importance: {score})\n"
        else:
            prompt += f"\n### Sub-Skill: {skill}\n"

        prompt += load_skill_md(skill)
        prompt += "\n" + "=" * 40 + "\n"

    return prompt
