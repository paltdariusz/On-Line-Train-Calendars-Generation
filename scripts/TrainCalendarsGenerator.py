import customtkinter as ctk
import tkinter
from tkinter import messagebox
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import os
import sys
from pathlib import Path
import numpy as np
from tkcalendar import Calendar
from PIL import Image

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.CreateClusters import ClusterGenerator, ClusterConfig
from src.MCSolver import solve_set_cover, SolverConfig


@dataclass
class DateRange:
    """
    Represents a validated date range.

    Attributes:
        start: Start date
        end: End date
        year: Year for which the range is valid
    """

    start: date
    end: date
    year: int = 2021

    def __post_init__(self):
        """Validate date range after initialization."""
        if self.end < self.start:
            raise ValueError("Start date must be before end date")
        if self.start.year != self.year or self.end.year != self.year:
            raise ValueError(f"Dates must be in year {self.year}")

    @property
    def day_indices(self) -> Tuple[int, int]:
        """Get day indices (1-based) for the date range."""
        return (self.start.timetuple().tm_yday, self.end.timetuple().tm_yday)


class CalendarState:
    """
    Manages application state and selected dates.

    Attributes:
        picked_ids: Dictionary tracking selected dates and their IDs
        date_range: Current selected date range
        clusters: Generated clusters data
    """

    def __init__(self):
        self.picked_ids: Dict[str, List] = {
            "dates": [],
        }
        self.date_range: Optional[DateRange] = None
        self.clusters: Optional[Tuple] = None

    def clear(self) -> None:
        """Reset state to initial values."""
        self.__init__()

    def add_date(self, selected_date: datetime) -> None:
        """
        Add a date to the picked dates.

        Args:
            selected_date: Date to add
        """
        if selected_date not in self.picked_ids["dates"]:
            self.picked_ids["dates"].append(selected_date)

    def remove_date(self, selected_date: datetime) -> None:
        """
        Remove a date from picked dates.

        Args:
            selected_date: Date to remove
        """
        if selected_date in self.picked_ids["dates"]:
            self.picked_ids["dates"].remove(selected_date)


class CalendarPopup(ctk.CTkToplevel):
    """
    Custom calendar popup window.

    Attributes:
        parent: Parent window
        entry: Entry widget to update with selected date
        initial_date: Initial date to show in calendar
    """

    def __init__(self, parent: ctk.CTk, entry: ctk.CTkEntry, initial_date: date):
        super().__init__(parent)
        self.entry = entry
        self.setup_window()
        self.create_calendar(initial_date)

    def setup_window(self) -> None:
        """Configure main window properties."""
        self.title("Train Calendar Generator")
        self.geometry("800x600")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Load icon if available
        icon_path = project_root / "assets" / "calendar.gif"
        if icon_path.exists():
            try:
                icon_image = tkinter.PhotoImage(file=str(icon_path))
                self.iconphoto(True, icon_image)
            except Exception as e:
                print(f"Error loading icon: {e}")

    def create_calendar(self, initial_date: date) -> None:
        """
        Create and configure calendar widget.

        Args:
            initial_date: Date to initially select in calendar
        """
        self.calendar = Calendar(
            self,
            selectmode="day",
            year=initial_date.year,
            month=initial_date.month,
            day=initial_date.day,
            date_pattern="dd/mm/yyyy",
        )
        self.calendar.pack(pady=10, expand=True, fill="both")

        # Add selection button
        ctk.CTkButton(self, text="Select", command=self.select_date).pack(pady=5)

    def select_date(self) -> None:
        """Handle date selection and update entry."""
        selected = datetime.strptime(self.calendar.get_date(), "%d/%m/%Y").date()
        print(f"Selected date string: {selected}")
        self.entry.delete(0, "end")
        self.entry.insert(0, selected.strftime("%d/%m/%Y"))  # Ensure consistent format
        self.destroy()


