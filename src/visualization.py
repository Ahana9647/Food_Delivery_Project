import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")                       # save charts without opening windows
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from datetime import date

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

from config import PROCESSED_DATA_PATH, OUTPUT_DIR

# SETTINGS
FIGURE_DIR = Path(OUTPUT_DIR) / "figures"
TABLE_DIR = Path(OUTPUT_DIR) / "tables"
REPORT_DIR = Path(OUTPUT_DIR) / "reports"
REPORT_FILE = REPORT_DIR / "Food_Delivery_Visualization_Report.pdf"
for folder in (FIGURE_DIR, TABLE_DIR, REPORT_DIR):
    folder.mkdir(parents=True, exist_ok=True)


ONLY_DELIVERED = False

# Colours (one main colour, one highlight; red/green only for bad/good)
BLUE, ORANGE, GREEN, RED, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#e34948", "#8a8a85"

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": "#e6e6e3", "axes.titleweight": "bold", "axes.titlesize": 12,
})

# LOAD DATA
def load_data(path=PROCESSED_DATA_PATH):
    """Read the cleaned CSV and add helper columns used by the charts."""
    df = pd.read_csv(path)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="%d-%m-%Y")
    df["Month"] = df["Order_Date"].dt.month
    df["Hour"] = df["Order_Time"].str.slice(0, 2).astype(int)
    df["Delay_Min"] = df["Delivery_Time_Min"] - df["Expected_Delivery_Min"]
    return df


def performance_data(df):
    """Rows used for delivery-performance charts."""
    return df[df["Order_Status"] == "Delivered"] if ONLY_DELIVERED else df


def save(name):
    """Save the current chart as PNG in outputs/figures and close it."""
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / name, bbox_inches="tight", facecolor="white")
    plt.close()
    print("  saved chart:", name)


def label_bars_h(ax, fmt="{:.1f}"):
    """Write the value at the end of each horizontal bar."""
    for p in ax.patches:
        ax.annotate(fmt.format(p.get_width()),
                    (p.get_width(), p.get_y() + p.get_height() / 2),
                    va="center", ha="left", fontsize=9, xytext=(3, 0),
                    textcoords="offset points")


def label_bars_v(ax, fmt="{:.1f}"):
    """Write the value on top of each vertical bar."""
    for p in ax.patches:
        ax.annotate(fmt.format(p.get_height()),
                    (p.get_x() + p.get_width() / 2, p.get_height()),
                    ha="center", va="bottom", fontsize=9, xytext=(0, 3),
                    textcoords="offset points")



# CHARTS  (each function = one chart)
def chart_01_delivery_time_distribution(df):
    plt.figure(figsize=(8, 4.8))
    sns.histplot(df["Delivery_Time_Min"], bins=30, color=BLUE)
    avg = df["Delivery_Time_Min"].mean()
    plt.axvline(avg, color=ORANGE, linestyle="--", linewidth=2)
    plt.text(avg + 1, plt.ylim()[1] * 0.92, f"Average = {avg:.1f} min", color="#333")
    plt.title("Distribution of Delivery Time")
    plt.xlabel("Delivery time (minutes)")
    plt.ylabel("Number of orders")
    save("01_delivery_time_distribution.png")


def chart_02_on_time_vs_late(df):
    counts = df["On_Time"].map({1: "On time", 0: "Late"}).value_counts()
    plt.figure(figsize=(6, 4.8))
    ax = sns.barplot(x=counts.index, y=counts.values, hue=counts.index,
                     palette={"On time": GREEN, "Late": RED}, legend=False, width=0.5)
    for p, v in zip(ax.patches, counts.values):
        ax.annotate(f"{v:,}\n({v / len(df) * 100:.1f}%)",
                    (p.get_x() + p.get_width() / 2, p.get_height()),
                    ha="center", va="bottom", fontsize=10, xytext=(0, 3),
                    textcoords="offset points")
    plt.ylim(0, counts.max() * 1.18)
    plt.title("On-Time vs Late Deliveries")
    plt.xlabel("")
    plt.ylabel("Number of orders")
    save("02_on_time_vs_late.png")


