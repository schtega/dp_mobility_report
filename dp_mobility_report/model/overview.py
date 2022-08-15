import calendar
from datetime import timedelta
from typing import TYPE_CHECKING, Optional

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from dp_mobility_report.md_report import MobilityDataReport

from dp_mobility_report import constants as const
from dp_mobility_report.model import m_utils
from dp_mobility_report.model.section import Section
from dp_mobility_report.privacy import diff_privacy


def get_dataset_statistics(
    mdreport: "MobilityDataReport", eps: Optional[float]
) -> Section:
    epsi = m_utils.get_epsi(mdreport.evalu, eps, 4)

    # counts for complete and incomplete trips
    points_per_trip = (
        mdreport.df.reset_index().groupby(const.TID).count()["index"].value_counts()
    )
    n_incomplete_trips = 0 if 1 not in points_per_trip else points_per_trip[1]
    n_incomplete_trips = diff_privacy.count_dp(
        n_incomplete_trips,
        epsi,
        mdreport.max_trips_per_user,
    )

    moe_incomplete_trips = diff_privacy.laplace_margin_of_error(
        0.95, epsi, mdreport.max_trips_per_user
    )

    n_complete_trips = 0 if 2 not in points_per_trip else points_per_trip[2]
    n_complete_trips = diff_privacy.count_dp(
        n_complete_trips,
        epsi,
        2 * mdreport.max_trips_per_user,
    )
    moe_complete_trips = diff_privacy.laplace_margin_of_error(
        0.95, epsi, 2 * mdreport.max_trips_per_user
    )

    n_trips = n_incomplete_trips + n_complete_trips
    if n_trips == 0:
        n_trips = None  # trips cannot be None
        moe_trips = (moe_incomplete_trips + moe_complete_trips) / 2
    else:
        moe_trips = (
            n_incomplete_trips * moe_incomplete_trips
            + n_complete_trips * moe_complete_trips
        ) / n_trips

    n_records = None if n_trips is None else (n_incomplete_trips + n_complete_trips * 2)
    if n_records is None:
        moe_records = (moe_incomplete_trips + moe_complete_trips * 2) / 2
    else:
        moe_records = (
            n_incomplete_trips * moe_incomplete_trips
            + n_complete_trips * 2 * moe_complete_trips
        ) / n_records

    n_users = diff_privacy.count_dp(
        mdreport.df[const.UID].nunique(), epsi, 1, nonzero=True
    )
    moe_users = diff_privacy.laplace_margin_of_error(0.95, epsi, 1)

    n_locations = diff_privacy.count_dp(
        mdreport.df.groupby([const.LAT, const.LNG]).ngroups,
        epsi,
        2 * mdreport.max_trips_per_user,
        nonzero=True,
    )
    moe_locations = diff_privacy.laplace_margin_of_error(
        0.95, epsi, 2 * mdreport.max_trips_per_user
    )

    stats = {
        "n_records": n_records,
        "n_trips": n_trips,
        "n_complete_trips": n_complete_trips,
        "n_incomplete_trips": n_incomplete_trips,
        "n_users": n_users,
        "n_locations": n_locations,
    }
    
    moe = {
        "records": moe_records,
        "trips": moe_trips,
        "complete_trips": moe_complete_trips,
        "incomplete_trips": moe_incomplete_trips,
        "users": moe_users,
        "locations": moe_locations,
    }

    return Section(data=stats, privacy_budget=eps, margin_of_errors_laplace=moe)


def get_missing_values(mdreport: "MobilityDataReport", eps: Optional[float]) -> Section:
    columns = [const.UID, const.TID, const.DATETIME, const.LAT, const.LNG]
    epsi = m_utils.get_epsi(mdreport.evalu, eps, len(columns))

    missings = dict((len(mdreport.df) - mdreport.df.count())[columns])

    moe = diff_privacy.laplace_margin_of_error(
        0.95, epsi, 2 * mdreport.max_trips_per_user
    )

    return Section(data=missings, privacy_budget=eps, margin_of_error_laplace=moe)


