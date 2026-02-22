import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import plotly.express as px
import joblib
from datetime import datetime

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Smart Expense Tracker AI",
    page_icon="💸",
    layout="wide"
)

# =============================
# LOAD CSS
# =============================
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# =============================
# GALAXY BACKGROUND (100% WORKING)
# =============================
components.html(
    """
    <script>

    if (!window.galaxyLoaded) {

        window.galaxyLoaded = true;

        const canvas = parent.document.createElement("canvas");
        canvas.id = "galaxy-canvas";

        canvas.style.position = "fixed";
        canvas.style.top = "0";
        canvas.style.left = "0";
        canvas.style.width = "100vw";
        canvas.style.height = "100vh";
        canvas.style.zIndex = "-1";
        canvas.style.pointerEvents = "none";

        parent.document.body.appendChild(canvas);

        const ctx = canvas.getContext("2d");

        function resize() {
            canvas.width = parent.window.innerWidth;
            canvas.height = parent.window.innerHeight;
        }

        resize();
        parent.window.addEventListener("resize", resize);

        let layers = [
            { count: 250, speed: 0.2, size: 1 },
            { count: 200, speed: 0.5, size: 1.5 },
            { count: 150, speed: 1.0, size: 2 }
        ];

        let stars = [];

        layers.forEach(layer => {
            for (let i = 0; i < layer.count; i++) {
                stars.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    size: Math.random() * layer.size,
                    speed: layer.speed
                });
            }
        });

        let shootingStars = [];

        function createShootingStar() {

    const startX = Math.random() * canvas.width;
    const startY = -50; // start slightly above screen

    const speed = Math.random() * 4 + 6;

    shootingStars.push({
        x: startY,
        y: startX,
        length: Math.random() * 120 + 80,
        speedX: -speed * 0.7,   // diagonal left
        speedY: speed,          // falling down
        opacity: 1
    });
}

        setInterval(createShootingStar, 4000);

        function animate() {
            ctx.fillStyle = "black";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            stars.forEach(star => {

                ctx.globalAlpha = Math.random();
                ctx.beginPath();
                ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
                ctx.fillStyle = "white";
                ctx.fill();
                ctx.globalAlpha = 1;

                star.y += star.speed;

                if (star.y > canvas.height) {
                    star.y = 0;
                    star.x = Math.random() * canvas.width;
                }
            });

            shootingStars.forEach((s, index) => {

    const gradient = ctx.createLinearGradient(
        s.x, s.y,
        s.x - s.length, s.y + s.length
    );

    gradient.addColorStop(0, "rgba(255,255,255,1)");
    gradient.addColorStop(1, "rgba(255,255,255,0)");

    ctx.beginPath();
    ctx.moveTo(s.x, s.y);
    ctx.lineTo(s.x - s.length, s.y + s.length);
    ctx.strokeStyle = gradient;
    ctx.lineWidth = 3;
    ctx.stroke();

    // Glow effect
    ctx.shadowBlur = 15;
    ctx.shadowColor = "white";

    s.x += s.speedX;
    s.y += s.speedY;
    s.opacity -= 0.02;

    if (s.opacity <= 0) {
        shootingStars.splice(index, 1);
    }

    ctx.shadowBlur = 0; // Reset
});

            requestAnimationFrame(animate);
        }

        animate();
    }

    </script>
    """,
    height=0,
)

# =============================
# FILE PATHS
# =============================
FILE_PATH = "data/expenses.csv"
MODEL_PATH = "expense_model.pkl"
os.makedirs("data", exist_ok=True)

# =============================
# SIDEBAR NAVIGATION
# =============================
st.sidebar.title("📌 Navigation")
menu = st.sidebar.radio("Go to", ["Add Expense", "Dashboard"])

# =============================
# ADD EXPENSE PAGE
# =============================
if menu == "Add Expense":

    st.title("💸 Smart Expense Tracker AI")
    st.subheader("➕ Add New Expense")

    date = st.date_input("Date", datetime.today())
    amount = st.number_input("Amount", min_value=0.0)
    category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Other"])
    description = st.text_input("Description")

    if st.button("Add Expense"):
        new_data = pd.DataFrame([[date, amount, category, description]],
                                columns=["Date", "Amount", "Category", "Description"])

        if os.path.exists(FILE_PATH):
            new_data.to_csv(FILE_PATH, mode='a', header=False, index=False)
        else:
            new_data.to_csv(FILE_PATH, index=False)

        st.success("✅ Expense Added Successfully!")