class CalendarApp(ctk.CTk):
    """
    Main application window.

    Attributes:
        state: Application state manager
        cluster_config: Configuration for cluster generation
    """

    def __init__(self, cluster_config: Optional[ClusterConfig] = None):
        super().__init__()

        self.calendar_state = CalendarState()
        self.cluster_config = cluster_config or ClusterConfig(year=2021)

        self.setup_window()
        self.create_widgets()

    def setup_window(self) -> None:
        """Configure main window properties."""
        self.title("Train Calendar Generator")
        self.geometry("800x600")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Modified icon loading code
        # Load icon if available
        icon_path = project_root / "assets" / "calendar.gif"
        if icon_path.exists():
            try:
                icon_image = tkinter.PhotoImage(file=str(icon_path))
                self.iconphoto(True, icon_image)
            except Exception as e:
                print(f"Error loading icon: {e}")

    def set_date_range(self) -> None:
        """Validate and set the selected date range."""
        try:
            start_date = datetime.strptime(self.start_date.get(), "%d/%m/%Y").date()
            end_date = datetime.strptime(self.end_date.get(), "%d/%m/%Y").date()

            self.calendar_state.date_range = DateRange(start_date, end_date)

            # Generate clusters after setting date range
            cluster_generator = ClusterGenerator(self.cluster_config)
            self.calendar_state.clusters = cluster_generator.create_clusters(
                *self.calendar_state.date_range.day_indices
            )

            # Clear existing calendar frame and show calendar
            for widget in self.calendar_frame.winfo_children():
                widget.destroy()

            self.show_calendar()

        except ValueError as e:
            self.show_error(str(e))

    def show_error(self, message: str) -> None:
        """Display error message to user."""
        messagebox.showerror("Error", message)

    def show_calendar(self) -> None:
        """Show calendar after date range is set."""
        if not self.calendar_state.date_range:
            return

        self.calendar = Calendar(
            self.calendar_frame,
            selectmode="day",
            year=self.calendar_state.date_range.year,
            month=self.calendar_state.date_range.start.month,
            # day=self.calendar_state.date_range.start.day,
            date_pattern="dd/mm/yyyy",
            multiselect=True,
            mindate=self.calendar_state.date_range.start,
            maxdate=self.calendar_state.date_range.end,
            selectbackground="red",
            selectforeground="blue",
        )
        self.calendar.pack(pady=20, expand=True, fill="both")
        self.calendar.bind("<<CalendarSelected>>", self.on_date_select)

    def on_date_select(self, event=None) -> None:
        """Handle date selection in calendar."""
        if self.calendar_state.date_range is None:
            self.show_error("Please set a date range first.")
            return

        selected_date_str = self.calendar.get_date()
        selected = datetime.strptime(selected_date_str, "%d/%m/%Y").date()
        # Validate date is within range
        if (
            selected < self.calendar_state.date_range.start
            or selected > self.calendar_state.date_range.end
        ):
            self.show_error("Please select dates within the specified range")
            return

        if selected in self.calendar_state.picked_ids["dates"]:
            self.calendar_state.remove_date(selected)
            # Visually deselect date by removing the event
            cids = self.calendar.get_calevents(date=selected)
            for cid in cids:
                self.calendar.calevent_remove(cid)
        else:
            self.calendar_state.add_date(selected)
            # Visually select date by creating an event with a tag
            self.calendar.calevent_create(
                selected, "Selected Date", tags="selected_date"
            )

        # Update calendar display to configure the appearance of selected dates
        self.update_calendar_display()

    def update_calendar_display(self) -> None:
        """Update calendar appearance based on selected dates."""
        self.calendar.tag_config("selected_date", background="red", foreground="blue")

    def create_widgets(self) -> None:
        """Create and arrange UI widgets."""
        self.create_date_selection_frame()
        self.create_calendar_frame()
        self.create_button_frame()

    def create_date_selection_frame(self) -> None:
        """Create frame for date range selection."""
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="x")

        self.start_date = self.create_date_picker(frame, "Start Date", 0)
        self.end_date = self.create_date_picker(frame, "End Date", 1)

        ctk.CTkButton(frame, text="Set Date Range", command=self.set_date_range).grid(
            row=2, column=0, columnspan=3, pady=10
        )

    def create_calendar_frame(self) -> None:
        """Create frame for calendar display."""
        self.calendar_frame = ctk.CTkFrame(self)
        self.calendar_frame.pack(pady=20, padx=20, expand=True, fill="both")

    def create_button_frame(self) -> None:
        """Create frame for action buttons."""
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="x")

        ctk.CTkButton(frame, text="Calculate Results", command=self.show_results).pack(
            side="left", padx=5
        )

        ctk.CTkButton(frame, text="Clear Selection", command=self.clear_selection).pack(
            side="right", padx=5
        )

    def create_date_picker(
        self, frame: ctk.CTkFrame, label: str, row: int
    ) -> ctk.CTkEntry:
        """
        Create a date picker widget with label and entry field.

        Args:
            frame: Parent frame
            label: Label text
            row: Grid row number

        Returns:
            Entry widget for date input
        """
        ctk.CTkLabel(frame, text=label).grid(row=row, column=0, padx=5, pady=5)

        entry = ctk.CTkEntry(frame)
        entry.grid(row=row, column=1, padx=5, pady=5)

        ctk.CTkButton(
            frame, text="Select", command=lambda e=entry: self.show_calendar_popup(e)
        ).grid(row=row, column=2, padx=5, pady=5)

        return entry

    def show_calendar_popup(self, entry: ctk.CTkEntry) -> None:
        """
        Show calendar popup for date selection.

        Args:
            entry: Entry widget to update with selected date
        """
        try:
            initial_date = datetime.strptime(entry.get(), "%d/%m/%Y").date()
        except ValueError:
            initial_date = date(self.cluster_config.year, 1, 1)

        CalendarPopup(self, entry, initial_date)

    def show_results(self) -> None:
        """Show results window with calculations."""
        if not self.calendar_state.date_range:
            self.show_error("Please set a date range first")
            return

        if not self.calendar_state.picked_ids["dates"]:
            self.show_error("Please select at least one date")
            return

        try:
            ResultWindow(parent=self, calendar_state=self.calendar_state)
        except Exception as e:
            self.show_error(f"Error calculating results: {str(e)}")

    def clear_selection(self) -> None:
        """Clear all selected dates."""
        if hasattr(self, "calendar"):
            self.calendar.calevent_remove("all")
        self.show_calendar()


