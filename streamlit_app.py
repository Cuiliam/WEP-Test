import streamlit as st
import pandas as pd
import plotly.express as px

# ----------- Sample Data (You can later load this from a CSV) -----------
data = {
    "Park": ["Hemlock Bluffs", "Dunham Park", "Fred G. Bond", "Thomas Brooks", "Carpenter"],
    "Threat Level": [8, 7, 6, 4, 3],
    "Water Distribution": [6, 5, 9, 4, 3],
    "Landscaping": [2, 5, 7, 6, 8],
    "Neighborhoods": [7, 6, 8, 5, 9],
    "Partnerships": [9, 6, 8, 7, 5],
    "Ranger Notes": [
        "Dense privet in northern quadrant",
        "Kudzu near trailheads",
        "Some management already in place",
        "Edge invasion, relatively contained",
        "Mostly landscaped, low risk"
    ]
}
df = pd.DataFrame(data)
df["Total Score"] = df.iloc[:, 1:6].sum(axis=1)
df = df.sort_values("Total Score", ascending=False)

# ---------------- STREAMLIT UI ----------------
st.title("Town of Cary Invasive Species Priority Dashboard")

# Sidebar
with st.sidebar:
    st.header("Filters")
    selected_parks = st.multiselect("Select parks to view", df["Park"].tolist(), default=df["Park"].tolist())

# Filter data
filtered_df = df[df["Park"].isin(selected_parks)]

# Display Prioritization Matrix
st.subheader("Prioritization Matrix")
st.dataframe(filtered_df.set_index("Park").style.background_gradient(axis=0, cmap="YlOrRd"))

# Show total ranking chart
st.subheader("Overall Priority Ranking")
fig = px.bar(filtered_df, x="Park", y="Total Score", color="Total Score", text="Total Score", color_continuous_scale='Reds')
st.plotly_chart(fig)

# Detailed info per park
st.subheader("Park Detail Viewer")
park_choice = st.selectbox("Select a park to view details", df["Park"])
park_row = df[df["Park"] == park_choice].iloc[0]

st.markdown(f"""
### {park_choice}
- **Threat Level**: {park_row['Threat Level']}  
- **Water Distribution**: {park_row['Water Distribution']}  
- **Landscaping**: {park_row['Landscaping']}  
- **Neighborhoods**: {park_row['Neighborhoods']}  
- **Partnerships**: {park_row['Partnerships']}  

> **Ranger Notes**: *{park_row['Ranger Notes']}*
""")

# Radar chart (optional bonus)
st.subheader("Radar Chart Comparison")
radar_df = filtered_df.set_index("Park")[["Threat Level", "Water Distribution", "Landscaping", "Neighborhoods", "Partnerships"]]
radar_df = radar_df.reset_index()

fig_radar = px.line_polar(
    radar_df.melt(id_vars="Park", var_name="Criteria", value_name="Score"),
    r="Score",
    theta="Criteria",
    color="Park",
    line_close=True
)
fig_radar.update_traces(fill='toself')
st.plotly_chart(fig_radar)
