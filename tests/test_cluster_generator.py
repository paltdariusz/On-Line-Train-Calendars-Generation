import pytest
import numpy as np
from datetime import datetime

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.CreateClusters import ClusterGenerator, ClusterConfig


@pytest.fixture
def default_generator():
    """Create a default ClusterGenerator instance for testing."""
    config = ClusterConfig(year=2021)
    return ClusterGenerator(config)


@pytest.fixture
def leap_year_generator():
    """Create a ClusterGenerator instance for leap year testing."""
    config = ClusterConfig(year=2020)
    return ClusterGenerator(config)


class TestClusterGenerator:

    def test_initialization(self, default_generator):
        """Test proper initialization of ClusterGenerator."""
        assert default_generator.days_in_year == 365
        assert len(default_generator.day_offsets) == 7

    def test_leap_year(self, leap_year_generator):
        """Test proper handling of leap years."""
        assert leap_year_generator.days_in_year == 366

    def test_invalid_indices(self, default_generator):
        """Test validation of invalid indices."""
        with pytest.raises(ValueError):
            default_generator.create_clusters(0, 365)
        with pytest.raises(ValueError):
            default_generator.create_clusters(366, 366)
        with pytest.raises(ValueError):
            default_generator.create_clusters(10, 5)

    def test_single_day_clusters(self, default_generator):
        """Test creation of single day clusters."""
        clusters = default_generator._create_single_day_clusters()
        assert len(clusters) == 7
        assert all(len(cluster) == 365 for cluster in clusters.values())
        assert all(cluster.sum() > 50 for cluster in clusters.values())  # Rough check

    def test_multi_day_clusters(self, default_generator):
        """Test creation of multi-day clusters."""
        doubles = default_generator._create_multi_day_clusters(2)
        assert len(doubles) == 7
        assert all("and" in name for name in doubles.keys())

        triples = default_generator._create_multi_day_clusters(3)
        assert len(triples) == 7
        assert all("from" in name and "to" in name for name in triples.keys())

    def test_special_clusters(self, default_generator):
        """Test creation of special clusters."""
        working_days = np.ones(365)
        special = default_generator._create_special_clusters(working_days)

        assert "Holidays" in special
        assert "Working days" in special
        assert "Days before Holidays" in special

        # Holidays should include all Sundays plus specified holidays
        assert special["Holidays"].sum() > len(default_generator.config.holidays)

    def test_full_cluster_creation(self, default_generator):
        """Test complete cluster creation process."""
        clusters, names, indices = default_generator.create_clusters(1, 10)

        assert clusters.shape[1] == 10  # 10 days as requested
        assert len(names) == clusters.shape[0]
        assert len(indices) == 10
        assert indices[0] == 1
        assert indices[-1] == 10

    def test_holiday_handling(self, default_generator):
        """Test proper handling of holidays."""
        # New Year's Day (January 1st) should be marked as holiday
        clusters, names, _ = default_generator.create_clusters(1, 1)
        holiday_idx = names.index("Holidays")
        assert clusters[holiday_idx][0] == 1

    @pytest.mark.parametrize(
        "start,end",
        [
            (1, 7),  # First week
            (359, 365),  # Last week
            (180, 187),  # Mid-year week
        ],
    )
    def test_various_ranges(self, default_generator, start, end):
        """Test cluster creation with various date ranges."""
        clusters, names, indices = default_generator.create_clusters(start, end)
        assert clusters.shape[1] == end - start + 1
        assert len(indices) == end - start + 1
        assert indices[0] == start
        assert indices[-1] == end

    def test_specific_cluster_output(self, default_generator):
        """Test specific output requirements for create_clusters(1, 3)."""
        clusters, names, indices = default_generator.create_clusters(1, 3)

        # Test lengths
        assert len(clusters) == 46, f"Expected clusters length 46, got {len(clusters)}"
        assert len(names) == 46, f"Expected names length 46, got {len(names)}"

        # Test shape
        assert clusters.shape == (
            46,
            3,
        ), f"Expected shape (46, 3), got {clusters.shape}"

        # Test indices
        np.testing.assert_array_equal(
            indices, np.array([1, 2, 3]), err_msg="Expected indices [1, 2, 3]"
        )

    def test_holiday_edge_cases(self, default_generator):
        """Test holidays falling on weekends or consecutive weekdays."""
        default_generator.config.holidays = [
            datetime(2021, 12, 25).strftime("%d/%m"),  # Saturday
            datetime(2021, 12, 26).strftime("%d/%m"),  # Sunday
            datetime(2021, 12, 27).strftime("%d/%m"),  # Monday (Boxing Day observed)
        ]
        clusters, names, _ = default_generator.create_clusters(355, 365)
        holiday_idx = names.index("Holidays")
        assert clusters[holiday_idx].sum() == 3

    def test_overlapping_clusters(self, default_generator):
        """Test correct handling of overlapping clusters."""
        clusters, names, _ = default_generator.create_clusters(1, 10)
        assert "Working days" in names
        assert "Holidays" in names
        assert not np.any(
            np.logical_and(
                clusters[names.index("Working days")], clusters[names.index("Holidays")]
            )
        ), "Working days and Holidays should not overlap"

    def test_full_year_range(self, default_generator):
        """Test cluster creation for the entire year."""
        clusters, names, indices = default_generator.create_clusters(1, 365)
        assert clusters.shape[1] == 365
        assert indices[0] == 1
        assert indices[-1] == 365