def chart_03_avg_delivery_by_restaurant(df):
    avg = df.groupby("Restaurant")["Delivery_Time_Min"].mean().sort_values()
    plt.figure(figsize=(8, 5.5))
    ax = sns.barplot(x=avg.values, y=avg.index, color=BLUE)
    label_bars_h(ax)
    plt.xlim(0, avg.max() * 1.12)
    plt.title("Average Delivery Time by Restaurant")
    plt.xlabel("Average delivery time (minutes)")
    plt.ylabel("")
    save("03_avg_delivery_time_by_restaurant.png")


def chart_04_on_time_rate_by_restaurant(df):
    rate = (df.groupby("Restaurant")["On_Time"].mean() * 100).sort_values()
    colours = [RED] * 3 + [BLUE] * (len(rate) - 6) + [GREEN] * 3
    plt.figure(figsize=(8, 5.5))
    ax = sns.barplot(x=rate.values, y=rate.index, hue=rate.index,
                     palette=dict(zip(rate.index, colours)), legend=False)
    label_bars_h(ax, "{:.1f}%")
    plt.xlim(0, 100)
    plt.title("On-Time Delivery % by Restaurant  (green = top 3, red = bottom 3)")
    plt.xlabel("On-time deliveries (%)")
    plt.ylabel("")
    save("04_on_time_rate_by_restaurant.png")


def chart_05_distance_vs_delivery_time(df):
    sample = df.sample(min(3000, len(df)), random_state=1)
    corr = df["Distance_KM"].corr(df["Delivery_Time_Min"])
    plt.figure(figsize=(8, 4.8))
    sns.regplot(data=sample, x="Distance_KM", y="Delivery_Time_Min",
                scatter_kws={"alpha": 0.25, "s": 12, "color": BLUE},
                line_kws={"color": ORANGE, "linewidth": 2})
    plt.title(f"Distance vs Delivery Time  (correlation = {corr:.2f})")
    plt.xlabel("Distance (km)")
    plt.ylabel("Delivery time (minutes)")
    save("05_distance_vs_delivery_time.png")


def chart_06_delivery_time_by_distance_band(df):
    bands = pd.cut(df["Distance_KM"], bins=[0, 3, 6, 9, 12, 15, 20],
                   labels=["0-3", "3-6", "6-9", "9-12", "12-15", "15+"])
    avg = df.groupby(bands, observed=True)["Delivery_Time_Min"].mean()
    plt.figure(figsize=(8, 4.8))
    ax = sns.barplot(x=avg.index.astype(str), y=avg.values, color=BLUE, width=0.6)
    label_bars_v(ax)
    plt.title("Average Delivery Time by Distance Band")
    plt.xlabel("Distance band (km)")
    plt.ylabel("Average delivery time (minutes)")
    save("06_delivery_time_by_distance_band.png")


def chart_07_rating_vs_delivery_time(df):
    bands = pd.cut(df["Delivery_Time_Min"], bins=[0, 30, 45, 60, 75, 120],
                   labels=["under 30", "30-45", "45-60", "60-75", "75+"])
    plt.figure(figsize=(8, 4.8))
    sns.boxplot(x=bands, y=df["Rating"], color=BLUE, linewidth=1.2, fliersize=2)
    plt.title("Customer Rating by Delivery Time Band")
    plt.xlabel("Delivery time band (minutes)")
    plt.ylabel("Customer rating")
    save("07_rating_vs_delivery_time.png")


def chart_08_orders_by_hour(df):
    hourly = df.groupby("Hour")["Order_ID"].count()
    plt.figure(figsize=(9, 4.8))
    plt.plot(hourly.index, hourly.values, marker="o", color=BLUE, linewidth=2)
    peak = hourly.idxmax()
    plt.annotate(f"Peak hour: {peak}:00", (peak, hourly.max()), xytext=(0, 10),
                 textcoords="offset points", ha="center", color="#333")
    plt.ylim(0, hourly.max() * 1.15)
    plt.xticks(range(int(hourly.index.min()), int(hourly.index.max()) + 1))
    plt.title("Number of Orders by Hour of the Day")
    plt.xlabel("Hour (24-hour clock)")
    plt.ylabel("Number of orders")
    save("08_orders_by_hour.png")


