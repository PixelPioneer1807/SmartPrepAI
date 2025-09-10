import os
import streamlit as st
from dotenv import load_dotenv
from src.utils.helper import *
from src.generator.question_generator import QuestionGenerator
from src.models.auth import AuthManager
from src.models.simple_session import SimpleSessionManager
from src.components.quiz_history_sidebar import show_quiz_history_right_sidebar, render_history_content, show_revision_view
import pandas as pd
from src.components.analytics_charts import plot_performance_over_time, plot_performance_by_topic
import time

load_dotenv()

def show_login_signup():
    """
    Displays a polished, centered login/signup page with feature highlights.
    This is the only part that has been visually updated.
    """
    auth = AuthManager()

    # --- Centered Header ---
    st.image("dashboard.png", width=120)

    st.title("Welcome to SmartPrepAI")
    st.subheader("Your Personal AI-Powered Study Partner")
    st.write("---")

    # --- Feature Highlights in Columns ---
    st.subheader("🚀 Key Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; padding: 10px;'>🧠<br><strong>Unlimited Quizzes</strong><br><small>Generate custom quizzes on any topic at any difficulty.</small></div>", unsafe_allow_html=True)

    with col2:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; padding: 10px;'>📊<br><strong>Track Progress</strong><br><small>A visual dashboard helps you see your improvement.</small></div>", unsafe_allow_html=True)

    with col3:
        with st.container(border=True):
            st.markdown("<div style='text-align: center; padding: 10px;'>🎯<br><strong>Personalized Prep</strong><br><small>AI analyzes your mistakes to create targeted quizzes.</small></div>", unsafe_allow_html=True)
    
    st.write("---")

    # --- Centered Login/Signup Form ---
    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        with st.container(border=True):
            tab1, tab2 = st.tabs(["**Login**", "**Sign Up**"])
            with tab1:
                with st.form("login_form"):
                    st.markdown("##### Login to Your Account")
                    username = st.text_input("Username", key="login_user", label_visibility="collapsed", placeholder="Username")
                    password = st.text_input("Password", type="password", key="login_pass", label_visibility="collapsed", placeholder="Password")
                    login_btn = st.form_submit_button("Login", use_container_width=True, type="primary")
                    
                    if login_btn and username and password:
                        user_data = auth.login_user(username, password)
                        if user_data:
                            st.session_state.user = {k: v for k, v in user_data.items() if k != 'token'}
                            st.session_state.token = user_data['token']
                            st.success("Login successful! Loading...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
            
            with tab2:
                with st.form("signup_form"):
                    st.markdown("##### Create a New Account")
                    new_username = st.text_input("Username", key="signup_user", label_visibility="collapsed", placeholder="Choose a Username")
                    new_email = st.text_input("Email", key="signup_email", label_visibility="collapsed", placeholder="Your Email")
                    new_password = st.text_input("Password", type="password", key="signup_pass", label_visibility="collapsed", placeholder="Create a Password")
                    confirm_password = st.text_input("Confirm Password", type="password", key="signup_pass_confirm", label_visibility="collapsed", placeholder="Confirm Password")
                    signup_btn = st.form_submit_button("Sign Up", use_container_width=True)
                    
                    if signup_btn and new_username and new_email and new_password:
                        if new_password != confirm_password:
                            st.error("Passwords don't match")
                        elif len(new_password) < 6:
                            st.error("Password must be at least 6 characters.")
                        elif auth.register_user(new_username, new_email, new_password):
                            st.success("Account created! Please log in.")
                        else:
                            st.error("Username or email already exists.")

def check_auto_suggestions():
    """Check if user needs automatic suggestions based on recent poor performance"""
    if 'user' not in st.session_state or not st.session_state.user:
        return None
    
    try:
        quiz_manager = st.session_state.quiz_manager
        if not hasattr(quiz_manager, 'question_logger') or not quiz_manager.question_logger:
            return None
        
        user_id = st.session_state.user['id']
        
        recent_questions = quiz_manager.question_logger.get_recent_questions(user_id, 10)
        
        if len(recent_questions) >= 5:
            topic_performance = {}
            for q in recent_questions:
                topic_key = q['topic']
                if q.get('sub_topic'):
                    topic_key = f"{q['topic']} - {q['sub_topic']}"
                if topic_key not in topic_performance:
                    topic_performance[topic_key] = {'correct': 0, 'total': 0}
                topic_performance[topic_key]['total'] += 1
                if q['is_correct']:
                    topic_performance[topic_key]['correct'] += 1
            
            weak_topics = []
            for topic, perf in topic_performance.items():
                if perf['total'] >= 3:
                    accuracy = (perf['correct'] / perf['total']) * 100
                    if accuracy < 50:
                        weak_topics.append({'topic': topic, 'accuracy': accuracy, 'attempts': perf['total']})
            
            if weak_topics:
                return weak_topics  # <-- FIX: Return the entire list of weak topics
    
    except Exception as e:
        print(f"Auto suggestion check error: {e}")
    
    return None

def show_auto_suggestion_popup(weak_topics_list):
    """Show automatic suggestion popup, allowing user to choose if multiple topics are weak."""
    
    st.error("🎯 **Performance Alert!**")
    
    with st.container():
        # Let user choose which topic to focus on
        topic_options = [wt['topic'] for wt in weak_topics_list]
        
        if len(topic_options) > 1:
            st.write("Our AI noticed you're struggling in a few areas. Select a topic for a focused practice quiz:")
            chosen_topic_name = st.radio("Choose a topic to practice:", topic_options)
        else:
            chosen_topic_name = topic_options[0]
            st.write(f"**Struggling with {chosen_topic_name}?** Our AI recommends a focused practice quiz to improve!")

        # Find the full details of the chosen topic
        selected_topic_info = next((item for item in weak_topics_list if item["topic"] == chosen_topic_name), None)

        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🚀 Yes, Help Me!", type="primary", use_container_width=True):
                return "ACCEPT_AUTO_SUGGESTION", selected_topic_info
        
        with col2:
            if st.button("⏭️ Skip for Now", use_container_width=True):
                return "SKIP_AUTO_SUGGESTION", None
                
        with col3:
            if st.button("🔕 Don't Ask Again", use_container_width=True):
                st.session_state.disable_auto_suggestions = True
                return "DISABLE_AUTO_SUGGESTION", None
    
    return None, None

def generate_quiz_from_suggestion(suggestion_data):
    """Generate quiz directly from AI suggestion"""
    try:
        topic_full = f"{suggestion_data['main_topic']} - {suggestion_data['sub_topic']}" if suggestion_data.get('sub_topic') else suggestion_data['main_topic']
        st.session_state.current_topic, st.session_state.current_sub_topic, st.session_state.current_difficulty = suggestion_data['main_topic'], suggestion_data.get('sub_topic', ''), suggestion_data['difficulty']
        
        clear_quiz_states()
        with st.spinner("🤖 Generating personalized quiz based on your weak areas..."):
            generator = QuestionGenerator()
            success = st.session_state.quiz_manager.generate_questions(generator, topic_full, suggestion_data.get('question_type', 'Multiple Choice'), suggestion_data['difficulty'], suggestion_data['num_questions'])
        
        if success:
            st.session_state.quiz_generated = True
            st.success("✅ AI-powered quiz generated! Let's improve your weak areas!")
        else:
            st.error("❌ Failed to generate quiz. Please try again.")
        return success
        
    except Exception as e:
        st.error(f"❌ Quiz generation error: {e}")
        return False

def show_smart_recommendations():
    """Display AI-powered quiz recommendations with direct generation"""
    if 'user' not in st.session_state or not st.session_state.user:
        return None, None
    if st.session_state.get('quiz_generated', False) and not st.session_state.get('quiz_submitted', False):
        return None, None
    
    try:
        quiz_manager = st.session_state.quiz_manager
        recommendations = quiz_manager.get_smart_recommendations(st.session_state.user['id'])
        
        if recommendations['has_recommendations']:
            with st.expander("🤖 AI-Powered Quiz Recommendations", expanded=True):
                st.info(recommendations['motivation_message'])
                suggested = recommendations.get('suggested_quiz')
                if suggested:
                    st.write("**🎯 Recommended Quiz for You:**")
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**Topic:** {suggested['main_topic']}")
                        if suggested.get('sub_topic'): st.write(f"**Sub-topic:** {suggested['sub_topic']}")
                        st.write(f"**Difficulty:** {suggested['difficulty']}")
                        st.write(f"**Questions:** {suggested['num_questions']}")
                        st.caption(f"💡 {suggested['reason']}")
                    if col2.button("🚀 Generate AI Quiz", type="primary"):
                        return "GENERATE_DIRECT", suggested
                
                if recommendations.get('focus_areas'):
                    st.write("**📊 Your Performance Analysis:**")
                    for area in recommendations['focus_areas']:
                        st.write(f"• {area}")
        else:
            st.success("🌟 " + recommendations.get('motivation_message', 'Keep practicing!'))
    
    except Exception as e:
        print(f"Smart recommendations error: {e}")
        st.info("🤖 AI recommendations will appear after you take more quizzes!")
    
    return None, None

def handle_personalized_prep(topic_name: str):
    """
    Handles the RAG-based personalized quiz generation and trial usage.
    """
    auth = AuthManager()
    user_id = st.session_state.user['id']

    st.session_state.current_topic = topic_name
    st.session_state.current_sub_topic = ""
    st.session_state.current_difficulty = "Easy"
    
    clear_quiz_states()
    
    with st.spinner(f"🤖 Retrieving your weak points for '{topic_name}'..."):
        if not st.session_state.quiz_manager.vector_db_manager.has_enough_context():
            st.error("You don't have enough prep material yet. Fail a quiz on this topic first!")
            time.sleep(3); return
        context_docs = st.session_state.quiz_manager.vector_db_manager.retrieve_relevant_documents(topic_name)
    
    with st.spinner("🧠 Generating a personalized quiz..."):
        try:
            generator = QuestionGenerator()
            questions = []
            for _ in range(3):
                q = generator.generate_rag_mcq(topic_name, context_docs, "Easy")
                questions.append({'type': 'MCQ', 'question': q.question, 'options': q.options, 'correct_answer': q.correct_answer, 'explanation': getattr(q, 'explanation', '')})
            
            st.session_state.quiz_manager.questions = questions
            st.session_state.quiz_generated = True
            
            auth.mark_rag_trial_as_used(user_id)
            st.session_state.user['has_used_rag_trial'] = 1
            
            st.success("✅ Personalized quiz ready! Your free trial has been used."); time.sleep(2); st.rerun()
        except Exception as e:
            st.error(f"Failed to generate personalized quiz: {e}"); time.sleep(3)

def show_dashboard():
    """Show user dashboard with analytics and visualizations."""
    user = st.session_state.user
    session_manager = SimpleSessionManager()
    
    st.header(f"Welcome back, {user['username']}! 👋")
    
    user_sessions = session_manager.get_user_sessions(user['id'], limit=1000)
    if not user_sessions:
        st.info("Your dashboard will be populated once you complete a quiz!"); return

    total_quizzes, avg_score = len(user_sessions), sum(s['score'] for s in user_sessions) / len(user_sessions) if user_sessions else 0
    from datetime import datetime, timedelta
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_sessions_count = sum(1 for s in user_sessions if datetime.strptime(s['created_at'], '%Y-%m-%d %H:%M:%S') >= seven_days_ago)

    col1, col2, col3 = st.columns(3); col1.metric("Total Quizzes", total_quizzes); col2.metric("Average Score", f"{avg_score:.1f}%"); col3.metric("Quizzes This Week", recent_sessions_count)
    st.markdown("---")

    st.subheader("📊 Your Performance Visualized")
    df = pd.DataFrame(user_sessions)
    plot_performance_over_time(df); plot_performance_by_topic(df)
    st.markdown("---")

    st.subheader("🎯 Areas for Improvement")
    topic_performance = {}
    for session in user_sessions:
        topic_key = session['display_title']
        if topic_key not in topic_performance:
            topic_performance[topic_key] = {'scores': [], 'count': 0}
        topic_performance[topic_key]['scores'].append(session['score']); topic_performance[topic_key]['count'] += 1
        
    weak_topics = []
    pass_score = st.session_state.get('pass_score', 70)
    for topic, data in topic_performance.items():
        avg_score = sum(data['scores']) / len(data['scores'])
        if avg_score < pass_score:
            weak_topics.append({"topic": topic, "avg_score": avg_score, "count": data['count']})

    if weak_topics:
        st.warning(f"AI has identified topics below your {pass_score}% goal. Focus here!")
        for topic_data in sorted(weak_topics, key=lambda x: x['avg_score']):
            with st.container(border=True):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**{topic_data['topic']}**"); st.caption(f"Avg Score: {topic_data['avg_score']:.1f}% ({topic_data['count']} quizzes)")
                with col2:
                    if not user.get('has_used_rag_trial', False):
                        if st.button("🚀 Prep (Free Trial)", key=f"prep_{topic_data['topic']}", use_container_width=True):
                            handle_personalized_prep(topic_data['topic'])
                    else:
                        st.button("✨ Upgrade to Prep", key=f"prep_{topic_data['topic']}", disabled=True, use_container_width=True)
    else:
        st.success("🎉 Great job! You're meeting your pass score in all topics.")
    st.markdown("---")

    st.subheader("📖 Recent Quiz History")
    for session in user_sessions[:5]:
        with st.expander(f"**{session['display_title']}** - Score: {session['score']:.1f}% ({session['short_date']})"):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Type:** {session['question_type']}"); c1.write(f"**Difficulty:** {session['difficulty']}")
            c2.write(f"**Questions:** {session['num_questions']}"); c2.write(f"**Score:** {session['score']:.1f}%")
            if c3.button(f"📖 Review Quiz", key=f"review_{session['id']}"):
                st.session_state.viewing_quiz_id, st.session_state.view_mode = session['id'], 'revision'; st.rerun()

def clear_quiz_states():
    st.session_state.quiz_generated, st.session_state.quiz_submitted = False, False
    if hasattr(st.session_state.get('quiz_manager'), 'questions'):
        st.session_state.quiz_manager.questions, st.session_state.quiz_manager.user_answers, st.session_state.quiz_manager.results = [], [], []

def main():
    st.set_page_config(page_title="SmartPrepAI", layout="wide")
    auth = AuthManager()
    
    if not auth.is_authenticated():
        show_login_signup(); return
    
    if 'quiz_manager' not in st.session_state: st.session_state.quiz_manager = QuizManager()
    if 'quiz_generated' not in st.session_state: st.session_state.quiz_generated = False
    if 'quiz_submitted' not in st.session_state: st.session_state.quiz_submitted = False
    
    if st.session_state.get('view_mode') == 'revision' and st.session_state.get('viewing_quiz_id'):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("SmartPrepAI - Quiz Revision")
            show_revision_view(st.session_state.viewing_quiz_id)
        with col2: render_history_content()
        return
    
    col1, col2 = st.columns([6, 1])
    with col1: st.title("StudyBuddyAI")
    with col2:
        if st.button("📚 History", help="Toggle quiz history"):
            st.session_state.show_history = not st.session_state.get('show_history', False); st.rerun()
    
    with st.sidebar:
        if st.button("Logout"): auth.logout()
    
    main_col, history_col = st.columns([3, 1]) if st.session_state.get('show_history', False) else (st.container(), None)
    
    with main_col:
        tab1, tab2 = st.tabs(["**New Quiz**", "**Dashboard**"])
        with tab1:
            auto_suggestion_result = None, None
            if not st.session_state.get('disable_auto_suggestions', False):
                weak_topic = check_auto_suggestions()
                if weak_topic and not st.session_state.get('quiz_generated', False) and not st.session_state.get('quiz_submitted', False):
                    auto_suggestion_result = show_auto_suggestion_popup(weak_topic)
            
            action, data = auto_suggestion_result
            if action == "ACCEPT_AUTO_SUGGESTION":
                topic_parts = data['topic'].split(' - ', 1)
                suggestion_data = {'main_topic': topic_parts[0], 'sub_topic': topic_parts[1] if len(topic_parts) > 1 else "", 'difficulty': 'Easy', 'question_type': 'Multiple Choice', 'num_questions': 5}
                generate_quiz_from_suggestion(suggestion_data); st.rerun()
            elif action in ["SKIP_AUTO_SUGGESTION", "DISABLE_AUTO_SUGGESTION"]:
                st.rerun()
            
            if not weak_topic or st.session_state.get('disable_auto_suggestions', False):
                if not st.session_state.get('quiz_generated', False) or st.session_state.get('quiz_submitted', False):
                    action, data = show_smart_recommendations()
                    if action == "GENERATE_DIRECT":
                        generate_quiz_from_suggestion(data); st.rerun()
            
            with st.sidebar:
                st.header("Quiz Settings")
                question_type = st.selectbox("Select Question Type", ["Multiple Choice", "Fill in the Blank"])
                main_topic = st.selectbox("Select Main Topic", ["Operating Systems", "Computer Networks", "DBMS", "DSA", "OOPs", "Machine Learning", "Software Engineering", "C++", "Java", "Javascript", "Python"])
                sub_topic = st.text_input("Enter Sub-topic", placeholder="e.g., Paging, TCP/IP, Normalization")
                topic = f"{main_topic} - {sub_topic}" if sub_topic else main_topic
                st.session_state.current_topic, st.session_state.current_sub_topic = main_topic, sub_topic
                difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
                st.session_state.current_difficulty = difficulty
                num_questions = st.number_input("Number of Questions", 1, 10, 5)
                pass_score = st.slider("Set Your Pass Score (%)", 30, 90, 70, 5, help="Set the score you want to achieve to consider a topic 'mastered'.")
                st.session_state.pass_score = pass_score
                
                if st.button("Generate Quiz", type="primary"):
                    clear_quiz_states()
                    with st.spinner("🤖 AI is generating personalized questions..."):
                        generator = QuestionGenerator()
                        success = st.session_state.quiz_manager.generate_questions(generator, topic, question_type, difficulty, num_questions)
                    st.session_state.quiz_generated = success
                    if success: st.success("✅ Quiz generated successfully!")
                    st.rerun()
            
            if st.session_state.quiz_generated and not st.session_state.quiz_submitted:
                st.header("📝 Quiz Time!")
                topic_display = st.session_state.current_topic
                if st.session_state.get('current_sub_topic'): topic_display += f" - {st.session_state.current_sub_topic}"
                st.write(f"**🤖 Topic:** {topic_display} | **Difficulty:** {st.session_state.get('current_difficulty', 'Medium')} | **Questions:** {len(st.session_state.quiz_manager.questions)}")
                st.session_state.quiz_manager.attempt_quiz()
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🎯 Submit Quiz", type="primary", use_container_width=True):
                        with st.spinner("🔍 Evaluating your answers..."):
                            st.session_state.quiz_manager.evaluate_quiz()
                            st.session_state.quiz_submitted = True
                        st.rerun()
            
            elif st.session_state.quiz_submitted:
                st.header("📊 Quiz Results")
                results_df = st.session_state.quiz_manager.generate_result_dataframe()
                if not results_df.empty:
                    correct, total, score = results_df["is_correct"].sum(), len(results_df), (results_df["is_correct"].sum()/len(results_df))*100
                    st.subheader("🚀 Quick Actions")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("🔄 Same Topic Again", use_container_width=True):
                            topic_full = f"{st.session_state.get('current_topic', 'DSA')} - {st.session_state.get('current_sub_topic', '')}" if st.session_state.get('current_sub_topic') else st.session_state.get('current_topic', 'DSA')
                            clear_quiz_states()
                            with st.spinner("🔄 Generating another quiz..."):
                                generator = QuestionGenerator()
                                success = st.session_state.quiz_manager.generate_questions(generator, topic_full, "Multiple Choice", st.session_state.get('current_difficulty', 'Medium'), 5)
                                if success: st.session_state.quiz_generated = True
                            st.rerun()
                    with col2:
                        if st.button("⬆️ Increase Difficulty", use_container_width=True):
                            next_diff = {'Easy': 'Medium', 'Medium': 'Hard', 'Hard': 'Hard'}[st.session_state.get('current_difficulty', 'Easy')]
                            st.session_state.current_difficulty = next_diff
                            topic_full = f"{st.session_state.get('current_topic', 'DSA')} - {st.session_state.get('current_sub_topic', '')}" if st.session_state.get('current_sub_topic') else st.session_state.get('current_topic', 'DSA')
                            clear_quiz_states()
                            with st.spinner(f"⬆️ Generating {next_diff} quiz..."):
                                generator = QuestionGenerator()
                                success = st.session_state.quiz_manager.generate_questions(generator, topic_full, "Multiple Choice", next_diff, 5)
                                if success: st.session_state.quiz_generated = True
                            st.rerun()
                    with col3:
                        if st.button("🤖 AI Suggestion", use_container_width=True):
                            clear_quiz_states(); st.rerun()
                    with col4:
                        if st.button("📊 View Progress", use_container_width=True):
                            st.info("👆 Switch to Dashboard tab!")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Score", f"{score:.1f}%"); col2.metric("Correct", f"{correct}/{total}"); col3.metric("Status", "📈 Keep going!" if score >= 60 else "🎯 Opportunity to improve!")
                    
                    if score >= 80: st.success(f"🎉 Excellent! Score: {score:.1f}%")
                    elif score >= 60: st.info(f"👍 Good job! Score: {score:.1f}%")
                    else: st.warning(f"📚 Score: {score:.1f}% - A chance to learn and improve!")
                    
                    st.subheader("🔍 Detailed Results with AI Explanations")
                    for _, result in results_df.iterrows():
                        if result['is_correct']: st.success(f"✅ **Q{result['question_number']}:** {result['question']}")
                        else: st.error(f"❌ **Q{result['question_number']}:** {result['question']}"); st.write(f"Your: `{result['user_answer']}` | Correct: `{result['correct_answer']}`")
                        if result.get('explanation'): st.info(f"💡 **AI Explanation:** {result['explanation']}")
                        ai_links = st.session_state.quiz_manager.generate_ai_links(result['question'], result['correct_answer'], st.session_state.get('current_topic', 'General'), result['user_answer'])
                        st.write("**🤖 Need deeper understanding? Ask AI assistants:**")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.markdown(f"[💬 ChatGPT]({ai_links['chatgpt']})"); c2.markdown(f"[✨ Gemini]({ai_links['gemini']})"); c3.markdown(f"[🧠 Claude]({ai_links['claude']})"); c4.markdown(f"[🔍 Perplexity]({ai_links['perplexity']})")
                        st.markdown("---")
        
        with tab2:
            show_dashboard()
    
    if history_col:
        with history_col: render_history_content()

if __name__ == "__main__":
    main()