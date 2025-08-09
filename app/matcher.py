from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ✅ Expanded Domain Keyword Bank for Better Weighting
DOMAIN_KEYWORDS = set([
    # Data Science & ML
    "data science", "machine learning", "deep learning", "nlp", "natural language processing",
    "data analysis", "data visualization", "supervised learning", "unsupervised learning",
    "reinforcement learning", "clustering", "classification", "regression", "time series",
    "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "tensorflow", "keras", "xgboost",

    # Software Development
    "software engineering", "design patterns", "oop", "object-oriented programming",
    "data structures", "algorithms", "system design", "api development", "rest api",
    "microservices", "unit testing", "integration testing", "agile", "scrum", "version control",

    # Programming Languages & Tools
    "python", "java", "c++", "c#", "javascript", "typescript", "go", "r", "sql", "html", "css",
    "bash", "powershell", "linux", "git", "github", "bitbucket",

    # Web & App Development
    "frontend", "backend", "fullstack", "react", "angular", "vue", "node.js", "express",
    "flask", "django", "fastapi", "next.js", "tailwind", "bootstrap", "redux", "websockets",

    # Cloud & DevOps
    "aws", "azure", "gcp", "cloud computing", "devops", "docker", "kubernetes", "terraform",
    "jenkins", "ci/cd", "ansible", "prometheus", "grafana", "linux administration",

    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "oracle", "nosql", "dynamodb", "data warehouse",
    "etl", "data pipeline", "snowflake", "bigquery", "redshift",

    # AI/GenAI & Tools
    "generative ai", "chatbot", "langchain", "llm", "openai", "gemini", "prompt engineering",
    "vector db", "pinecone", "chromadb", "retrieval augmented generation", "rag", "embedding",

    # Business/Finance/Analytics
    "business analyst", "forecasting", "portfolio", "risk management", "credit scoring",
    "finance", "equity", "trading", "valuation", "stock prediction", "market analysis",

    # Tools & Platforms
    "power bi", "tableau", "excel", "jira", "notion", "postman", "airflow", "mlflow",
    "streamlit", "gradio", "dash", "plotly",

    # Soft + Collaboration (Optional Boost)
    "communication", "leadership", "problem solving", "collaboration", "teamwork"
])

def _calculate_weighted_match(resume_keywords, jd_keywords):
    """
    Custom weighted overlap score prioritizing domain-specific keywords.
    """
    matched = set(resume_keywords).intersection(set(jd_keywords))
    matched_domain = matched.intersection(DOMAIN_KEYWORDS)

    base_score = len(matched)
    domain_bonus = len(matched_domain) * 1.5  # Domain skills get higher weight

    total_possible = len(set(jd_keywords)) + 1e-5  # avoid division by zero
    match_percent = ((base_score + domain_bonus) / total_possible) * 100
    return round(match_percent, 2), list(matched), list(set(jd_keywords) - set(resume_keywords))

def compare_resume_and_jd(resume_keywords, resume_vector, jd_keywords, jd_vector):
    from sklearn.metrics.pairwise import cosine_similarity

    matched_skills = list(set(resume_keywords).intersection(set(jd_keywords)))
    missing_skills = list(set(jd_keywords) - set(resume_keywords))
    similarity_score = float(cosine_similarity([resume_vector], [jd_vector])[0][0])

    matched_domain = set(matched_skills) & DOMAIN_KEYWORDS
    domain_bonus = len(matched_domain) * 2.0
    
    match_percent = round((similarity_score * 100) + domain_bonus, 2)

    return {
        "match_percent": match_percent,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }