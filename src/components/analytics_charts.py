import streamlit as st
import pandas as pd
import altair as alt

def plot_performance_over_time(df: pd.DataFrame):
    """
    Plots user's quiz scores over time.
    """
    if df.empty or 'created_at' not in df.columns or 'score' not in df.columns:
        st.info("Take more quizzes to see your performance over time!")
        return

    df['created_at'] = pd.to_datetime(df['created_at'])

    chart = alt.Chart(df).mark_line(
        point=alt.OverlayMarkDef(color="blue", size=50),
        color='blue'
    ).encode(
        x=alt.X('created_at:T', title='Date', axis=alt.Axis(format='%b %d, %Y')),
        y=alt.Y('score:Q', title='Score (%)', scale=alt.Scale(domain=[0, 100])),
        tooltip=[
            alt.Tooltip('created_at:T', title='Date', format='%Y-%m-%d'),
            alt.Tooltip('topic:N', title='Topic'),
            alt.Tooltip('score:Q', title='Score', format='.1f'),
            alt.Tooltip('difficulty:N', title='Difficulty')
        ]
    ).properties(
        title='Your Quiz Performance Over Time'
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)

def plot_performance_by_topic(df: pd.DataFrame):
    """
    Plots user's average score by topic.
    """
    if df.empty or 'topic' not in df.columns or 'score' not in df.columns:
        st.info("Your topic performance will appear here after you take some quizzes.")
        return

    avg_scores = df.groupby('topic')['score'].mean().reset_index()
    avg_scores = avg_scores.sort_values(by='score', ascending=False)

    chart = alt.Chart(avg_scores).mark_bar().encode(
        x=alt.X('score:Q', title='Average Score (%)', scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('topic:N', title='Topic', sort='-x'),
        color=alt.Color('score:Q', scale=alt.Scale(scheme='greenblue'), legend=None),
        tooltip=[
            alt.Tooltip('topic:N', title='Topic'),
            alt.Tooltip('score:Q', title='Average Score', format='.1f')
        ]
    ).properties(
        title='Average Performance by Topic'
    )
    
    st.altair_chart(chart, use_container_width=True)