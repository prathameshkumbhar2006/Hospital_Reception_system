# ============================================================
# HOSPITAL RECEPTION SYSTEM
# FILE: doctor/dashboard.py
# PURPOSE: Doctor Dashboard and Analytics
# DATABASE: SQLite3
# GUI: CustomTkinter
# GRAPHS: Matplotlib
# ============================================================

import sqlite3

from datetime import date

import customtkinter as ctk

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
    SUCCESS_COLOR,
    ERROR_COLOR,
    DASHBOARD_REFRESH_INTERVAL
)

from database import fetch_one, fetch_all


# ============================================================
# DOCTOR DASHBOARD
# ============================================================

class DashboardScreen(ctk.CTkFrame):

    def __init__(self, parent, app):

        super().__init__(
            parent,
            fg_color=BACKGROUND_COLOR,
            corner_radius=0
        )

        self.app = app

        self.refresh_job = None

        self.stat_labels = {}

        self.create_widgets()

        self.load_dashboard()

        self.schedule_refresh()

    # ========================================================
    # 1. CREATE GUI
    # ========================================================

    def create_widgets(self):

        # ----------------------------------------------------
        # SCROLLABLE MAIN CONTENT
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        self.header = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.header.pack(
            fill="x",
            pady=(0, 20)
        )

        self.title_frame = ctk.CTkFrame(
            self.header,
            fg_color="transparent"
        )

        self.title_frame.pack(side="left")

        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="Dashboard",
            font=("Arial", 28, "bold"),
            text_color=TEXT_COLOR
        )

        self.title_label.pack(anchor="w")

        self.welcome_label = ctk.CTkLabel(
            self.title_frame,
            text=f"Welcome, {self.app.doctor_name}",
            font=("Arial", 15),
            text_color=MUTED_TEXT_COLOR
        )

        self.welcome_label.pack(
            anchor="w",
            pady=(5, 0)
        )

        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.header,
            text="Refresh",
            width=110,
            height=40,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            font=("Arial", 14, "bold"),
            command=self.load_dashboard
        )

        self.refresh_button.pack(
            side="right",
            padx=5
        )

        # ----------------------------------------------------
        # ERROR MESSAGE
        # ----------------------------------------------------

        self.message_label = ctk.CTkLabel(
            self.container,
            text="",
            font=("Arial", 13),
            text_color=ERROR_COLOR,
            anchor="w",
            height=20
        )

        self.message_label.pack(
            fill="x",
            pady=(0, 5)
        )

        # ----------------------------------------------------
        # STATISTICS CARDS
        # ----------------------------------------------------

        self.stats_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.stats_frame.pack(
            fill="x",
            pady=(0, 20)
        )

        for column in range(3):
            self.stats_frame.grid_columnconfigure(
                column,
                weight=1,
                uniform="stat"
            )

        self.create_stat_card(
            "Total Patients",
            "total_patients",
            0,
            0
        )

        self.create_stat_card(
            "Today's Patients",
            "today_patients",
            0,
            1
        )

        self.create_stat_card(
            "Waiting Patients",
            "waiting_patients",
            0,
            2
        )

        self.create_stat_card(
            "Completed Today",
            "completed_patients",
            1,
            0
        )

        self.create_stat_card(
            "Today's Revenue",
            "today_revenue",
            1,
            1
        )

        self.create_stat_card(
            "Total Revenue",
            "total_revenue",
            1,
            2
        )

        # ----------------------------------------------------
        # QUICK ACTIONS
        # ----------------------------------------------------

        self.actions_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.actions_frame.pack(
            fill="x",
            pady=(0, 20)
        )

        self.tokens_button = ctk.CTkButton(
            self.actions_frame,
            text="View Today's Tokens",
            width=190,
            height=42,
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER_COLOR,
            command=self.app.show_tokens
        )

        self.tokens_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.patients_button = ctk.CTkButton(
            self.actions_frame,
            text="Patient Records",
            width=160,
            height=42,
            fg_color=CARD_COLOR,
            hover_color="#E5E7EB",
            text_color=TEXT_COLOR,
            border_width=1,
            border_color=BORDER_COLOR,
            command=self.app.show_patients
        )

        self.patients_button.pack(side="left")

        # ----------------------------------------------------
        # CHARTS SECTION
        # ----------------------------------------------------

        self.graphs_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.graphs_frame.pack(
            fill="x",
            pady=(0, 20)
        )

        self.graphs_frame.grid_columnconfigure(
            0,
            weight=1,
            uniform="graphs"
        )

        self.graphs_frame.grid_columnconfigure(
            1,
            weight=1,
            uniform="graphs"
        )

        # Patient visits chart
        self.visits_card = self.create_chart_card(
            "Patient Visits - Last 7 Days",
            0
        )

        # Revenue chart
        self.revenue_card = self.create_chart_card(
            "Revenue - Last 7 Days",
            1
        )

        # ----------------------------------------------------
        # RECENT PATIENTS
        # ----------------------------------------------------

        self.recent_card = ctk.CTkFrame(
            self.container,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )

        self.recent_card.pack(
            fill="x",
            pady=(0, 20)
        )

        self.recent_title = ctk.CTkLabel(
            self.recent_card,
            text="Recent Patient Visits",
            font=("Arial", 20, "bold"),
            text_color=TEXT_COLOR
        )

        self.recent_title.pack(
            anchor="w",
            padx=20,
            pady=(15, 10)
        )

        self.recent_table = ctk.CTkFrame(
            self.recent_card,
            fg_color="transparent"
        )

        self.recent_table.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

    # ========================================================
    # 2. CREATE STATISTICS CARD
    # ========================================================

    def create_stat_card(
        self,
        title,
        key,
        row,
        column
    ):

        card = ctk.CTkFrame(
            self.stats_frame,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )

        card.grid(
            row=row,
            column=column,
            padx=6,
            pady=6,
            sticky="nsew"
        )

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 14),
            text_color=MUTED_TEXT_COLOR
        )

        title_label.pack(
            anchor="w",
            padx=18,
            pady=(15, 5)
        )

        value_label = ctk.CTkLabel(
            card,
            text="0",
            font=("Arial", 27, "bold"),
            text_color=PRIMARY_COLOR
        )

        value_label.pack(
            anchor="w",
            padx=18,
            pady=(0, 15)
        )

        self.stat_labels[key] = value_label

    # ========================================================
    # 3. CREATE CHART CARD
    # ========================================================

    def create_chart_card(self, title, column):

        card = ctk.CTkFrame(
            self.graphs_frame,
            fg_color=CARD_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR
        )

        card.grid(
            row=0,
            column=column,
            padx=6,
            pady=5,
            sticky="nsew"
        )

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 17, "bold"),
            text_color=TEXT_COLOR
        )

        title_label.pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        chart_frame = ctk.CTkFrame(
            card,
            fg_color=CARD_COLOR
        )

        chart_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        if column == 0:
            self.visits_chart_frame = chart_frame
        else:
            self.revenue_chart_frame = chart_frame

        return card

    # ========================================================
    # 4. GET DASHBOARD STATISTICS
    # ========================================================

    def get_statistics(self):

        today = date.today().isoformat()

        # Total registered patients
        total_patients = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM patients
            """
        )

        # Today's patient visits
        today_patients = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM visits
            WHERE visit_date = ?
            """,
            (today,)
        )

        # Waiting patients today
        waiting_patients = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM visits
            WHERE visit_date = ?
              AND status = 'Waiting'
            """,
            (today,)
        )

        # Completed consultations today
        completed_patients = fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM visits
            WHERE visit_date = ?
              AND status = 'Completed'
            """,
            (today,)
        )

        # Today's revenue
        today_revenue = fetch_one(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE DATE(paid_at) = ?
            """,
            (today,)
        )

        # Total collected revenue
        total_revenue = fetch_one(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM payments
            """
        )

        return {
            "total_patients": total_patients["total"],
            "today_patients": today_patients["total"],
            "waiting_patients": waiting_patients["total"],
            "completed_patients": completed_patients["total"],
            "today_revenue": today_revenue["total"],
            "total_revenue": total_revenue["total"]
        }

    # ========================================================
    # 5. UPDATE STATISTICS CARDS
    # ========================================================

    def update_statistics(self, statistics):

        for key, value in statistics.items():

            if key in [
                "today_revenue",
                "total_revenue"
            ]:

                formatted_value = f"₹{value:,.2f}"

            else:

                formatted_value = str(value)

            self.stat_labels[key].configure(
                text=formatted_value
            )

    # ========================================================
    # 6. GET PATIENT VISIT CHART DATA
    # ========================================================

    def get_patient_chart_data(self):

        rows = fetch_all(
            """
            WITH RECURSIVE dates(day) AS (
                SELECT DATE('now', 'localtime', '-6 days')

                UNION ALL

                SELECT DATE(day, '+1 day')
                FROM dates
                WHERE day < DATE('now', 'localtime')
            )

            SELECT
                dates.day AS visit_day,
                COUNT(visits.id) AS total

            FROM dates

            LEFT JOIN visits
                ON visits.visit_date = dates.day

            GROUP BY dates.day

            ORDER BY dates.day
            """
        )

        labels = [
            row["visit_day"][5:]
            for row in rows
        ]

        values = [
            row["total"]
            for row in rows
        ]

        return labels, values

    # ========================================================
    # 7. GET REVENUE CHART DATA
    # ========================================================

    def get_revenue_chart_data(self):

        rows = fetch_all(
            """
            WITH RECURSIVE dates(day) AS (
                SELECT DATE('now', 'localtime', '-6 days')

                UNION ALL

                SELECT DATE(day, '+1 day')
                FROM dates
                WHERE day < DATE('now', 'localtime')
            )

            SELECT
                dates.day AS revenue_day,
                COALESCE(SUM(payments.amount), 0) AS total

            FROM dates

            LEFT JOIN payments
                ON DATE(payments.paid_at) = dates.day

            GROUP BY dates.day

            ORDER BY dates.day
            """
        )

        labels = [
            row["revenue_day"][5:]
            for row in rows
        ]

        values = [
            row["total"]
            for row in rows
        ]

        return labels, values

    # ========================================================
    # 8. DRAW MATPLOTLIB GRAPH
    # ========================================================

    def draw_graph(
        self,
        parent,
        labels,
        values,
        graph_type="line"
    ):

        # Remove previous graph
        for widget in parent.winfo_children():
            widget.destroy()

        # Create Matplotlib figure
        figure = Figure(
            figsize=(5, 3),
            dpi=85,
            facecolor="white"
        )

        axis = figure.add_subplot(111)

        x_positions = list(range(len(labels)))

        # Patient visits line graph
        if graph_type == "line":

            axis.plot(
                x_positions,
                values,
                marker="o",
                linewidth=2,
                color="#2563EB"
            )

            axis.set_ylabel(
                "Patients",
                fontsize=10
            )

            axis.set_ylim(
                bottom=0
            )

        # Revenue bar graph
        else:

            axis.bar(
                x_positions,
                values,
                color="#2563EB",
                width=0.6
            )

            axis.set_ylabel(
                "Revenue (INR)",
                fontsize=10
            )

            axis.set_ylim(
                bottom=0
            )

        axis.set_xticks(x_positions)

        axis.set_xticklabels(
            labels,
            rotation=30,
            fontsize=8
        )

        axis.grid(
            axis="y",
            alpha=0.2
        )

        axis.spines["top"].set_visible(False)

        axis.spines["right"].set_visible(False)

        figure.tight_layout()

        # Embed Matplotlib into CustomTkinter
        canvas = FigureCanvasTkAgg(
            figure,
            master=parent
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        # Close the figure when its parent is destroyed
        def cleanup(event):

            if event.widget == parent:
                figure.clear()

        parent.bind("<Destroy>", cleanup, add="+")

    # ========================================================
    # 9. UPDATE GRAPHS
    # ========================================================

    def update_graphs(self):

        # Patient visits graph
        visit_labels, visit_values = (
            self.get_patient_chart_data()
        )

        self.draw_graph(
            self.visits_chart_frame,
            visit_labels,
            visit_values,
            "line"
        )

        # Revenue graph
        revenue_labels, revenue_values = (
            self.get_revenue_chart_data()
        )

        self.draw_graph(
            self.revenue_chart_frame,
            revenue_labels,
            revenue_values,
            "bar"
        )

    # ========================================================
    # 10. GET RECENT PATIENTS
    # ========================================================

    def get_recent_patients(self):

        return fetch_all(
            """
            SELECT
                v.id,
                v.token_number,
                p.name AS patient_name,
                v.visit_date,
                v.visit_time,
                v.status

            FROM visits v

            JOIN patients p
                ON v.patient_id = p.id

            ORDER BY
                v.visit_date DESC,
                v.visit_time DESC,
                v.id DESC

            LIMIT 8
            """
        )

    # ========================================================
    # 11. CREATE TABLE CELL
    # ========================================================

    def create_table_cell(
        self,
        parent,
        text,
        row,
        column,
        bold=False,
        color=None
    ):

        label = ctk.CTkLabel(
            parent,
            text=str(text),
            font=(
                "Arial",
                13,
                "bold" if bold else "normal"
            ),
            text_color=color or TEXT_COLOR,
            anchor="w"
        )

        label.grid(
            row=row,
            column=column,
            padx=10,
            pady=8,
            sticky="w"
        )

    # ========================================================
    # 12. UPDATE RECENT PATIENTS TABLE
    # ========================================================

    def update_recent_patients(self):

        # Clear old table
        for widget in self.recent_table.winfo_children():
            widget.destroy()

        columns = [
            "Token",
            "Patient Name",
            "Date",
            "Time",
            "Status"
        ]

        for column in range(len(columns)):

            self.recent_table.grid_columnconfigure(
                column,
                weight=1
            )

            self.create_table_cell(
                self.recent_table,
                columns[column],
                0,
                column,
                bold=True
            )

        patients = self.get_recent_patients()

        if not patients:

            no_records_label = ctk.CTkLabel(
                self.recent_table,
                text="No patient visits found.",
                font=("Arial", 14),
                text_color=MUTED_TEXT_COLOR
            )

            no_records_label.grid(
                row=1,
                column=0,
                columnspan=5,
                pady=20
            )

            return

        # Display actual database records
        for row_index, patient in enumerate(
            patients,
            start=1
        ):

            status = patient["status"]

            if status == "Completed":
                status_color = SUCCESS_COLOR

            elif status == "Waiting":
                status_color = PRIMARY_COLOR

            elif status == "Cancelled":
                status_color = ERROR_COLOR

            else:
                status_color = "#D97706"

            values = [
                patient["token_number"],
                patient["patient_name"],
                patient["visit_date"],
                patient["visit_time"],
                status
            ]

            for column_index, value in enumerate(values):

                self.create_table_cell(
                    self.recent_table,
                    value,
                    row_index,
                    column_index,
                    color=(
                        status_color
                        if column_index == 4
                        else TEXT_COLOR
                    )
                )

    # ========================================================
    # 13. LOAD DASHBOARD
    # ========================================================

    def load_dashboard(self):

        try:

            self.message_label.configure(text="")

            # Load statistics
            statistics = self.get_statistics()

            self.update_statistics(statistics)

            # Load charts
            self.update_graphs()

            # Load recent records
            self.update_recent_patients()

        except sqlite3.Error as error:

            print("Dashboard database error:", error)

            self.message_label.configure(
                text="Unable to load dashboard data."
            )

        except Exception as error:

            print("Dashboard error:", error)

            self.message_label.configure(
                text="An error occurred while loading the dashboard."
            )

    # ========================================================
    # 14. AUTOMATIC REFRESH
    # ========================================================

    def schedule_refresh(self):

        if not self.winfo_exists():
            return

        self.refresh_job = self.after(
            DASHBOARD_REFRESH_INTERVAL,
            self.auto_refresh
        )

    def auto_refresh(self):

        self.refresh_job = None

        if not self.winfo_exists():
            return

        self.load_dashboard()

        self.schedule_refresh()

    # ========================================================
    # 15. CLEANUP
    # ========================================================

    def destroy(self):

        if self.refresh_job is not None:

            try:
                self.after_cancel(self.refresh_job)

            except ValueError:
                pass

            self.refresh_job = None

        super().destroy()


# ============================================================
# END OF FILE
# ============================================================
