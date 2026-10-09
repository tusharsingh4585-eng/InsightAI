from io import BytesIO
import pandas as pd

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace("-", "_")
        for c in df.columns
    ]
    return df

def pick_column(df, candidates):
    for col in df.columns:
        if col in candidates:
            return col
    return None

def analyze_csv(raw: bytes):
    df = normalize_columns(pd.read_csv(BytesIO(raw)))

    if df.empty:
        raise ValueError("CSV file contains no data rows.")

    quantity_col = pick_column(
        df, {"quantity", "qty", "units", "units_sold"}
    )
    price_col = pick_column(
        df, {"unit_price", "price", "selling_price", "sale_price"}
    )
    cost_col = pick_column(
        df, {"cost", "unit_cost", "cost_price", "purchase_price"}
    )
    revenue_col = pick_column(
        df, {"revenue", "sales", "amount", "total_sales", "total_revenue"}
    )
    profit_col = pick_column(
        df, {"profit", "net_profit", "gross_profit"}
    )

    for col in [quantity_col, price_col, cost_col, revenue_col, profit_col]:
        if col:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if revenue_col:
        revenue_values = df[revenue_col]
    elif quantity_col and price_col:
        revenue_values = df[quantity_col] * df[price_col]
    else:
        revenue_values = pd.Series(0.0, index=df.index)

    if profit_col:
        profit_values = df[profit_col]
    elif quantity_col and price_col and cost_col:
        profit_values = df[quantity_col] * (df[price_col] - df[cost_col])
    else:
        profit_values = pd.Series(0.0, index=df.index)

    revenue = float(revenue_values.sum())
    profit = float(profit_values.sum())
    margin = profit / revenue * 100 if revenue else 0.0

    insights = []
    if revenue:
        insights.append(f"Total revenue is {revenue:,.2f}.")
    if revenue and (profit_col or (quantity_col and price_col and cost_col)):
        insights.append(f"Overall profit margin is {margin:.1f}%.")

    date_col = pick_column(
        df, {"date", "order_date", "sales_date", "created_at"}
    )
    trend = []

    if date_col:
        dates = pd.to_datetime(df[date_col], errors="coerce")
        temp = pd.DataFrame({"date": dates, "revenue": revenue_values})
        temp = temp.dropna(subset=["date"])
        if not temp.empty:
            temp["month"] = temp["date"].dt.to_period("M").astype(str)
            monthly = temp.groupby("month", as_index=False)["revenue"].sum()
            trend = monthly.rename(columns={"month": "date"}).to_dict("records")

    insights.append(
        f"Dataset contains {len(df)} rows and {len(df.columns)} columns."
    )

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "revenue_total": round(revenue, 2),
        "profit_total": round(profit, 2),
        "profit_margin": round(margin, 2),
        "columns_list": list(df.columns),
        "insights": insights,
        "trend": trend,
    }