import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="EduPro Learner Analytics",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    df = pd.read_csv("edupro_data.csv")

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert Age to numeric if available
    if "Age" in df.columns:
        df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

    # Convert TransactionDate to datetime
    if "TransactionDate" in df.columns:
        df["TransactionDate"] = pd.to_datetime(
            df["TransactionDate"],
            errors="coerce"
        )

    # Create AgeGroup if it does not already exist
    if "AgeGroup" not in df.columns and "Age" in df.columns:
        def create_age_group(age):
            if pd.isna(age):
                return "Unknown"
            elif age < 18:
                return "<18"
            elif age <= 25:
                return "18–25"
            elif age <= 35:
                return "26–35"
            elif age <= 45:
                return "36–45"
            else:
                return "45+"

        df["AgeGroup"] = df["Age"].apply(create_age_group)

    return df


try:
    df = load_data()
except Exception as e:
    st.error("Unable to load edupro_data.csv")
    st.error(f"Error: {e}")
    st.stop()


# ============================================================
# TITLE
# ============================================================

st.title("📊 EduPro Learner Demographics & Course Enrollment Analysis")

st.markdown(
    """
    **Interactive learner intelligence dashboard**

    This dashboard analyzes learner demographics and course enrollment
    behavior across age groups, gender, course categories, course levels,
    and course types.
    """
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🎯 Dashboard Filters")

# Age Group
if "AgeGroup" in df.columns:
    age_options = sorted(
        df["AgeGroup"].dropna().astype(str).unique().tolist()
    )
else:
    age_options = []

selected_age = st.sidebar.multiselect(
    "Age Group",
    options=age_options,
    default=age_options
)

# Gender
if "Gender" in df.columns:
    gender_options = sorted(
        df["Gender"].dropna().astype(str).unique().tolist()
    )
else:
    gender_options = []

selected_gender = st.sidebar.multiselect(
    "Gender",
    options=gender_options,
    default=gender_options
)

# Course Category
if "CourseCategory" in df.columns:
    category_options = sorted(
        df["CourseCategory"].dropna().astype(str).unique().tolist()
    )
else:
    category_options = []

selected_category = st.sidebar.multiselect(
    "Course Category",
    options=category_options,
    default=category_options
)

# Course Level
if "CourseLevel" in df.columns:
    level_options = sorted(
        df["CourseLevel"].dropna().astype(str).unique().tolist()
    )
else:
    level_options = []

selected_level = st.sidebar.multiselect(
    "Course Level",
    options=level_options,
    default=level_options
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()

if selected_age:
    filtered_df = filtered_df[
        filtered_df["AgeGroup"].astype(str).isin(selected_age)
    ]

if selected_gender:
    filtered_df = filtered_df[
        filtered_df["Gender"].astype(str).isin(selected_gender)
    ]

if selected_category:
    filtered_df = filtered_df[
        filtered_df["CourseCategory"].astype(str).isin(selected_category)
    ]

if selected_level:
    filtered_df = filtered_df[
        filtered_df["CourseLevel"].astype(str).isin(selected_level)
    ]


# ============================================================
# KPI SECTION
# ============================================================

st.subheader("📌 Key Performance Indicators")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

# Total enrollments
total_enrollments = len(filtered_df)

# Unique learners
if "UserID" in filtered_df.columns:
    unique_learners = filtered_df["UserID"].nunique()
else:
    unique_learners = 0

# Unique courses
if "CourseID" in filtered_df.columns:
    unique_courses = filtered_df["CourseID"].nunique()
else:
    unique_courses = 0

# Average courses per learner
if unique_learners > 0:
    avg_courses = total_enrollments / unique_learners
else:
    avg_courses = 0


kpi1.metric(
    "Total Enrollments",
    f"{total_enrollments:,}"
)

kpi2.metric(
    "Unique Learners",
    f"{unique_learners:,}"
)

kpi3.metric(
    "Unique Courses",
    f"{unique_courses:,}"
)

kpi4.metric(
    "Avg Courses / Learner",
    f"{avg_courses:.2f}"
)


st.divider()


# ============================================================
# AGE-WISE ENROLLMENT
# ============================================================

if "AgeGroup" in filtered_df.columns:

    st.subheader("1️⃣ Age-wise Enrollment")

    age_data = (
        filtered_df
        .groupby("AgeGroup")
        .size()
        .reset_index(name="Enrollments")
    )

    age_order = ["<18", "18–25", "26–35", "36–45", "45+"]

    age_data["AgeGroup"] = pd.Categorical(
        age_data["AgeGroup"],
        categories=age_order,
        ordered=True
    )

    age_data = age_data.sort_values("AgeGroup")

    fig_age = px.bar(
        age_data,
        x="AgeGroup",
        y="Enrollments",
        title="Enrollment Distribution by Age Group",
        text="Enrollments"
    )

    fig_age.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_age,
        use_container_width=True
    )


# ============================================================
# GENDER PARTICIPATION
# ============================================================

if "Gender" in filtered_df.columns:

    st.subheader("2️⃣ Gender Participation")

    gender_data = (
        filtered_df
        .groupby("Gender")
        .size()
        .reset_index(name="Enrollments")
    )

    fig_gender = px.pie(
        gender_data,
        names="Gender",
        values="Enrollments",
        title="Gender-wise Enrollment Distribution",
        hole=0.35
    )

    st.plotly_chart(
        fig_gender,
        use_container_width=True
    )


# ============================================================
# COURSE CATEGORY POPULARITY
# ============================================================

if "CourseCategory" in filtered_df.columns:

    st.subheader("3️⃣ Course Category Popularity")

    category_data = (
        filtered_df
        .groupby("CourseCategory")
        .size()
        .reset_index(name="Enrollments")
        .sort_values("Enrollments", ascending=False)
    )

    fig_category = px.bar(
        category_data,
        x="CourseCategory",
        y="Enrollments",
        title="Most Popular Course Categories",
        text="Enrollments"
    )

    fig_category.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# ============================================================
# COURSE LEVEL PREFERENCE
# ============================================================

if "CourseLevel" in filtered_df.columns:

    st.subheader("4️⃣ Course Level Preference")

    level_data = (
        filtered_df
        .groupby("CourseLevel")
        .size()
        .reset_index(name="Enrollments")
    )

    fig_level = px.bar(
        level_data,
        x="CourseLevel",
        y="Enrollments",
        title="Learner Preference by Course Level",
        text="Enrollments"
    )

    fig_level.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_level,
        use_container_width=True
    )


