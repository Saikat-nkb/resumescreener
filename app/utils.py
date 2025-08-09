import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download once at startup
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Domain word bank (prioritized keywords)
DOMAIN_WORD_BANK = {
    "Data Science": [
        "machine learning", "deep learning", "regression", "classification", "clustering", "nlp", "computer vision",
        "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "tensorflow", "keras", "xgboost", "lightgbm",
        "data preprocessing", "model evaluation", "data cleaning", "feature engineering", "EDA", "data visualization",
        "time series", "sentiment analysis", "recommendation systems"
    ],
    "Web Development": [
        "html", "css", "javascript", "typescript", "react", "vue", "angular", "next.js", "tailwind", "bootstrap",
        "responsive design", "frontend", "backend", "api", "rest", "crud", "full stack", "node.js", "express", "flask", "django"
    ],
    "DevOps & Cloud": [
        "docker", "kubernetes", "terraform", "ansible", "jenkins", "ci/cd", "aws", "azure", "gcp", "lambda", "s3", "ec2", 
        "cloud functions", "load balancing", "auto scaling", "monitoring", "devops pipeline", "helm"
    ],
    "Cybersecurity": [
        "penetration testing", "vulnerabilities", "sql injection", "xss", "csrf", "firewall", "hashing", "encryption",
        "ssl", "tls", "authentication", "authorization", "jwt", "oauth", "kali linux", "nmap", "wireshark", "metasploit"
    ],
    "Mobile Development": [
        "android", "ios", "flutter", "dart", "react native", "swift", "kotlin", "firebase", "push notifications",
        "mobile ui", "play store", "app store", "cross platform", "native app"
    ],
    "Blockchain": [
        "ethereum", "solidity", "web3", "smart contract", "decentralized", "dapps", "blockchain", "wallet", "metamask",
        "nft", "token", "polygon", "binance", "gas fees", "consensus", "cryptography"
    ],
    "Artificial Intelligence": [
        "neural networks", "convolutional network", "transformers", "bert", "gpt", "reinforcement learning",
        "self supervised", "openai", "llm", "ai agents", "langchain", "autogpt", "rlhf", "speech recognition"
    ],
    "Finance & Analytics": [
        "stock prediction", "portfolio optimization", "monte carlo simulation", "risk modeling", "yfinance",
        "quantitative analysis", "fundamental analysis", "financial ratios", "npv", "roi", "cashflow", "excel modeling",
        "powerbi", "tableau", "dashboard", "etl", "sql", "analytics"
    ],
    "Big Data & Tools": [
        "hadoop", "spark", "hive", "pig", "kafka", "bigquery", "databricks", "airflow", "datalake", "data warehouse",
        "etl pipeline", "streaming", "data ingestion", "distributed systems"
    ],
    "Programming & Tools": [
        "python", "java", "c++", "git", "github", "bash", "linux", "regex", "jupyter", "vs code", "debugging", "pytest"
    ]
}


# Flatten full set of prioritized domain keywords
PRIORITY_KEYWORDS = list({kw.lower() for kws in DOMAIN_WORD_BANK.values() for kw in kws})

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII
    text = re.sub(r'https?://\S+|www\.\S+', '', text)  # Remove URLs
    text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)  # Remove punctuations
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_keywords(text):
    cleaned = clean_text(text)
    tokens = nltk.word_tokenize(cleaned)
    filtered = [lemmatizer.lemmatize(word) for word in tokens if word.isalnum() and word not in stop_words]
    
    # Prioritize domain-specific keywords
    domain_keywords = [word for word in filtered if word in PRIORITY_KEYWORDS]
    common_keywords = [word for word in filtered if word not in domain_keywords]
    
    return list(set(domain_keywords + common_keywords))
