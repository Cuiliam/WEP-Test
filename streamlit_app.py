import streamlit as st
import pandas as pd
import plotly.express as px

# ----------- Sample Data (You can later load this from a CSV) -----------

data = {
    "Park": ["Hemlock Bluffs", "Dunham Park", "Fred G. Bond", "Thomas Brooks", "Carpenter"],
    "Threat Level": [8, 6, 7, 6, 8],
    "Water Distribution": [5, 0, 3, 1, 2],
    "Landscaping": [2, 7, 5, 6, 9],
    "Private Property": [4, 8, 8, 3, 3],
    "Partnerships": [8, 8, 6, 2, 9],
    "Most Concerning Invasive Species": [
        "Chinese Privet, Japanese Stiltgrass, Bamboo",
        "Mimosa Tree, Privet, Japanese Honey Suckle",
        "English Ivy, Japanese Privet, Nandina",
        "English Ivy, Autumn Olive, Japanese Privet",
        "Dogfennel, Broomsedge, Privet"
    ],
    "Current Efforts": [
        "Privet: hand pull small shrubs; Cut and Paint large shrubs. Will likely need to come back retreat a few times.\nJapanese Stiltgrass:  It is very widespread and difficult to tackle. We hand pull small sections and mow small sections where we can. Hand pulling is very easy because the the root system is weak. If we had A LOT of volunteers we may be able to make a dent in the stiltgrass through hand pulling. However, handpulling needs to happen in the summer months. The same time that copperheads, yellow jackets and mosquitoes are active, so I have not done this yet.  Foliar spray is another treatment method , but because the stiltgrass is mixed in with native plants and/or near water, I do not want to spray herbicide.\nBamboo: Very difficult to remove! Due to the bamboo being so close to Swift Creek, the only option I have come across so far is to cut and paint the bamboo, although even that will likely not be super effective. Another obstacle is the size and amount of bamboo. Much of the patch bamboo is 30ft tall. Removing the bamboo and figuring out what to do with all the biomass is just as big of a hurdle as treating it.",
        "Privet & Mimosa: cutting to base and then direct application of glyphosate.\nHoneysuckle: removal of bulb from ground (digging up and hand weeding)",
        "English Ivy: requires hand pulling or mowing and spraying, burning would also work, but difficult in this area.\nPrivet: cut and sprayed.\nNandina: cut or dug up.",
        "English Ivy: requires hand pulling or mowing and spraying.\nAutumn Olive: cut and sprayed.\nJapanese Privet: cut and sprayed.\nMay also need to replant an understory depending on the severity of the population.",
        "Targeted application of glycophate."
    ]
}

df = pd.DataFrame(data)
df["Total Score"] = df["Threat Level"] + df["Water Distribution"] + (
    df["Landscaping"] + df["Partnerships"] - df["Private Property"]
)
df = df.sort_values("Total Score", ascending=False)

# ---------------- STREAMLIT UI ----------------
st.title("Town of Cary Invasive Species Priority Dashboard")

# Sidebar
with st.sidebar:
    st.header("Filters")
    selected_parks = st.multiselect("Select parks to view", df["Park"].tolist(), default=df["Park"].tolist())

# Filter data
filtered_df = df[df["Park"].isin(selected_parks)]

# Calculate Feasibility and Urgency
df["Feasibility"] = df["Landscaping"] + df["Partnerships"] - df["Private Property"]
df["Urgency"] = df["Threat Level"] + df["Water Distribution"]
scatter_df = df[df["Park"].isin(selected_parks)]

# Use medians to define quadrant cutoffs
x_median = scatter_df["Feasibility"].mean()
y_median = scatter_df["Urgency"].mean()

# Create Scatter Plot
fig_scatter = px.scatter(
    scatter_df,
    x="Feasibility",
    y="Urgency",
    text="Park",
    color="Park",
    size="Threat Level",
    hover_data=["Threat Level", "Water Distribution", "Landscaping", "Private Property", "Partnerships"]
)

# Add quadrant lines
fig_scatter.add_shape(type="line", x0=x_median, x1=x_median, y0=scatter_df["Urgency"].min()-2, y1=scatter_df["Urgency"].max()+2,
                      line=dict(color="White", dash="dash"))
fig_scatter.add_shape(type="line", x0=scatter_df["Feasibility"].min()-6, x1=scatter_df["Feasibility"].max()+2, y0=y_median, y1=y_median,
                      line=dict(color="White", dash="dash"))

# Add annotations for quadrant labels
fig_scatter.add_annotation(x=x_median + 7, y=y_median + 4,
                           text="Quick Wins<br>(High Feasibility, High Urgency)", showarrow=False, bgcolor="lightgreen", font=dict(color="black"))
fig_scatter.add_annotation(x=x_median - 7, y=y_median + 4,
                           text="Difficult but Urgent<br>(Low Feasibility, High Urgency)", showarrow=False, bgcolor="khaki", font=dict(color="black"))
fig_scatter.add_annotation(x=x_median - 7, y=y_median - 4,
                           text="Lower Priority<br>(Low Feasibility, Low Urgency)", showarrow=False, bgcolor="lightgray", font=dict(color="black"))
fig_scatter.add_annotation(x=x_median + 7, y=y_median - 4,
                           text="Easy but Not Urgent<br>(High Feasibility, Low Urgency)", showarrow=False, bgcolor="salmon", font=dict(color="black"))

# Update layout
fig_scatter.update_traces(textposition='top center')
fig_scatter.update_layout(
    xaxis_title="Feasibility (Landscaping + Partnerships - Private Property)",
    yaxis_title="Urgency (Threat Level + Water Distribution)",
    title="Invasive Species Action Priority Matrix"
)

st.plotly_chart(fig_scatter)

# Display Prioritization Matrix
st.subheader("Prioritization Table")
st.dataframe(filtered_df.set_index("Park").style.background_gradient(axis=0, cmap="YlOrRd"))

# Show total ranking chart
st.subheader("Overall Priority Ranking")
fig = px.bar(filtered_df, x="Park", y="Total Score", color="Total Score", text="Total Score", color_continuous_scale='Reds')
st.plotly_chart(fig)

# Radar chart (optional bonus)
st.subheader("Radar Chart Comparison")
radar_df = filtered_df.set_index("Park")[["Threat Level", "Water Distribution", "Landscaping", "Private Property", "Partnerships"]]
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

# Detailed info per park
st.subheader("Park Detail Viewer")
park_choice = st.selectbox("Select a park to view details", df["Park"])
park_row = df[df["Park"] == park_choice].iloc[0]

st.markdown(f"""
### {park_choice}
- **Threat Level**: {park_row['Threat Level']}  
- **Water Distribution**: {park_row['Water Distribution']}  
- **Landscaping**: {park_row['Landscaping']}  
- **Private Property**: {park_row['Private Property']}  
- **Partnerships**: {park_row['Partnerships']}  

> **Most Concerning Invasive Species**: *{park_row['Most Concerning Invasive Species']}*
\n> **Current Efforts**: *{park_row['Current Efforts']}*
""")
