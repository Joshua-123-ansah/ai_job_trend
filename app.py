import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load dataset
df = pd.read_csv("ai_job_trends_dataset.csv")
df["Job Change"] = df["Projected Openings (2030)"] - df["Job Openings (2024)"]

# Summarization at industry level
industry_summary = df.groupby("Industry", as_index=False).agg({
    "Job Change": "sum",
    "Job Openings (2024)": "sum",  # This is needed for percentage calculation
    "AI Impact Level": lambda x: x.mode()[0]
})

# Percentage calculation
industry_summary["Job Change %"] = (industry_summary["Job Change"] / industry_summary["Job Openings (2024)"]) * 100

impact_map = {"Low": 1, "Moderate": 2, "High": 3}
industry_summary["AI Impact Numeric"] = industry_summary["AI Impact Level"].map(impact_map)
industry_summary["Trend"] = industry_summary["Job Change %"].apply(lambda x: "Job Creation" if x > 0 else "Job Loss")
industry_summary["Abs Job Change %"] = industry_summary["Job Change %"].abs()

color_map = {
    "Job Creation": "#2ecc71",  # Green
    "Job Loss": "#e74c3c"       # Red
}

fig = px.scatter(
    industry_summary,
    x="AI Impact Numeric",
    y="Job Change %",
    size="Abs Job Change %",
    size_max=50,  # Increased from default ~20 to make bubbles bigger
    color="Trend",
    color_discrete_map=color_map,
    hover_name="Industry",
    title="Industry-Level Job Change % vs. AI Impact Intensity",
    labels={
        "AI Impact Numeric": "AI Impact Intensity (Low → High)",
        "Job Change %": "Net Job Change % (2030–2024)"
    }
)
fig.update_layout(
    xaxis=dict(tickvals=[1, 2, 3], ticktext=["Low", "Moderate", "High"]),
    yaxis=dict(tickformat=".1f", ticksuffix="%"),  # Format y-axis as percentages
    template="plotly_white"
)

# --- Dash App Setup ---
app = Dash(__name__)

app.layout = html.Div([
    html.H2("AI Job Trends Dashboard"),
    dcc.Graph(id="bubble-chart", figure=fig),
    html.H4("Job Titles in Selected Industry:"),
    html.Ul(id="job-list")
])

# --- Interactivity Callback ---
@app.callback(
    Output("job-list", "children"),
    Input("bubble-chart", "clickData")
)
def display_job_titles(clickData):
    if clickData is None:
        return [html.Li("Click on a bubble to view job titles.")]
    
    industry_clicked = clickData["points"][0]["hovertext"]
    jobs = df.loc[df["Industry"] == industry_clicked, "Job Title"].unique()
    
    if len(jobs) == 0:
        return [html.Li(f"No job titles found for {industry_clicked}")]
    
    # Sortted jobs alphabetically for better readability
    jobs_sorted = sorted(jobs)
    
    return [
        html.H5(f"Industry: {industry_clicked} ({len(jobs_sorted)} jobs)"),
        html.Ul([html.Li(job) for job in jobs_sorted])
    ]

if __name__ == "__main__":
    app.run(debug=True)
