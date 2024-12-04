from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import numpy as np
from numpy.typing import NDArray


@dataclass
class ClusterConfig:
    """Configuration for cluster generation."""

    year: int
    weekdays: List[str] = field(
        default_factory=lambda: [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
    )
    holidays: List[str] = field(
        default_factory=lambda: [
            "01/01",
            "06/01",
            "05/04",
            "01/05",
            "03/05",
            "23/05",
            "03/06",
            "15/08",
            "01/11",
            "11/11",
            "25/12",
            "26/12",
        ]
    )


class ClusterGenerator:
    """Generates day clusters based on patterns and holidays."""

    def __init__(self, config: ClusterConfig):
        self.config = config
        self.days_in_year = 365 if not self._is_leap_year(config.year) else 366
        self.day_offsets = self._calculate_day_offsets()

    def _calculate_day_offsets(self) -> List[int]:
        """Calculate day offsets for each weekday based on the first day of the year."""
        first_day = datetime(self.config.year, 1, 1).weekday()  # Monday=0, Sunday=6
        return [(i - first_day) % 7 for i in range(7)]

    def _is_leap_year(self, year: int) -> bool:
        """Check if the given year is a leap year."""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def _create_single_day_clusters(self) -> Dict[str, NDArray]:
        """Create clusters for individual days of the week."""
        clusters = {}
        for day_index, day_name in enumerate(self.config.weekdays):
            clusters[day_name] = np.array(
                [
                    (
                        1
                        if (
                            datetime(self.config.year, 1, 1) + timedelta(days=i)
                        ).weekday()
                        == day_index
                        else 0
                    )
                    for i in range(self.days_in_year)
                ]
            )
        return clusters

    def _create_multi_day_clusters(self, num_days: int) -> Dict[str, NDArray]:
        """Create clusters for consecutive days."""
        clusters = {}
        single_day_clusters = self._create_single_day_clusters()
        weekdays = self.config.weekdays
        num_weekdays = len(weekdays)

        for i in range(num_weekdays):
            cluster_days = []
            cluster_name_parts = []

            for j in range(num_days):
                day_idx = (i + j) % num_weekdays
                day_name = weekdays[day_idx]
                cluster_days.append(single_day_clusters[day_name])
                cluster_name_parts.append(day_name)

            if num_days <= 2:
                name = f"{cluster_name_parts[0]} and {cluster_name_parts[-1]}"
            else:
                name = f"from {cluster_name_parts[0]} to {cluster_name_parts[-1]}"

            clusters[name] = np.sum(cluster_days, axis=0)

        return clusters

    def _create_special_clusters(self, working_days: NDArray) -> Dict[str, NDArray]:
        """Create special clusters like holidays and pre-holidays."""
        holiday_indices = self._date_strings_to_indices(self.config.holidays)
        holidays = np.zeros(self.days_in_year)
        holidays[np.array(holiday_indices) - 1] = 1

        # Add Sundays to holidays
        sunday_idx = self.config.weekdays.index("Sunday")
        holidays += self._create_single_day_clusters()[self.config.weekdays[sunday_idx]]
        holidays[holidays > 1] = 1

        # Working days excluding holidays
        working_days = working_days.copy()
        working_days[holidays == 1] = 0

        # Pre-holiday days
        pre_holidays = np.roll(holidays, -1) - holidays
        pre_holidays[pre_holidays < 0] = 0

        return {
            "Holidays": holidays,
            "Working days": working_days,
            "Days before Holidays": pre_holidays,
        }

    def _date_strings_to_indices(self, date_strings: List[str]) -> List[int]:
        """Convert date strings (DD/MM) to day-of-year indices."""
        return [
            datetime.strptime(f"{date}/{self.config.year}", "%d/%m/%Y")
            .timetuple()
            .tm_yday
            for date in date_strings
        ]

    def _combine_clusters(
        self,
        cluster_collections: Dict[str, Dict[str, NDArray]],
        special_clusters: Dict[str, NDArray],
        start_idx: int,
        end_idx: int,
    ) -> Tuple[NDArray, List[str], NDArray]:
        """Combine all clusters and prepare final output."""
        all_clusters = []
        cluster_names = []

        # Add regular clusters
        for collection in cluster_collections.values():
            for name, cluster in collection.items():
                all_clusters.append(cluster)
                cluster_names.append(name)

        # Add special clusters
        for name, cluster in special_clusters.items():
            all_clusters.append(cluster)
            cluster_names.append(name)

        # Add "All days" cluster
        all_days = np.ones(self.days_in_year)
        all_clusters.append(all_days)
        cluster_names.append("All days")

        # Convert to numpy array and slice to requested range
        clusters_array = np.array(all_clusters)[:, start_idx - 1 : end_idx]
        day_indices = np.array(range(start_idx, end_idx + 1))

        return clusters_array, cluster_names, day_indices

    def create_clusters(
        self, start_idx: int, end_idx: int
    ) -> Tuple[NDArray, List[str], NDArray]:
        """
        Create clusters of days based on specific patterns and holidays.

        Args:
            start_idx: The starting day index (1-based).
            end_idx: The ending day index (1-based).

        Returns:
            A tuple containing:
            - A numpy array of clusters for the specified range.
            - A list of cluster names.
            - A numpy array of day indices for the specified range.

        Raises:
            ValueError: If indices are invalid.
        """
        if start_idx < 1 or end_idx > self.days_in_year or start_idx > end_idx:
            raise ValueError(
                f"Invalid indices: start_idx={start_idx}, end_idx={end_idx}"
            )

        # Create all cluster collections
        cluster_collections = {
            "single": self._create_single_day_clusters(),
            "double": self._create_multi_day_clusters(2),
            "triple": self._create_multi_day_clusters(3),
            "quadruple": self._create_multi_day_clusters(4),
            "quintuple": self._create_multi_day_clusters(5),
            "sextuple": self._create_multi_day_clusters(6),
        }

        # Get working days from quintuple clusters (Monday to Friday)
        working_days = cluster_collections["quintuple"]["from Monday to Friday"]

        # Create special clusters
        special_clusters = self._create_special_clusters(working_days)

        # Combine all clusters and return
        return self._combine_clusters(
            cluster_collections, special_clusters, start_idx, end_idx
        )
