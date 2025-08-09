import json

def load_project_ideas(json_path="assets/project_ideas.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def recommend_projects(jd_keywords, resume_keywords, ideas):
    aligned_projects = []
    suggested_projects = []

    for idea in ideas:
        project_title = idea.get("project_title", idea.get("title", "Untitled Project")).strip()
        description = idea.get("description", "").strip()
        keywords = [kw.lower() for kw in idea.get("keywords", [])]

        # Flags
        matches_resume = any(kw in resume_keywords for kw in keywords)
        matches_jd = any(kw in jd_keywords for kw in keywords)

        project_summary = {
            "project_title": project_title,  # Ensure key is consistent
            "description": description,
            "domain": idea.get("domain", ""),
            "tools": idea.get("tools", []),
            "keywords": keywords,
            "level": idea.get("level", "")
        }

        if matches_resume:
            aligned_projects.append(project_summary)
        elif matches_jd:
            suggested_projects.append(project_summary)

    return {
        "aligned": aligned_projects,
        "suggested": suggested_projects
    }
