# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: doctor/analytics.py
# PURPOSE: Patient and Revenue Analytics
# DATABASE: SQLite3
# GUI: CustomTkinter
# GRAPHS: Matplotlib
# OS: Ubuntu Linux
# ============================================================

import sqlite3
from datetime import date, timedelta

import customtkinter as ctk
import pandas as pd

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config import (
    BACKGROUND_COLOR,
    CARD_COLOR,
    PRIMARY_COLOR,
    PRIMARY_HOVER_COLOR,
    TEXT_COLOR,
    MUTED_TEXT_COLOR,
    BORDER_COLOR,
    ERROR_COLOR
)

from database import fetch_all, fetch_one


class AnalyticsScreen(ctk.CTkFrame):

    def __init__(self, parent, app):
        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app
        self.chart_canvases = []

        self.create_widgets()
        self.load_analytics()

    # ========================================================
    # 1. CREATE GUI
    # ========================================================

    def create_widgets(self):

        self.container = ctk.CTkScrollableFrame(
            self,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        # Header
        header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        header.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            header,
            text="Hospital Analytics",
            font=("Arial", 27, "bold"),
            text_color=TEXT_COLOR
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Refresh",
            width=110,
            height=40,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            command=self.load_analytics
        ).pack(side="right")

        # Date filter
        filter_card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )
        filter_card.pack(fill="x", pady=(0, 15))

        filter_row = ctk.CTkFrame(
            filter_card,
            fg_color="transparent"
        )
        filter_row.pack(
            fill="x",
            padx=20,
            pady=15
        )

        ctk.CTkLabel(
            filter_row,
            text="Select Period:",
            font=("Arial", 15, "bold"),
            text_color=TEXT_COLOR
        ).pack(side="left", padx=(0, 15))

        self.period_filter = ctk.CTkOptionMenu(
            filter_row,
            values=[
                "Last 7 Days",
                "Last 30 Days",
                "Last 90 Days",
                "This Year",
                "All Time"
            ],
            width=180,
            height=40,
            command=lambda value: self.load_analytics()
        )
        self.period_filter.pack(side="left")
        self.period_filter.set("Last 30 Days")

        # Summary cards
        self.summary_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        self.summary_frame.pack(fill="x", pady=(0, 15))

        self.summary_labels = {}

        summary_items = [
            ("Patient Visits", "visits"),
            ("New Patients", "patients"),
            ("Completed Visits", "completed"),
            ("Total Billing", "billing"),
            ("Collected Revenue", "revenue"),
            ("Outstanding", "outstanding")
        ]

        for index, (title, key) in enumerate(summary_items):

            self.summary_frame.grid_columnconfigure(
                index % 3,
                weight=1,
                uniform="analytics_cards"
            )

            row = index // 3
            column = index % 3

            card = ctk.CTkFrame(
                self.summary_frame,
                fg_color=CARD_COLOR,
                corner_radius=10,
                border_width=1,
                border_color=BORDER_COLOR
            )
            card.grid(
                row=row,
                column=column,
                padx=5,
                pady=5,
                sticky="nsew"
            )

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 14),
                text_color=MUTED_TEXT_COLOR
            ).pack(
                anchor="w",
                padx=18,
                pady=(15, 5)
            )

            value_label = ctk.CTkLabel(
                card,
                text="0",
                font=("Arial", 25, "bold"),
                text_color=PRIMARY_COLOR
            )
            value_label.pack(
                anchor="w",
                padx=18,
                pady=(0, 15)
            )

            self.summary_labels[key] = value_label

        # Chart sections
        self.charts_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        self.charts_frame.pack(fill="x")

        self.charts_frame.grid_columnconfigure(
            0, weight=1, uniform="charts"
        )
        self.charts_frame.grid_columnconfigure(
            1, weight=1, uniform="charts"
        )

        self.visits_chart = self.create_chart_card(
            "Patient Visit Trends", 0, 0
        )

        self.revenue_chart = self.create_chart_card(
            "Daily Revenue", 0, 1
        )

        self.gender_chart = self.create_chart_card(
            "Patient Gender Distribution", 1, 0
        )

        self.status_chart = self.create_chart_card(
            "Token Status Distribution", 1, 1
        )

        self.fees_chart = self.create_chart_card(
            "Consultation vs Medicine Fees", 2, 0
        )

        self.payment_chart = self.create_chart_card(
            "Payment Method Distribution", 2, 1
        )

        # Message
        self.message_label = ctk.CTkLabel(
            self.container,
            text="",
            font=("Arial", 14),
            text_color=ERROR_COLOR
        )
        self.message_label.pack(pady=10)

    # ========================================================
    # 2. CREATE CHART CARD
    # ========================================================

    def create_chart_card(self, title, row, column):

        card = ctk.CTkFrame(
            self.charts_frame,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )
        card.grid(
            row=row,
            column=column,
            padx=6,
            pady=7,
            sticky="nsew"
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 17, "bold"),
            text_color=TEXT_COLOR
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        chart_frame = ctk.CTkFrame(
            card,
            fg_color=CARD_COLOR,
            height=290
        )
        chart_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )
        chart_frame.pack_propagate(False)

        return chart_frame

    # ========================================================
    # 3. DATE FILTER
    # ========================================================

    def get_start_date(self):

        today = date.today()
        period = self.period_filter.get()

        if period == "Last 7 Days":
            return (today - timedelta(days=6)).isoformat()

        if period == "Last 30 Days":
            return (today - timedelta(days=29)).isoformat()

        if period == "Last 90 Days":
            return (today - timedelta(days=89)).isoformat()

        if period == "This Year":
            return date(today.year, 1, 1).isoformat()

        return None

    # ========================================================
    # 4. DATABASE DATA
    # ========================================================

    def get_count(self, table, date_column, extra_condition=""):

        allowed = {
            ("patients", "created_at"),
            ("visits", "visit_date")
        }

        if (table, date_column) not in allowed:
            raise ValueError("Invalid analytics table.")

        start_date = self.get_start_date()

        query = f"""
            SELECT COUNT(*) AS total
            FROM {table}
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += f" AND DATE({date_column}) >= ?"
            params.append(start_date)

        if extra_condition == "completed" and table == "visits":
            query += " AND status = 'Completed'"

        result = fetch_one(query, tuple(params))

        return result["total"] if result else 0

    def get_billing_totals(self):

        start_date = self.get_start_date()

        query = """
            SELECT
                COALESCE(SUM(total_amount), 0) AS billing,
                COALESCE(SUM(consultation_fee), 0) AS consultation,
                COALESCE(SUM(medicine_fee), 0) AS medicine,
                COALESCE(SUM(other_charges), 0) AS other_charges
            FROM bills
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(created_at) >= ?"
            params.append(start_date)

        return fetch_one(query, tuple(params))

    def get_payment_totals(self):

        start_date = self.get_start_date()

        query = """
            SELECT COALESCE(SUM(amount), 0) AS revenue
            FROM payments
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(paid_at) >= ?"
            params.append(start_date)

        return fetch_one(query, tuple(params))

    def get_daily_visits(self):

        start_date = self.get_start_date()

        query = """
            SELECT
                visit_date AS day,
                COUNT(*) AS total
            FROM visits
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND visit_date >= ?"
            params.append(start_date)

        query += """
            GROUP BY visit_date
            ORDER BY visit_date
        """

        return fetch_all(query, tuple(params))

    def get_daily_revenue(self):

        start_date = self.get_start_date()

        query = """
            SELECT
                DATE(paid_at) AS day,
                COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(paid_at) >= ?"
            params.append(start_date)

        query += """
            GROUP BY DATE(paid_at)
            ORDER BY day
        """

        return fetch_all(query, tuple(params))

    def get_gender_distribution(self):

        start_date = self.get_start_date()

        query = """
            SELECT
                gender,
                COUNT(*) AS total
            FROM patients
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(created_at) >= ?"
            params.append(start_date)

        query += """
            GROUP BY gender
            ORDER BY gender
        """

        return fetch_all(query, tuple(params))

    def get_token_status(self):

        start_date = self.get_start_date()

        query = """
            SELECT
                status,
                COUNT(*) AS total
            FROM visits
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND visit_date >= ?"
            params.append(start_date)

        query += """
            GROUP BY status
            ORDER BY status
        """

        return fetch_all(query, tuple(params))

    def get_payment_methods(self):

        start_date = self.get_start_date()

        query = """
            SELECT
                payment_method,
                COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE 1 = 1
        """

        params = []

        if start_date:
            query += " AND DATE(paid_at) >= ?"
            params.append(start_date)

        query += """
            GROUP BY payment_method
            ORDER BY payment_method
        """

        return fetch_all(query, tuple(params))

    # ========================================================
    # 5. UPDATE SUMMARY
    # ========================================================

    def update_summary(self):

        visits = self.get_count(
            "visits", "visit_date"
        )

        patients = self.get_count(
            "patients", "created_at"
        )

        completed = self.get_count(
            "visits", "visit_date", "completed"
        )

        billing = self.get_billing_totals()
        payments = self.get_payment_totals()

        billed_amount = float(billing["billing"])
        revenue = float(payments["revenue"])

        # Outstanding is calculated across all bills.
        # This avoids counting payments from older bills as
        # negative balances in the selected billing period.
        start_date = self.get_start_date()

        outstanding_query = """
            SELECT COALESCE(
                SUM(
                    MAX(
                        b.total_amount -
                        COALESCE(
                            (
                                SELECT SUM(p.amount)
                                FROM payments p
                                WHERE p.bill_id = b.id
                            ),
                            0
                        ),
                        0
                    )
                ),
                0
            ) AS outstanding
            FROM bills b
            WHERE 1 = 1
        """

        params = []

        if start_date:
            outstanding_query += " AND DATE(b.created_at) >= ?"
            params.append(start_date)

        outstanding_row = fetch_one(
            outstanding_query,
            tuple(params)
        )

        outstanding = float(
            outstanding_row["outstanding"] or 0
        )

        values = {
            "visits": str(visits),
            "patients": str(patients),
            "completed": str(completed),
            "billing": f"₹{billed_amount:,.2f}",
            "revenue": f"₹{revenue:,.2f}",
            "outstanding": f"₹{outstanding:,.2f}"
        }

        for key, value in values.items():
            self.summary_labels[key].configure(text=value)

    # ========================================================
    # 6. CREATE MATPLOTLIB FIGURE
    # ========================================================

    def create_figure(self):

        figure = Figure(
            figsize=(5, 3),
            dpi=90,
            facecolor="white"
        )

        axis = figure.add_subplot(111)

        return figure, axis

    def display_figure(self, parent, figure):

        for widget in parent.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(
            figure,
            master=parent
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        # Keep the canvas referenced while its screen exists.
        parent.chart_canvas = canvas

    @staticmethod
    def style_axis(axis):

        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.grid(axis="y", alpha=0.2)

    @staticmethod
    def show_no_data(axis):

        axis.text(
            0.5,
            0.5,
            "No data available",
            horizontalalignment="center",
            verticalalignment="center",
            transform=axis.transAxes,
            fontsize=12,
            color="#6B7280"
        )

        axis.set_xticks([])
        axis.set_yticks([])

    # ========================================================
    # 7. PATIENT VISITS GRAPH
    # ========================================================

    def draw_visits_chart(self):

        records = self.get_daily_visits()

        figure, axis = self.create_figure()

        if records:

            df = pd.DataFrame(records)

            df["day"] = pd.to_datetime(df["day"])

            start_date = self.get_start_date()

            if start_date:
                first_day = pd.Timestamp(start_date)
            else:
                first_day = df["day"].min()

            last_day = pd.Timestamp(date.today())

            dates = pd.date_range(
                start=first_day,
                end=last_day,
                freq="D"
            )

            df = (
                df.set_index("day")
                .reindex(dates, fill_value=0)
            )

            # Keep long time periods readable.
            if len(df) > 45:
                df = df.resample("MS").sum()

            labels = [
                day.strftime("%d %b")
                for day in df.index
            ]

            if len(df) > 45:
                labels = [
                    day.strftime("%b %Y")
                    for day in df.index
                ]

            values = df["total"].tolist()

            axis.plot(
                range(len(values)),
                values,
                marker="o" if len(values) <= 31 else None,
                linewidth=2,
                color=PRIMARY_COLOR
            )

            step = max(1, len(labels) // 7)

            ticks = list(range(0, len(labels), step))

            axis.set_xticks(ticks)
            axis.set_xticklabels(
                [labels[i] for i in ticks],
                rotation=30,
                fontsize=8
            )

            axis.set_ylabel("Patient Visits")
            axis.set_ylim(bottom=0)

            self.style_axis(axis)

        else:
            self.show_no_data(axis)

        figure.tight_layout()

        self.display_figure(
            self.visits_chart,
            figure
        )

    # ========================================================
    # 8. REVENUE GRAPH
    # ========================================================

    def draw_revenue_chart(self):

        records = self.get_daily_revenue()

        figure, axis = self.create_figure()

        if records:

            df = pd.DataFrame(records)

            df["day"] = pd.to_datetime(df["day"])

            start_date = self.get_start_date()

            if start_date:
                first_day = pd.Timestamp(start_date)
            else:
                first_day = df["day"].min()

            dates = pd.date_range(
                start=first_day,
                end=pd.Timestamp(date.today()),
                freq="D"
            )

            df = (
                df.set_index("day")
                .reindex(dates, fill_value=0)
            )

            if len(df) > 45:
                df = df.resample("MS").sum()
                labels = [
                    day.strftime("%b %Y")
                    for day in df.index
                ]
            else:
                labels = [
                    day.strftime("%d %b")
                    for day in df.index
                ]

            values = df["total"].tolist()

            axis.bar(
                range(len(values)),
                values,
                color=PRIMARY_COLOR,
                width=0.7
            )

            step = max(1, len(labels) // 7)
            ticks = list(range(0, len(labels), step))

            axis.set_xticks(ticks)

            axis.set_xticklabels(
                [labels[i] for i in ticks],
                rotation=30,
                fontsize=8
            )

            axis.set_ylabel("Revenue (INR)")

            self.style_axis(axis)

        else:
            self.show_no_data(axis)

        figure.tight_layout()

        self.display_figure(
            self.revenue_chart,
            figure
        )

    # ========================================================
    # 9. GENDER DISTRIBUTION
    # ========================================================

    def draw_gender_chart(self):

        records = self.get_gender_distribution()

        figure, axis = self.create_figure()

        if records:

            labels = [
                row["gender"]
                for row in records
            ]

            values = [
                row["total"]
                for row in records
            ]

            axis.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"fontsize": 10}
            )

            axis.axis("equal")

        else:
            self.show_no_data(axis)

        figure.tight_layout()

        self.display_figure(
            self.gender_chart,
            figure
        )

    # ========================================================
    # 10. TOKEN STATUS DISTRIBUTION
    # ========================================================

    def draw_status_chart(self):

        records = self.get_token_status()

        figure, axis = self.create_figure()

        if records:

            labels = [
                row["status"]
                for row in records
            ]

            values = [
                row["total"]
                for row in records
            ]

            positions = range(len(labels))

            axis.bar(
                positions,
                values,
                color=PRIMARY_COLOR
            )

            axis.set_xticks(list(positions))

            axis.set_xticklabels(
                labels,
                rotation=20,
                fontsize=9
            )

            axis.set_ylabel("Number of Tokens")

            self.style_axis(axis)

        else:
            self.show_no_data(axis)

        figure.tight_layout()

        self.display_figure(
            self.status_chart,
            figure
        )

    # ========================================================
    # 11. CONSULTATION VS MEDICINE FEES
    # ========================================================

    def draw_fees_chart(self):

        totals = self.get_billing_totals()

        figure, axis = self.create_figure()

        labels = [
            "Consultation",
            "Medicine",
            "Other"
        ]

        values = [
            float(totals["consultation"]),
            float(totals["medicine"]),
            float(totals["other_charges"])
        ]

        if any(value > 0 for value in values):

            axis.bar(
                labels,
                values,
                color=PRIMARY_COLOR,
                width=0.55
            )

            axis.set_ylabel("Amount (INR)")
            self.style_axis(axis)

        else:
            self.show_no_data(axis)

        figure.tight_layout()

        self.display_figure(
            self.fees_chart,
            figure
        )

    # ========================================================
    # 12. PAYMENT METHOD DISTRIBUTION
    # ========================================================

    def draw_payment_chart(self):

        records = self.get_payment_methods()

        figure, axis = self.create_figure()

        if records:

            labels = [
                row["payment_method"]
                for row in records
            ]

            values = [
                float(row["total"])
                for row in records
            ]

            if sum(values) > 0:

                axis.pie(
                    values,
                    labels=labels,
                    autopct="%1.1f%%",
                    startangle=90,
                    textprops={"fontsize": 10}
                )

                axis.axis("equal")

            else:
                self.show_no_data(axis)

        else:
            self.show_no_data(axis)

        figure.tight_layout()

        self.display_figure(
            self.payment_chart,
            figure
        )

    # ========================================================
    # 13. LOAD ALL ANALYTICS
    # ========================================================

    def load_analytics(self):

        try:

            self.message_label.configure(text="")

            self.update_summary()

            self.draw_visits_chart()
            self.draw_revenue_chart()
            self.draw_gender_chart()
            self.draw_status_chart()
            self.draw_fees_chart()
            self.draw_payment_chart()

        except (
            sqlite3.Error,
            ValueError,
            KeyError,
            TypeError
        ) as error:

            print("Analytics error:", error)

            self.message_label.configure(
                text="Unable to load analytics data."
            )

    # ========================================================
    # END OF ANALYTICS SCREEN
    # ========================================================


# ============================================================
# END OF FILE
# ============================================================
