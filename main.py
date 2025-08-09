import streamlit as st
import sqlite3
import bcrypt
import tempfile
import os
from sklearn.feature_extraction.text import TfidfVectorizer
import plotly.graph_objects as go
import plotly.figure_factory as ff
from app import resume_parser, jd_parser, matcher, recommender

# ================== STREAMLIT CONFIGURATION ==================
st.set_page_config(page_title="  Resume screener", layout="wide")
st.title("🚀 Screener: Resume vs JD Matcher")
st.markdown("Upload your resume & job description to get match score, insights, and project recommendations.")


# ================== DATABASE SETUP ==================
DB_PATH = "users.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()

def create_user(username, name, email, password):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with conn:
            conn.execute("INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)",
                         (username, name, email, hashed_pw))
        return True
    except sqlite3.IntegrityError:
        return False

def get_user(username):
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    return c.fetchone()

def verify_user(username, password):
    user = get_user(username)
    if user and bcrypt.checkpw(password.encode(), user[4].encode()):
        return True, user
    return False, None

def update_password(email, new_password):
    hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    with conn:
        conn.execute("UPDATE users SET password=? WHERE email=?", (hashed_pw, email))
    return True

# ================== SIDEBAR AUTH CONTROLS ==================
st.sidebar.title("User Authentication")
auth_action = st.sidebar.radio("Choose Action", ["Login", "Signup", "Reset Password"])

if auth_action == "Signup":
    st.subheader("Create a new account")
    username = st.text_input("Username")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    if st.button("Create Account"):
        if password != confirm:
            st.error("Passwords do not match.")
        elif create_user(username.strip(), name.strip(), email.strip(), password.strip()):
            st.success("Account created! Please go to Login.")
        else:
            st.error("Username or Email already exists.")

elif auth_action == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        valid, user = verify_user(username, password)
        if valid:
            st.session_state['auth_user'] = {"username": username, "name": user[2], "email": user[3]}
            st.success(f"Welcome {user[2]}!")
        else:
            st.error("Invalid username or password.")

elif auth_action == "Reset Password":
    st.subheader("Reset your password")
    email = st.text_input("Enter your registered email")
    new_pw = st.text_input("New Password", type="password")
    confirm_pw = st.text_input("Confirm New Password", type="password")
    if st.button("Update Password"):
        if new_pw != confirm_pw:
            st.error("Passwords do not match.")
        else:
            update_password(email.strip(), new_pw.strip())
            st.success("Password updated! Please login.")

# ================== PROTECT MAIN APP ==================
if 'auth_user' in st.session_state:
    st.sidebar.write(f"Logged in as {st.session_state['auth_user']['name']}")
    if st.sidebar.button("Logout"):
        del st.session_state['auth_user']
        st.experimental_rerun()

    # ========= ORIGINAL Resume Matcher Logic =========
    PROJECT_IDEA_PATH = "assets/project_ideas.json"
    project_ideas = recommender.load_project_ideas(PROJECT_IDEA_PATH)

    

    # Upload Resume
    resume_file = st.file_uploader("📄 Upload your Resume (PDF)", type=["pdf"], key="resume_file")
    jd_input_method = st.radio("📋 Job Description Input", ["Upload .txt file", "Paste JD text"], key="jd_input")

    # Handle JD input
    jd_text = ""
    if jd_input_method == "Upload .txt file":
        jd_file = st.file_uploader("Upload Job Description (.txt)", type=["txt"], key="jd_file")
        if jd_file:
            jd_text = jd_file.read().decode("utf-8")
    else:
        jd_text = st.text_area("Paste Job Description here", key="jd_text_area")

    # Analyze Button
    if st.button("🔍 Analyze", key="analyze_button"):
        if resume_file and jd_text.strip():
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_resume:
                temp_resume.write(resume_file.read())
                temp_resume_path = temp_resume.name
            try:
                # Extract and preprocess
                resume_text = resume_parser.extract_text_from_pdf(temp_resume_path)
                resume_info = resume_parser.extract_basic_info(resume_text)
                resume_keywords = resume_parser.extract_resume_keywords(resume_text)
                jd_keywords = jd_parser.extract_jd_keywords(jd_text)

                # Use shared TF-IDF vectorizer
                combined_texts = [" ".join(resume_keywords), " ".join(jd_keywords)]
                vectorizer = TfidfVectorizer()
                vectors = vectorizer.fit_transform(combined_texts).toarray()
                resume_vector = vectors[0]
                jd_vector = vectors[1]

                # Matching Logic
                result = matcher.compare_resume_and_jd(resume_keywords, resume_vector, jd_keywords, jd_vector)

                # Project Suggestions
                projects = recommender.recommend_projects(jd_keywords, resume_keywords, project_ideas)

                # Display Results
                st.subheader("📊 Match Summary")
                st.markdown(f"**Match %:** `{result['match_percent']}%`")
                st.markdown(f"**Email:** {resume_info['email']} | **Phone:** {resume_info['phone']}")

                st.subheader("✅ Matched Skills")
                st.write(", ".join(result['matched_skills']) if result['matched_skills'] else "No major overlaps")

                st.subheader("❌ Missing Skills (from JD)")
                st.write(", ".join(result['missing_skills']) if result['missing_skills'] else "You're fully covered!")

                st.subheader("💡 Recommended Projects")
                if projects["suggested"]:
                    for proj in projects["suggested"]:
                        with st.expander(f"🛠 {proj['project_title']} ({proj['domain']}) [{proj['level']}]"):
                            st.markdown(f"- **Description:** {proj['description']}")
                            st.markdown(f"- **Tools:** {', '.join(proj['tools'])}")
                            st.markdown(f"- **Keywords:** {', '.join(proj['keywords'])}")
                else:
                    st.success("✅ No suggestions needed. You're well aligned!")

                # --- Dual Visualization: Heatmap + Gauge ---
                col1, col2 = st.columns(2)

                with col1:
                    fig = ff.create_annotated_heatmap(
                        z=[[result["match_percent"]]],
                        x=["JD"],
                        y=["Resume"],
                        annotation_text=[[f"{result['match_percent']}%"]],
                        colorscale="YlGnBu",
                        showscale=True,
                        font_colors=["black"],
                        zmin=0,
                        zmax=100
                    )
                    fig.update_layout(
                        title_text="Resume vs JD Match Heatmap",
                        title_x=0.5
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("🎯 Resume–JD Gauge Match")
                    gauge_fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=result["match_percent"],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Match %", 'font': {"size": 22}},
                        delta={'reference': 75, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                        gauge={
                            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                            'bar': {'color': "royalblue"},
                            'bgcolor': "white",
                            'steps': [
                                {'range': [0, 50], 'color': 'tomato'},
                                {'range': [50, 75], 'color': 'gold'},
                                {'range': [75, 100], 'color': 'lightgreen'}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': result["match_percent"]
                            }
                        }
                    ))
                    gauge_fig.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(gauge_fig)

            except Exception as e:
                st.error(f"⚠️ Error during processing: {str(e)}")
            finally:
                os.remove(temp_resume_path)
        else:
            st.warning("Please upload both a resume and job description.")
    else:
        st.info("Upload your resume and job description to get started!")