def chart_09_monthly_orders(df):
    monthly = df.groupby("Month")["Order_ID"].count()
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    plt.figure(figsize=(9, 4.8))
    ax = sns.barplot(x=[names[m - 1] for m in monthly.index], y=monthly.values,
                     color=BLUE, width=0.6)
    label_bars_v(ax, "{:,.0f}")
    plt.ylim(0, monthly.max() * 1.12)
    plt.title("Monthly Order Volume")
    plt.xlabel("Month")
    plt.ylabel("Number of orders")
    save("09_monthly_orders.png")


def chart_10_order_status_and_vehicle(df):
    """Two small charts side by side: order status and delivery time by vehicle."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    status = df["Order_Status"].value_counts()
    sns.barplot(x=status.index, y=status.values, hue=status.index,
                palette={"Delivered": GREEN, "Cancelled": RED}, legend=False,
                width=0.5, ax=axes[0])
    for p, v in zip(axes[0].patches, status.values):
        axes[0].annotate(f"{v:,}\n({v / len(df) * 100:.1f}%)",
                         (p.get_x() + p.get_width() / 2, p.get_height()),
                         ha="center", va="bottom", fontsize=9, xytext=(0, 3),
                         textcoords="offset points")
    axes[0].set_ylim(0, status.max() * 1.2)
    axes[0].set_title("Order Status")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Number of orders")

    vehicle = df.groupby("Vehicle_Type")["Delivery_Time_Min"].mean().sort_values()
    sns.barplot(x=vehicle.index, y=vehicle.values, color=BLUE, width=0.55, ax=axes[1])
    for p in axes[1].patches:
        axes[1].annotate(f"{p.get_height():.1f}",
                         (p.get_x() + p.get_width() / 2, p.get_height()),
                         ha="center", va="bottom", fontsize=9, xytext=(0, 3),
                         textcoords="offset points")
    axes[1].set_ylim(0, vehicle.max() * 1.15)
    axes[1].set_title("Average Delivery Time by Vehicle")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Minutes")
    save("10_order_status_and_vehicle.png")


def chart_11_correlation_heatmap(df):
    cols = ["Distance_KM", "Preparation_Time_Min", "Delivery_Time_Min",
            "Expected_Delivery_Min", "Rating", "Order_Value", "Delivery_Fee"]
    plt.figure(figsize=(8, 6))
    sns.heatmap(df[cols].corr(), annot=True, fmt=".2f", cmap="Blues",
                vmin=0, vmax=1, linewidths=1, linecolor="white", cbar=False)
    plt.title("Correlation Between Numeric Fields")
    plt.xticks(rotation=35, ha="right")
    save("11_correlation_heatmap.png")


CHARTS = [
    chart_01_delivery_time_distribution, chart_02_on_time_vs_late,
    chart_03_avg_delivery_by_restaurant, chart_04_on_time_rate_by_restaurant,
    chart_05_distance_vs_delivery_time, chart_06_delivery_time_by_distance_band,
    chart_07_rating_vs_delivery_time, chart_08_orders_by_hour,
    chart_09_monthly_orders, chart_10_order_status_and_vehicle,
    chart_11_correlation_heatmap,
]


# SUMMARY TABLES  (CSV files - also load these into Power BI)
def build_tables(df):
    perf = performance_data(df)
    tables = {}

    tables["kpi_summary"] = pd.DataFrame({
        "KPI": ["Total orders", "Delivered orders", "Cancelled orders",
                "Average delivery time (min)", "On-time delivery (%)",
                "Late orders", "Average rating", "Average distance (km)",
                "Average preparation time (min)", "Average order value",
                "Average delivery fee"],
        "Value": [len(df), int((df["Order_Status"] == "Delivered").sum()),
                  int((df["Order_Status"] == "Cancelled").sum()),
                  round(perf["Delivery_Time_Min"].mean(), 2),
                  round(perf["On_Time"].mean() * 100, 2),
                  int((perf["On_Time"] == 0).sum()),
                  round(perf["Rating"].mean(), 2),
                  round(perf["Distance_KM"].mean(), 2),
                  round(perf["Preparation_Time_Min"].mean(), 2),
                  round(df["Order_Value"].mean(), 2),
                  round(df["Delivery_Fee"].mean(), 2)]})

    def group(by):
        out = perf.groupby(by).agg(
            Orders=("Order_ID", "count"),
            Avg_Delivery_Time=("Delivery_Time_Min", "mean"),
            On_Time_Percentage=("On_Time", "mean"),
            Avg_Rating=("Rating", "mean"),
            Avg_Distance=("Distance_KM", "mean")).reset_index()
        out["On_Time_Percentage"] *= 100
        return out.round(2)

    tables["restaurant_summary"] = group("Restaurant").sort_values("On_Time_Percentage", ascending=False)
    tables["city_summary"] = group("City")
    tables["vehicle_summary"] = group("Vehicle_Type")
    tables["monthly_summary"] = group("Month")
    tables["hourly_summary"] = group("Hour")

    for name, table in tables.items():
        table.to_csv(TABLE_DIR / f"{name}.csv", index=False)
        print("  saved table:", f"{name}.csv")
    return tables


# PDF REPORT  (created automatically from the charts and tables)
PDF_BLUE = colors.HexColor("#2a78d6")
styles = getSampleStyleSheet()
TITLE = ParagraphStyle("t", parent=styles["Title"], fontSize=26, leading=32, textColor=PDF_BLUE)
H1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, textColor=PDF_BLUE, spaceBefore=8)
H2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, spaceBefore=6)
BODY = ParagraphStyle("b", parent=styles["BodyText"], fontSize=10, leading=14)
CAPTION = ParagraphStyle("c", parent=BODY, fontSize=9, textColor=colors.HexColor("#52514e"))
CENTER = ParagraphStyle("ctr", parent=BODY, alignment=1)


def picture(filename, width_cm=16):
    """Insert a chart image scaled to the page width."""
    path = FIGURE_DIR / filename
    w, h = PILImage.open(path).size
    width = width_cm * cm
    return Image(str(path), width=width, height=width * h / w)


def table(data, col_widths=None):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PDF_BLUE), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cfcfca")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6f9")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "Food Delivery Order Performance Analysis - Visualization Report")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build_report():
    df = load_data()
    perf = performance_data(df)

    # ---- numbers used in the text (all calculated from the data) ----
    on_time = perf["On_Time"].mean() * 100
    avg_time = perf["Delivery_Time_Min"].mean()
    corr_dist = df["Distance_KM"].corr(df["Delivery_Time_Min"])
    corr_prep = df["Preparation_Time_Min"].corr(df["Delivery_Time_Min"])
    corr_rate = round(df["Rating"].corr(df["Delivery_Time_Min"]), 2) + 0.0
    rest = perf.groupby("Restaurant")["On_Time"].mean() * 100
    hourly = df.groupby("Hour")["Order_ID"].count()
    monthly = df.groupby("Month")["Order_ID"].count()
    month_names = ["January", "February", "March", "April", "May", "June", "July",
                   "August", "September", "October", "November", "December"]
    vehicle = perf.groupby("Vehicle_Type")["Delivery_Time_Min"].mean()
    near = perf[perf["Distance_KM"] <= 3]["Delivery_Time_Min"].mean()
    far = perf[perf["Distance_KM"] > 15]["Delivery_Time_Min"].mean()
    cancel = (df["Order_Status"] == "Cancelled").mean() * 100
    scope = "delivered orders only" if ONLY_DELIVERED else "all orders in the cleaned file"

    story = []

    # ---------------- cover page ----------------
    story += [Spacer(1, 5 * cm),
              Paragraph("Food Delivery Order<br/>Performance Analysis", TITLE),
              Spacer(1, 0.5 * cm),
              Paragraph("Data Visualization Report", H1),
              Spacer(1, 1 * cm),
              Paragraph("Group C - DataVerse", BODY),
              Paragraph("Repository: Ahana9647/Food_Delivery_Project", BODY),
              Paragraph(f"Generated automatically on {date.today():%d %B %Y}", BODY),
              Paragraph(f"Records analysed: {len(df):,} orders, 17 original fields", BODY),
              PageBreak()]

    # ---------------- 1. overview ----------------
    story += [Paragraph("1. Purpose and Method", H1),
              Paragraph("This report presents the visual analysis of the cleaned food delivery "
                        "dataset (<i>data/processed/cleaned_food_delivery_orders.csv</i>). "
                        "All charts were created in Python using Pandas, Matplotlib and Seaborn "
                        "and this PDF was generated automatically by "
                        "<i>src/visualization.py</i>. The same summary tables are saved in "
                        "<i>outputs/tables/</i> and loaded into Power BI for the interactive dashboard.", BODY),
              Spacer(1, 0.2 * cm),
              Paragraph(f"Scope of delivery-performance charts: {scope}.", BODY),
              Spacer(1, 0.4 * cm),
              Paragraph("2. Key Performance Indicators", H1)]
    kpi = pd.read_csv(Path(OUTPUT_DIR) / "tables" / "kpi_summary.csv")

    def fmt(v):
        v = float(v)
        return f"{v:,.0f}" if v.is_integer() and v >= 100 else f"{v:,.2f}"

    rows = [["KPI", "Value"]] + [[r.KPI, fmt(r.Value)] for r in kpi.itertuples()]
    story += [table(rows, [9 * cm, 5 * cm]), PageBreak()]

    # ---------------- 3. charts ----------------
    story.append(Paragraph("3. Charts and Findings", H1))

    def block(title, filename, text):
        story.append(KeepTogether([Paragraph(title, H2), picture(filename),
                                   Paragraph(text, CAPTION), Spacer(1, 0.5 * cm)]))

    block("3.1 Delivery time distribution", "01_delivery_time_distribution.png",
          f"The average delivery time is {avg_time:.1f} minutes. Most orders fall between "
          f"{perf['Delivery_Time_Min'].quantile(.25):.0f} and {perf['Delivery_Time_Min'].quantile(.75):.0f} "
          f"minutes (middle 50% of orders).")
    block("3.2 On-time vs late deliveries", "02_on_time_vs_late.png",
          f"{on_time:.1f}% of orders were delivered within the expected time and "
          f"{100 - on_time:.1f}% were late.")
    block("3.3 Average delivery time by restaurant", "03_avg_delivery_time_by_restaurant.png",
          f"Restaurant averages range only from {perf.groupby('Restaurant')['Delivery_Time_Min'].mean().min():.1f} "
          f"to {perf.groupby('Restaurant')['Delivery_Time_Min'].mean().max():.1f} minutes, so no restaurant "
          f"is clearly faster than the others.")
    block("3.4 On-time delivery % by restaurant", "04_on_time_rate_by_restaurant.png",
          f"On-time rates range from {rest.min():.1f}% ({rest.idxmin()}) to {rest.max():.1f}% "
          f"({rest.idxmax()}). The gap is only {rest.max() - rest.min():.1f} percentage points, so the "
          f"top/bottom ranking should not be treated as strong evidence of a real difference.")
    block("3.5 Distance vs delivery time", "05_distance_vs_delivery_time.png",
          f"The correlation is {corr_dist:.2f}: longer distance is strongly associated with longer delivery. "
          f"Correlation does not prove cause.")
    block("3.6 Delivery time by distance band", "06_delivery_time_by_distance_band.png",
          f"Orders within 3 km average {near:.1f} minutes, while orders over 15 km average {far:.1f} minutes.")
    block("3.7 Rating by delivery time band", "07_rating_vs_delivery_time.png",
          f"The correlation between delivery time and rating is {corr_rate:.2f}, so in this dataset "
          f"ratings do not change with delivery time.")
    block("3.8 Orders by hour of the day", "08_orders_by_hour.png",
          f"Order volume is highest at {hourly.idxmax()}:00 ({hourly.max():,} orders) and lowest at "
          f"{hourly.idxmin()}:00 ({hourly.min():,} orders).")
    block("3.9 Monthly order volume", "09_monthly_orders.png",
          f"{month_names[monthly.idxmax() - 1]} has the most orders ({monthly.max():,}) and "
          f"{month_names[monthly.idxmin() - 1]} the fewest ({monthly.min():,}).")
    block("3.10 Order status and vehicle type", "10_order_status_and_vehicle.png",
          f"{cancel:.1f}% of orders were cancelled. Average delivery time is almost the same for every "
          f"vehicle type ({vehicle.min():.1f} to {vehicle.max():.1f} minutes).")
    block("3.11 Correlation heatmap", "11_correlation_heatmap.png",
          f"Distance ({corr_dist:.2f}) and preparation time ({corr_prep:.2f}) are the two fields most "
          f"related to delivery time. Rating, order value and delivery fee show almost no relation to it.")

    # ---------------- 4. findings ----------------
    story += [PageBreak(), Paragraph("4. Summary of Findings", H1)]
    for line in [
        f"Distance is the main driver of delivery time (correlation {corr_dist:.2f}); preparation time is a smaller driver ({corr_prep:.2f}).",
        f"About {on_time:.1f}% of orders arrive on time, so roughly {100 - on_time:.0f} in 100 orders are late.",
        f"The restaurants perform very similarly: on-time rates differ by only {rest.max() - rest.min():.1f} percentage points.",
        f"Customer rating is not related to delivery time (correlation {corr_rate:.2f}).",
        f"Demand peaks at {hourly.idxmax()}:00 and in {month_names[monthly.idxmax() - 1]}.",
    ]:
        story.append(Paragraph("&bull; " + line, BODY))

    story += [Spacer(1, 0.4 * cm), Paragraph("5. Limitations", H1)]
    for line in [
        "Charts show association, not cause.",
        "Restaurant differences are very small, so rankings may reflect chance.",
        "The dataset may be synthetic or simulated, so results may not match a real platform.",
        "Weather, traffic and rider availability are not in the data.",
    ]:
        story.append(Paragraph("&bull; " + line, BODY))

    story += [Spacer(1, 0.4 * cm), Paragraph("6. Power BI Dashboard", H1),
              Paragraph("The interactive Power BI dashboard is built from the same cleaned CSV and the "
                        "summary tables in <i>outputs/tables/</i>. Dashboard screenshots can be added here.", BODY)]

# ---- 6. POWER BI DASHBOARD (added) ----
    from pathlib import Path as _Path
    _styles = getSampleStyleSheet()
    _shot_dir = _Path(OUTPUT_DIR) / "powerbi"
    _shots = sorted(p for p in _shot_dir.glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg")) if _shot_dir.exists() else []
    story.append(PageBreak())
    story.append(Paragraph("6. Power BI Dashboard", _styles["Heading1"]))
    story.append(Paragraph("The interactive Power BI dashboard was built from the same cleaned CSV file. "
                           "Screenshots of the dashboard are shown below.", _styles["BodyText"]))
    story.append(Spacer(1, 0.3 * cm))
    for _n, _shot in enumerate(_shots, 1):
        _w, _h = PILImage.open(_shot).size
        story.append(KeepTogether([Image(str(_shot), width=16 * cm, height=16 * cm * _h / _w),
                                   Paragraph(f"Figure: Power BI dashboard, view {_n}", _styles["Italic"]),
                                   Spacer(1, 0.4 * cm)]))


    doc = SimpleDocTemplate(str(REPORT_FILE), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title="Food Delivery Visualization Report", author="Group C - DataVerse")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("PDF report saved:", REPORT_FILE)
    return REPORT_FILE


# RUN EVERYTHING  (charts + tables + PDF report)
def run_visualization():
    print("Loading data from:", PROCESSED_DATA_PATH)
    df = load_data()
    perf = performance_data(df)
    print(f"Creating {len(CHARTS)} charts ...")
    for chart in CHARTS:
        # status chart needs all rows; the others use the performance rows
        chart(df if chart is chart_10_order_status_and_vehicle else perf)
    print("Creating summary tables ...")
    tables = build_tables(df)
    print("Creating PDF report ...")
    build_report()
    print("Visualization finished.")
    return df, tables


if __name__ == "__main__":
    run_visualization()