# =============================
# DASHBOARD PAGE
# =============================
elif menu == "Dashboard":

    st.title("📊 AI Expense Dashboard")

    if os.path.exists(FILE_PATH):

        df = pd.read_csv(FILE_PATH)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Month"] = df["Date"].dt.to_period("M").astype(str)

        # Filters
        st.sidebar.subheader("🔎 Filter Data")

        min_date = df["Date"].min()
        max_date = df["Date"].max()

        date_range = st.sidebar.date_input(
            "Select Date Range",
            [min_date, max_date]
        )

        categories = df["Category"].unique()
        selected_categories = st.sidebar.multiselect(
            "Select Categories",
            categories,
            default=categories
        )

        filtered_df = df[
            (df["Date"] >= pd.to_datetime(date_range[0])) &
            (df["Date"] <= pd.to_datetime(date_range[1])) &
            (df["Category"].isin(selected_categories))
        ]

        monthly = filtered_df.groupby("Month")["Amount"].sum().reset_index()

        # KPIs
        col1, col2, col3, col4 = st.columns(4)

        total_spent = filtered_df["Amount"].sum()
        avg_spent = filtered_df["Amount"].mean() if len(filtered_df) > 0 else 0

        col1.metric("💰 Total Spending", f"₹ {total_spent:,.0f}")
        col2.metric("📊 Avg Transaction", f"₹ {avg_spent:,.0f}")
        col3.metric("📅 Transactions", len(filtered_df))
        col4.metric("📆 Months Tracked", len(monthly))

        st.markdown("---")

        tab1, tab2, tab3 = st.tabs([
            "📊 Analytics Dashboard",
            "🚨 Risk Monitoring",
            "🔮 AI Forecast"
        ])

        # ANALYTICS
        with tab1:

            category_data = filtered_df.groupby("Category")["Amount"].sum().reset_index()

            if not category_data.empty:
                fig1 = px.pie(category_data, names="Category", values="Amount", hole=0.5)
                st.plotly_chart(fig1, use_container_width=True)

            daily_data = filtered_df.groupby("Date")["Amount"].sum().reset_index()

            if not daily_data.empty:
                fig2 = px.line(daily_data, x="Date", y="Amount", markers=True)
                st.plotly_chart(fig2, use_container_width=True)

            if not monthly.empty:
                fig3 = px.bar(monthly, x="Month", y="Amount")
                st.plotly_chart(fig3, use_container_width=True)

        # RISK
        with tab2:

            st.subheader("🚨 Overspending Detection")

            if len(monthly) >= 4:
                current = monthly.iloc[-1]["Amount"]
                last_three_avg = monthly.iloc[-4:-1]["Amount"].mean()

                if current > 1.2 * last_three_avg:
                    st.error("⚠ You are overspending!")
                else:
                    st.success("✅ Spending is normal.")
            else:
                st.info("Not enough monthly data.")

            st.subheader("🔎 Anomaly Detection")

            if len(filtered_df) > 0:
                mean_amount = filtered_df["Amount"].mean()
                std_amount = filtered_df["Amount"].std()

                if std_amount != 0:
                    filtered_df = filtered_df.copy()
                    filtered_df["Z_Score"] = (
                        filtered_df["Amount"] - mean_amount
                    ) / std_amount

                    anomalies = filtered_df[abs(filtered_df["Z_Score"]) > 2.5]

                    if not anomalies.empty:
                        st.error("⚠ Unusual Transactions Detected!")
                        st.dataframe(
                            anomalies[["Date", "Amount", "Category", "Description"]]
                        )
                    else:
                        st.success("✅ No unusual transactions.")
                else:
                    st.info("Not enough variation.")
            else:
                st.info("No data available.")

        # FORECAST
        with tab3:

            st.subheader("🔮 Next Month Prediction (ARIMA)")

            if os.path.exists(MODEL_PATH):
                model_fit = joblib.load(MODEL_PATH)
                forecast = model_fit.forecast(steps=1)
                predicted_value = forecast.iloc[0]
                st.success(f"Predicted Next Month Expense: ₹ {predicted_value:,.2f}")
            else:
                st.warning("Train the ARIMA model first.")

    else:
        st.warning("No expense data found.")