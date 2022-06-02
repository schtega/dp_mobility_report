from typing import TYPE_CHECKING, Optional, Tuple

from pandas import DataFrame
from tqdm.auto import tqdm

from dp_mobility_report.model.section import Section

if TYPE_CHECKING:
    from dp_mobility_report.md_report import MobilityDataReport

from dp_mobility_report import constants as const
from dp_mobility_report.model import (
    od_analysis,
    overview,
    place_analysis,
    user_analysis,
)


def get_analysis_elements_info(analysis_selection: list) -> Tuple:
    is_all_analyses = const.ALL in analysis_selection

    if is_all_analyses:
        return (
            len(const.OVERVIEW_ELEMENTS)
            + len(const.PLACE_ELEMENTS)
            + len(const.OD_ELEMENTS)
            + len(const.USER_ELEMENTS),
            is_all_analyses,
        )

    element_count = (
        len(const.OVERVIEW_ELEMENTS) if (const.OVERVIEW in analysis_selection) else 0
    )
    element_count += (
        len(const.PLACE_ELEMENTS) if (const.PLACE_ANALYSIS in analysis_selection) else 0
    )
    element_count += (
        len(const.OD_ELEMENTS) if (const.OD_ANALYSIS in analysis_selection) else 0
    )
    element_count += (
        len(const.USER_ELEMENTS) if (const.USER_ANALYSIS in analysis_selection) else 0
    )

    return element_count, is_all_analyses


def report_elements(mdreport: "MobilityDataReport") -> dict:

    report: dict = {}
    element_count, is_all_analyses = get_analysis_elements_info(
        mdreport.analysis_selection
    )
    record_count = None
    trip_count = None

    # get privacy budget for each report element
    if mdreport.privacy_budget is None or mdreport.evalu is True:
        epsilon = mdreport.privacy_budget
    else:
        epsilon = (
            mdreport.privacy_budget / element_count
            if element_count > 0
            else mdreport.privacy_budget
        )

    with tqdm(  # progress bar
        total=4, desc="Create report", disable=mdreport.disable_progress_bar
    ) as pbar:
        if is_all_analyses | (const.OVERVIEW in mdreport.analysis_selection):
            report = {**report, **add_overview_elements(mdreport, epsilon)}
            record_count = report[const.DS_STATISTICS].data["n_records"]
            trip_count = report[const.DS_STATISTICS].data["n_trips"]
        pbar.update()

        if is_all_analyses | (const.PLACE_ANALYSIS in mdreport.analysis_selection):
            report = {
                **report,
                **add_place_analysis_elements(mdreport, epsilon, record_count),
            }
        pbar.update()

        if is_all_analyses | (const.OD_ANALYSIS in mdreport.analysis_selection):
            _od_shape = od_analysis.get_od_shape(mdreport.df, mdreport.tessellation)
            report = {
                **report,
                **add_od_analysis_elements(mdreport, _od_shape, epsilon, trip_count),
            }
        pbar.update()

        if is_all_analyses | (const.USER_ANALYSIS in mdreport.analysis_selection):
            report = {**report, **add_user_analysis_elements(mdreport, epsilon)}
        pbar.update()

    return report


def add_overview_elements(mdreport: "MobilityDataReport", epsilon: float) -> dict:
    return {
        const.DS_STATISTICS: overview.get_dataset_statistics(mdreport, epsilon)
        if const.DS_STATISTICS in const.OVERVIEW_ELEMENTS
        else Section(),
        const.MISSING_VALUES: overview.get_missing_values(mdreport, epsilon)
        if const.MISSING_VALUES in const.OVERVIEW_ELEMENTS
        else Section(),
        const.TRIPS_OVER_TIME: overview.get_trips_over_time(mdreport, epsilon)
        if const.TRIPS_OVER_TIME in const.OVERVIEW_ELEMENTS
        else Section(),
        const.TRIPS_PER_WEEKDAY: overview.get_trips_per_weekday(mdreport, epsilon)
        if const.TRIPS_PER_WEEKDAY in const.OVERVIEW_ELEMENTS
        else Section(),
        const.TRIPS_PER_HOUR: overview.get_trips_per_hour(mdreport, epsilon)
        if const.TRIPS_PER_HOUR in const.OVERVIEW_ELEMENTS
        else Section(),
    }


def add_place_analysis_elements(
    mdreport: "MobilityDataReport", epsilon: float, record_count: Optional[int]
) -> dict:
    return {
        const.VISITS_PER_TILE: place_analysis.get_visits_per_tile(
            mdreport, epsilon, record_count
        )
        if const.VISITS_PER_TILE in const.PLACE_ELEMENTS
        else Section(),
        const.VISITS_PER_TILE_TIMEWINDOW: place_analysis.get_visits_per_tile_timewindow(
            mdreport, epsilon, record_count
        )
        if const.VISITS_PER_TILE_TIMEWINDOW in const.PLACE_ELEMENTS
        else Section(),
    }


def add_od_analysis_elements(
    mdreport: "MobilityDataReport",
    _od_shape: DataFrame,
    epsilon: float,
    trip_count: Optional[int],
) -> dict:
    return {
        const.OD_FLOWS: od_analysis.get_od_flows(
            _od_shape, mdreport, epsilon, trip_count
        )
        if const.OD_FLOWS in const.OD_ELEMENTS
        else Section(),
        const.TRAVEL_TIME: od_analysis.get_travel_time(_od_shape, mdreport, epsilon)
        if const.TRAVEL_TIME in const.OD_ELEMENTS
        else Section(),
        const.JUMP_LENGTH: od_analysis.get_jump_length(_od_shape, mdreport, epsilon)
        if const.JUMP_LENGTH in const.OD_ELEMENTS
        else Section(),
    }


def add_user_analysis_elements(mdreport: "MobilityDataReport", epsilon: float) -> dict:
    return {
        const.TRIPS_PER_USER: user_analysis.get_trips_per_user(mdreport, epsilon)
        if const.TRIPS_PER_USER in const.USER_ELEMENTS
        else Section(),
        const.USER_TIME_DELTA: user_analysis.get_user_time_delta(mdreport, epsilon)
        if const.USER_TIME_DELTA in const.USER_ELEMENTS
        else Section(),
        const.RADIUS_OF_GYRATION: user_analysis.get_radius_of_gyration(
            mdreport, epsilon
        )
        if const.RADIUS_OF_GYRATION in const.USER_ELEMENTS
        else Section(),
        const.USER_TILE_COUNT: user_analysis.get_user_tile_count(mdreport, epsilon)
        if const.USER_TILE_COUNT in const.USER_ELEMENTS
        else Section(),
        const.MOBILITY_ENTROPY: user_analysis.get_mobility_entropy(mdreport, epsilon)
        if const.MOBILITY_ENTROPY in const.USER_ELEMENTS
        else Section(),
    }