def get_trips_over_time(
    mdreport: "MobilityDataReport", eps: Optional[float]
) -> Section:
    epsi = m_utils.get_epsi(mdreport.evalu, eps, 3)
    epsi_limits = epsi * 2 if epsi is not None else None

    df_trip = mdreport.df[
        (mdreport.df[const.POINT_TYPE] == const.END)
    ]  # only count each trip once
    dp_bounds = diff_privacy.bounds_dp(
        df_trip[const.DATETIME], epsi_limits, mdreport.max_trips_per_user
    )

    # cut based on dp min and max values
    (
        trips_over_time
    ) = m_utils.cut_outliers(  # don't disclose outliers to the as the boundaries are not defined through user input
        df_trip[const.DATETIME],
        min_value=dp_bounds[0],
        max_value=dp_bounds[1],
    )

    # only use date and remove time
    dp_bounds = pd.Series(dp_bounds).dt.date

    # different aggregations based on range of dates
    range_of_days = dp_bounds[1] - dp_bounds[0]
    if range_of_days > timedelta(days=712):  # more than two years (102 weeks)
        resample = "M"
        datetime_precision = const.PREC_MONTH
    if range_of_days > timedelta(days=90):  # more than three months
        resample = "W-Mon"
        datetime_precision = const.PREC_WEEK
    else:
        resample = "1D"
        datetime_precision = const.PREC_DATE

    trip_count = pd.DataFrame(trips_over_time)
    trip_count.loc[:, "trip_count"] = 1
    trip_count = (
        trip_count.set_index(const.DATETIME)
        .resample(resample, label="left")
        .count()
        .reset_index()
    )
    trip_count[const.DATETIME] = trip_count[const.DATETIME].dt.date
    trip_count["trip_count"] = diff_privacy.counts_dp(
        trip_count["trip_count"].values,
        epsi,
        mdreport.max_trips_per_user,
    )

    moe_laplace = diff_privacy.laplace_margin_of_error(
        0.95, epsi, mdreport.max_trips_per_user
    )

    # as percent instead of absolute values
    trip_sum = np.sum(trip_count["trip_count"])
    if trip_sum != 0:
        trip_count["trip_count"] = trip_count["trip_count"] / trip_sum * 100
        moe_laplace = moe_laplace / trip_sum * 100

    quartiles = pd.Series({"min": dp_bounds[0], "max": dp_bounds[1]})

    return Section(
        data=trip_count,
        privacy_budget=eps,
        datetime_precision=datetime_precision,
        quartiles=quartiles,
        margin_of_error_laplace=moe_laplace,
    )


def get_trips_per_weekday(
    mdreport: "MobilityDataReport", eps: Optional[float]
) -> Section:
    mdreport.df.loc[:, const.DATE] = mdreport.df[const.DATETIME].dt.date
    mdreport.df.loc[:, const.DAY_NAME] = mdreport.df[const.DATETIME].dt.day_name()

    trips_per_weekday = (
        mdreport.df[
            mdreport.df[const.POINT_TYPE] == const.END
        ]  # count trips not records
        .groupby([const.DAY_NAME], sort=False)
        .count()[const.TID]
    )
    missing_days = set(calendar.day_name) - set(trips_per_weekday.index.tolist())
    trips_per_weekday = trips_per_weekday.append(pd.Series(0, index=list(missing_days)))
    trips_per_weekday.index = pd.Categorical(
        trips_per_weekday.index, list(calendar.day_name)
    )
    trips_per_weekday.sort_index(inplace=True)

    trips_per_weekday = pd.Series(
        index=trips_per_weekday.index,
        data=diff_privacy.counts_dp(
            trips_per_weekday.values,
            eps,
            mdreport.max_trips_per_user,
        ),
    )
    moe = diff_privacy.laplace_margin_of_error(0.95, eps, mdreport.max_trips_per_user)

    trip_sum = np.sum(trips_per_weekday)
    if trip_sum != 0:
        trips_per_weekday = trips_per_weekday / trip_sum * 100
        moe = moe / trip_sum * 100

    return Section(
        data=trips_per_weekday, privacy_budget=eps, margin_of_error_laplace=moe
    )


def get_trips_per_hour(mdreport: "MobilityDataReport", eps: Optional[float]) -> Section:

    # TODO: include all times (even if not present in data)
    hour_weekday = mdreport.df.groupby(
        [const.HOUR, const.IS_WEEKEND, const.POINT_TYPE]
    ).count()[const.TID]
    hour_weekday.name = "count"

    # create all potential combinations
    full_combination = pd.DataFrame(
        list(
            map(
                np.ravel,
                np.meshgrid(
                    range(0, 24),
                    [const.WEEKDAY, const.WEEKEND],
                    [const.START, const.END],
                ),
            )
        )
    ).T
    full_combination.columns = [const.HOUR, const.IS_WEEKEND, const.POINT_TYPE]
    full_combination["count"] = 0
    full_combination.set_index(
        [const.HOUR, const.IS_WEEKEND, const.POINT_TYPE], inplace=True
    )

    hour_weekday = full_combination.add(pd.DataFrame(hour_weekday), fill_value=0)

    hour_weekday = hour_weekday.reset_index()
    hour_weekday["count"] = diff_privacy.counts_dp(
        hour_weekday["count"], eps, mdreport.max_trips_per_user
    )

    hour_weekday[const.TIME_CATEGORY] = (
        hour_weekday[const.IS_WEEKEND] + "_" + hour_weekday[const.POINT_TYPE]
    )
    moe = diff_privacy.laplace_margin_of_error(0.95, eps, mdreport.max_trips_per_user)

    # as percent instead of absolute values
    trip_sum = np.sum(
        hour_weekday[hour_weekday.point_type == const.END]["count"]
    )  # only use ends to get sum of trips
    if trip_sum != 0:
        hour_weekday["count"] = hour_weekday["count"] / trip_sum * 100
        moe = moe / trip_sum * 100

    return Section(
        data=hour_weekday[[const.HOUR, const.TIME_CATEGORY, "count"]],
        privacy_budget=eps,
        margin_of_error_laplace=moe,
    )
