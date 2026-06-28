import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def update_analytics(session_state, question, category, confidence, duration):
    """
    Updates the session state analytics data.
    """
    if 'analytics_data' not in session_state:
        session_state['analytics_data'] = {
            'questions': [],
            'categories': [],
            'confidences': [],
            'durations': []
        }
        
    session_state['analytics_data']['questions'].append(question)
    session_state['analytics_data']['categories'].append(category)
    session_state['analytics_data']['confidences'].append(confidence)
    session_state['analytics_data']['durations'].append(duration)

def generate_dashboard_figures(session_state):
    """
    Generates Plotly figures for the Analytics dashboard based on session state.
    Returns a dictionary of figures.
    """
    if 'analytics_data' not in session_state or not session_state['analytics_data']['questions']:
        return None

    data = session_state['analytics_data']
    df = pd.DataFrame(data)

    figs = {}

    # Average Confidence Gauge
    avg_conf = df['confidences'].mean()
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_conf,
        title={'text': "Avg Confidence", 'font': {'color': '#94a3b8'}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
            'bar': {'color': "#22C55E"},
            'bgcolor': "rgba(255,255,255,0.05)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.2)"},
                {'range': [50, 80], 'color': "rgba(234, 179, 8, 0.2)"},
                {'range': [80, 100], 'color': "rgba(34, 197, 94, 0.2)"}
            ]
        }
    ))
    fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=200, margin=dict(l=20, r=20, t=30, b=20))
    figs['confidence_gauge'] = fig_gauge

    # 1. Confidence Distribution (Histogram)
    fig_conf = px.histogram(
        df, 
        x="confidences", 
        nbins=10, 
        title="Confidence Score Distribution",
        color_discrete_sequence=['#06B6D4']
    )
    fig_conf.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=250, margin=dict(l=20, r=20, t=30, b=20))
    figs['confidence_dist'] = fig_conf

    # 2. Most Asked Categories (Pie Chart)
    category_counts = df['categories'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    fig_cat = px.pie(
        category_counts, 
        names='Category', 
        values='Count', 
        title="Topics Queried",
        color_discrete_sequence=['#7C3AED', '#06B6D4', '#22C55E', '#f59e0b', '#ec4899']
    )
    fig_cat.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=250, margin=dict(l=20, r=20, t=30, b=20))
    figs['category_dist'] = fig_cat

    # 3. Overall Metrics
    figs['total_questions'] = len(df)
    figs['avg_confidence'] = avg_conf
    figs['total_duration'] = df['durations'].sum() # Simple sum of times taken per query
    
    return figs