# ============================================================
# AGE × COURSE CATEGORY HEATMAP
# ============================================================

if "AgeGroup" in filtered_df.columns and "CourseCategory" in filtered_df.columns:

    st.subheader("5️⃣ Age Group × Course Category")

    heatmap_data = pd.crosstab(
        filtered_df["AgeGroup"],
        filtered_df["CourseCategory"]
    )

    fig_heatmap = px.imshow(
        heatmap_data,
        text_auto=True,
        aspect="auto",
        title="Enrollment Heatmap: Age Group vs Course Category"
    )

    st.plotly_chart(
        fig_heatmap,
        use_container_width=True
    )


# ============================================================
# GENDER × COURSE LEVEL
# ============================================================

if "Gender" in filtered_df.columns and "CourseLevel" in filtered_df.columns:

    st.subheader("6️⃣ Gender × Course Level")

    gender_level_data = (
        filtered_df
        .groupby(["Gender", "CourseLevel"])
        .size()
        .reset_index(name="Enrollments")
    )

    fig_gender_level = px.bar(
        gender_level_data,
        x="Gender",
        y="Enrollments",
        color="CourseLevel",
        barmode="group",
        title="Gender-wise Course Level Preference"
    )

    st.plotly_chart(
        fig_gender_level,
        use_container_width=True
    )


# ============================================================
# COURSE TYPE PREFERENCE
# ============================================================

if "CourseType" in filtered_df.columns:

    st.subheader("7️⃣ Course Type Preference")

    type_data = (
        filtered_df
        .groupby("CourseType")
        .size()
        .reset_index(name="Enrollments")
        .sort_values("Enrollments", ascending=False)
    )

    fig_type = px.bar(
        type_data,
        x="CourseType",
        y="Enrollments",
        title="Course Type Preference",
        text="Enrollments"
    )

    fig_type.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_type,
        use_container_width=True
    )


# ============================================================
# TOP 10 COURSES
# ============================================================

if "CourseName" in filtered_df.columns:

    st.subheader("8️⃣ Top 10 Most Enrolled Courses")

    top_courses = (
        filtered_df
        .groupby("CourseName")
        .size()
        .reset_index(name="Enrollments")
        .sort_values("Enrollments", ascending=False)
        .head(10)
    )

    top_courses = top_courses.sort_values(
        "Enrollments",
        ascending=True
    )

    fig_top_courses = px.bar(
        top_courses,
        x="Enrollments",
        y="CourseName",
        orientation="h",
        title="Top 10 Courses by Enrollment",
        text="Enrollments"
    )

    fig_top_courses.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_top_courses,
        use_container_width=True
    )


# ============================================================
# MONTHLY ENROLLMENT TREND
# ============================================================

if "TransactionDate" in filtered_df.columns:

    st.subheader("9️⃣ Monthly Enrollment Trend")

    monthly_data = filtered_df.dropna(
        subset=["TransactionDate"]
    ).copy()

    if not monthly_data.empty:

        monthly_data["Month"] = (
            monthly_data["TransactionDate"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_enrollment = (
            monthly_data
            .groupby("Month")
            .size()
            .reset_index(name="Enrollments")
        )

        fig_monthly = px.line(
            monthly_enrollment,
            x="Month",
            y="Enrollments",
            markers=True,
            title="Monthly Enrollment Trend"
        )

        st.plotly_chart(
            fig_monthly,
            use_container_width=True
        )


# ============================================================
# DATA TABLE
# ============================================================

st.subheader("🔎 Filtered Enrollment Data")

st.write(
    f"Showing **{len(filtered_df):,}** enrollment records."
)

st.dataframe(
    filtered_df,
    use_container_width=True
)


# ============================================================
# DOWNLOAD BUTTON
# ============================================================

st.subheader("⬇️ Download Data")

download_data = filtered_df.to_csv(index=False)

st.download_button(
    label="Download Filtered Data as CSV",
    data=download_data,
    file_name="edupro_filtered_data.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "EduPro Learner Demographics & Course Enrollment Behavior Analysis | "
    "Interactive Streamlit Dashboard"
)