class ResultWindow(ctk.CTkToplevel):
    """
    Window for displaying calculation results.

    Attributes:
        parent: Parent window
        calendar_state: Application state
        solver_config: Configuration for the solver
    """

    def __init__(
        self,
        parent: ctk.CTk,
        calendar_state: CalendarState,
        solver_config: Optional[SolverConfig] = None,
    ):
        super().__init__(parent)
        self.calendar_state = calendar_state
        self.solver_config = solver_config or SolverConfig()
        self.setup_window()
        self.calculate_and_display_results()

    def setup_window(self) -> None:
        """Configure result window properties."""
        self.title("Results")
        self.geometry("600x400")
        self.grab_set()  # Make window modal

    def calculate_and_display_results(self) -> None:
        """Calculate and display results based on selected dates."""
        if not self.calendar_state.date_range or not self.calendar_state.clusters:
            self.show_error("No date range or clusters available")
            return

        try:
            result_text = self.generate_result_text()
            self.display_result(result_text)
        except Exception as e:
            self.show_error(f"Error calculating results: {str(e)}")

    def generate_result_text(self) -> str:
        """
        Generate formatted result text.

        Returns:
            Formatted string containing calculation results
        """
        clusters, names, dates = self.calendar_state.clusters
        periodicity = self.calculate_periodicity()

        if len(periodicity) == 0:
            return self.generate_no_service_text()

        processed_clusters = self.process_clusters(clusters, dates)
        results = solve_set_cover(
            set(periodicity), processed_clusters, self.solver_config
        )

        return self.format_results(results, names, periodicity)

    def calculate_periodicity(self) -> np.ndarray:
        """
        Calculate periodicity based on selected dates.

        Returns:
            Array of day indices where service is needed
        """
        start_idx, end_idx = self.calendar_state.date_range.day_indices
        period_length = end_idx - start_idx + 1

        selected_indices = [
            date.timetuple().tm_yday for date in self.calendar_state.picked_ids["dates"]
        ]

        periodicity = np.array(
            [
                day_idx
                for day_idx in range(start_idx, end_idx + 1)
                if day_idx not in selected_indices
            ]
        )

        return periodicity

    def process_clusters(
        self, clusters: np.ndarray, dates: np.ndarray
    ) -> List[Set[int]]:
        """
        Process clusters into sets for solver.

        Args:
            clusters: Array of cluster data
            dates: Array of date indices

        Returns:
            List of sets representing processed clusters
        """
        processed = np.multiply(clusters, dates).astype(int).tolist()
        return [set(filter((0).__ne__, cluster)) for cluster in processed]

    def format_results(
        self, results: List[Set[int]], names: List[str], periodicity: np.ndarray
    ) -> str:
        """
        Format results into human-readable text.

        Args:
            results: List of result sets
            names: List of cluster names
            periodicity: Array of day indices

        Returns:
            Formatted result text
        """
        if not results:
            return self.generate_no_service_text()

        # Get cluster names for results
        result_names = []
        result_union = set()

        processed_clusters = self.process_clusters(
            self.calendar_state.clusters[0], self.calendar_state.clusters[2]
        )

        for result_set in results:
            try:
                idx = processed_clusters.index(result_set)
                name = names[idx]
                result_names.append(name)
                result_union |= result_set
            except ValueError:
                continue
        print(f"results: {results}")
        print(f"processed_clusters: {processed_clusters}")

        print(f"result_names: {result_names}")
        print(f"result_union: {result_union}")
        print(f"names: {names}")

        # Format text
        service_text = self.format_service_text(result_names)
        date_range_text = self.format_date_range_text()
        exception_text = self.format_exception_text(result_union, set(periodicity))

        return f"{service_text} {date_range_text} {exception_text}".strip()

    def format_service_text(self, names: List[str]) -> str:
        """Format service provision text."""
        if not names:
            return "No service is provided"

        elif len(names) == 1:
            return f"The service is provided on {names[0]}"

        elif len(names) == 2:
            return f"The service is provided on {names[0]} and {names[1]}"

        *first, last = names
        msg = (
            f"The service is provided on {', '.join(first)}, and {last}"
            if first[0] != "from"
            else f"The service is provided {first[0]} {', '.join(first[1:])}, and {last}"
        )
        return msg

    def format_date_range_text(self) -> str:
        """Format date range text."""
        start = self.calendar_state.date_range.start.strftime("%d/%m/%Y")
        end = self.calendar_state.date_range.end.strftime("%d/%m/%Y")
        return f"from {start} to {end}"

    def format_exception_text(
        self, result_union: Set[int], periodicity: Set[int]
    ) -> str:
        """Format exception text for missing or extra days."""
        days_to_exclude = sorted(result_union - periodicity)
        days_to_include = sorted(periodicity - result_union)
        print(f"days_to_exclude: {days_to_exclude}")
        print(f"days_to_include: {days_to_include}")
        texts = []

        if days_to_include:
            dates = self.days_to_dates(days_to_include)
            texts.append(f"with additional service on {self.format_dates(dates)}")

        if days_to_exclude:
            dates = self.days_to_dates(days_to_exclude)
            texts.append(f"except on {self.format_dates(dates)}")

        return " ".join(texts)

    def days_to_dates(self, days: List[int]) -> List[str]:
        """Convert day indices to formatted dates."""
        return [
            (
                datetime(self.calendar_state.date_range.year, 1, 1)
                + timedelta(days=day - 1)
            ).strftime("%d/%m/%Y")
            for day in days
        ]

    def format_dates(self, dates: List[str]) -> str:
        """Format list of dates into readable string."""
        if len(dates) == 1:
            return dates[0]
        if len(dates) == 2:
            return f"{dates[0]} and {dates[1]}"
        *first, last = dates
        return f"{', '.join(first)}, and {last}"

    def generate_no_service_text(self) -> str:
        """Generate text for no service case."""
        start = self.calendar_state.date_range.start.strftime("%d/%m/%Y")
        end = self.calendar_state.date_range.end.strftime("%d/%m/%Y")
        return f"No service is provided from {start} to {end}"

    def show_error(self, message: str) -> None:
        """
        Display error message.

        Args:
            message: Error message to display
        """
        ctk.CTkLabel(self, text=message, text_color="red").pack(pady=20)

    def display_result(self, result_text: str) -> None:
        """
        Display formatted result text.

        Args:
            result_text: Formatted result text to display
        """
        ctk.CTkLabel(self, text=result_text, wraplength=500).pack(pady=20, padx=20)

        # Add restart button
        ctk.CTkButton(self, text="Start Over", command=self.restart).pack(pady=10)

    def restart(self) -> None:
        """Reset application state and close window."""
        self.destroy()
