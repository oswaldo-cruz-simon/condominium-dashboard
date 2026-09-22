import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(
    page_title="Financial Dashboard",
    layout="wide"
)


# =========================================================
# LOAD FINANCIAL DATA
# =========================================================

def load_financial_data(file_path):
    df = pd.read_csv(file_path)

    required_columns = {
        "month",
        "amount",
        "type"
    }

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Financial CSV must contain: {required_columns}"
        )

    df["month"] = pd.to_datetime(
        df["month"],
        format="%Y-%m"
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["month", "amount"]
    )

    return df.sort_values("month")


# =========================================================
# LOAD CHARGES DATA
# =========================================================

def load_charges_data(file_path):
    df = pd.read_csv(file_path)

    required_columns = {
        "month",
        "category",
        "amount"
    }

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Charges CSV must contain: {required_columns}"
        )

    df["month"] = pd.to_datetime(
        df["month"],
        format="%Y-%m"
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["month", "amount"]
    )

    return df.sort_values("month")


def load_debt_data(file_path):
    df = pd.read_csv(file_path)

    required_columns = {
        "casa",
        "main_debt_balance",
        "other_debt_balance",
        "total_debt"
    }

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Debt CSV must contain: {required_columns}"
        )

    numeric_columns = [
        "main_debt_balance",
        "other_debt_balance",
        "total_debt"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(
        subset=numeric_columns
    )

    return df.sort_values("total_debt")

# =========================================================
# CASHFLOW CHART
# =========================================================

def render_cashflow_balance_chart(df):

    st.subheader(
        "Income, Outcome, Balance & Expected Income"
    )

    # Income
    income_df = (
        df[df["type"] == "income"]
        .groupby("month", as_index=False)["amount"]
        .sum()
    )

    # Outcome
    outcome_df = (
        df[df["type"] == "outcome"]
        .groupby("month", as_index=False)["amount"]
        .sum()
    )

    # Balance
    balance_df = (
        df[df["type"] == "balance"]
        .groupby("month", as_index=False)["amount"]
        .sum()
    )

    # Expected income
    expected_income_df = (
        df[df["type"] == "expected_income"]
        .groupby("month", as_index=False)["amount"]
        .sum()
    )

    fig = go.Figure()

    # Income
    fig.add_trace(
        go.Bar(
            x=income_df["month"],
            y=income_df["amount"],
            name="Income",
            offsetgroup="income",
            marker_color="green",
            hovertemplate=(
                "%{x|%Y-%m}<br>"
                "Income<br>"
                "$%{y:,.2f}"
                "<extra></extra>"
            )
        )
    )

    # Outcome
    fig.add_trace(
        go.Bar(
            x=outcome_df["month"],
            y=outcome_df["amount"],
            name="Outcome",
            offsetgroup="outcome",
            marker_color="red",
            hovertemplate=(
                "%{x|%Y-%m}<br>"
                "Outcome<br>"
                "$%{y:,.2f}"
                "<extra></extra>"
            )
        )
    )

    # Balance
    fig.add_trace(
        go.Scatter(
            x=balance_df["month"],
            y=balance_df["amount"],
            name="Balance",
            mode="lines+markers",
            line=dict(width=3),
            hovertemplate=(
                "%{x|%Y-%m}<br>"
                "Balance<br>"
                "$%{y:,.2f}"
                "<extra></extra>"
            )
        )
    )

    # Expected Income
    fig.add_trace(
        go.Scatter(
            x=expected_income_df["month"],
            y=expected_income_df["amount"],
            name="Expected Income",
            mode="lines+markers",
            line=dict(
                width=2,
                dash="dash",
                color="blue"
            ),
            hovertemplate=(
                "%{x|%Y-%m}<br>"
                "Expected Income<br>"
                "$%{y:,.2f}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title=(
            "Monthly Income, Outcome, "
            "Balance & Expected Income"
        ),

        barmode="group",

        # Same scale for bars and lines
        yaxis=dict(
            title="Amount",
            tickprefix="$",
            separatethousands=True,
            rangemode="tozero"
        ),

        xaxis=dict(
            title="Month",
            dtick="M1",
            tickformat="%Y-%m"
        ),

        hovermode="x unified",
        height=600,

        legend=dict(
            title="Type"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# CHARGES CHART
# =========================================================

def render_charges_stacked_bar_chart(
    df,
    key_suffix=""
):

    st.subheader(
        "Monthly Charges by Category"
    )

    categories = (
        df["category"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_categories = st.multiselect(
        "Charge categories",
        options=categories,
        default=categories,
        key=f"charge_categories_{key_suffix}"
    )

    filtered_df = df[
        df["category"].isin(selected_categories)
    ].copy()

    if filtered_df.empty:
        st.warning("No categories selected.")
        return

    filtered_df = (
        filtered_df
        .groupby(
            ["month", "category"],
            as_index=False
        )["amount"]
        .sum()
    )

    # Don't create zero-value categories
    filtered_df = filtered_df[
        filtered_df["amount"] != 0
    ]

    if filtered_df.empty:
        st.warning("No non-zero data available.")
        return

    fig = px.bar(
        filtered_df,
        x="month",
        y="amount",
        color="category",
        barmode="relative",
        title="Monthly Charges by Category"
    )

    fig.update_traces(
        hovertemplate=(
            "%{x|%Y-%m}<br>"
            "%{fullData.name}<br>"
            "$%{y:,.2f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount",
        hovermode="x unified",
        height=600,
        legend_title="Category"
    )

    fig.update_xaxes(
        dtick="M1",
        tickformat="%Y-%m"
    )

    fig.update_yaxes(
        tickprefix="$",
        separatethousands=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

def render_debt_by_house_chart(df):
    """Render horizontal stacked debt chart using a symmetric log scale."""

    import numpy as np
    import plotly.graph_objects as go

    st.subheader("Debt by House")

    chart_df = (
        df.sort_values("total_debt", ascending=True)
        .copy()
    )

    chart_df["casa"] = chart_df["casa"].astype(str)

    # Symmetric logarithmic transformation.
    # Keeps negative and positive values while compressing large values.
    def symlog(x, linthresh=1000):
        return np.sign(x) * np.log10(
            1 + np.abs(x) / linthresh
        )

    chart_df["main_debt_log"] = chart_df["main_debt_balance"].apply(symlog)
    chart_df["other_debt_log"] = chart_df["other_debt_balance"].apply(symlog)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=chart_df["casa"],
            x=chart_df["main_debt_log"],
            customdata=chart_df["main_debt_balance"],
            name="Main Debt",
            orientation="h",
            hovertemplate=(
                "Casa %{y}<br>"
                "Main Debt<br>"
                "$%{customdata:,.2f}"
                "<extra></extra>"
            )
        )
    )

    fig.add_trace(
        go.Bar(
            y=chart_df["casa"],
            x=chart_df["other_debt_log"],
            customdata=chart_df["other_debt_balance"],
            name="Other Debt",
            orientation="h",
            hovertemplate=(
                "Casa %{y}<br>"
                "Other Debt<br>"
                "$%{customdata:,.2f}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title="Debt by House",
        barmode="relative",

        xaxis=dict(
            title="Debt (logarithmic scale)",
            zeroline=True,
            tickvals=[
                symlog(-150000),
                symlog(-100000),
                symlog(-50000),
                0,
                symlog(50000),
                symlog(100000),
                symlog(150000),
            ],
            ticktext=[
                "-$150K",
                "-$100K",
                "-$50K",
                "$0",
                "$50K",
                "$100K",
                "$150K",
            ],
        ),

        yaxis=dict(
            title="House",
            categoryorder="array",
            categoryarray=chart_df["casa"].tolist(),
        ),

        height=900,
        hovermode="closest",
        legend=dict(title="Debt Type"),
    )

    st.plotly_chart(fig, use_container_width=True)
# =========================================================
# MAIN
# =========================================================

def main():

    st.title("Financial Dashboard")

    tab1, tab2 = st.tabs([
        "Financial Dashboard",
        "Debt by House"
    ])

    # =====================================================
    # TAB 1 - FINANCIAL DASHBOARD
    # =====================================================

    with tab1:

        financial_df = load_financial_data(
            "data/financial.csv"
        )

        charges_df_1 = load_charges_data(
            "data/charges_1.csv"
        )

        charges_df_2 = load_charges_data(
            "data/charges_2.csv"
        )

        # Main cashflow chart
        render_cashflow_balance_chart(
            financial_df
        )

        # Two charges charts side-by-side
        col1, col2 = st.columns(2)

        with col1:
            render_charges_stacked_bar_chart(
                charges_df_1,
                key_suffix="1"
            )

        with col2:
            render_charges_stacked_bar_chart(
                charges_df_2,
                key_suffix="2"
            )

    # =====================================================
    # TAB 2 - DEBT
    # =====================================================

    with tab2:

        debt_df = load_debt_data(
            "data/debt.csv"
        )

        render_debt_by_house_chart(
            debt_df
        )

if __name__ == "__main__":
    main()