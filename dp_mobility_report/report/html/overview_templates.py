from dp_mobility_report.report.html.utils import fmt, render_summary, get_template
from dp_mobility_report.visualization import plot, utils


def render_overview(report, extra_var):
    dataset_stats_table = None
    extra_var_barchart = None
    missing_values_table = None
    trips_over_time_linechart = None
    trips_over_time_linechart = None
    trips_over_time_summary_table = None
    trips_per_weekday_barchart = None
    trips_per_hour_linechart = None

    if "ds_statistics" in report:
        dataset_stats_table = render_dataset_statistics(
            report["ds_statistics"], extra_var
        )

    if "extra_var_counts" in report:
        extra_var_barchart = (
            "No additional variable specified"
            if extra_var is None
            else render_extra_var(report["extra_var_counts"], extra_var)
        )

    if "missing_values" in report:
        missing_values_table = render_missing_values(
            report["missing_values"], extra_var
        )
        # outlier_count_trips_over_time_info = render_outlier_info(
        #     report["trips_over_time_section"].n_outliers
        # )

    if "trips_over_time_section" in report:
        trips_over_time_linechart = render_trips_over_time(
            report["trips_over_time_section"]
        )
        trips_over_time_summary_table = render_summary(
            report["trips_over_time_section"].quartiles
        )

    if "trips_per_weekday" in report:
        trips_per_weekday_barchart = render_trips_per_weekday(
            report["trips_per_weekday"]
        )

    if "trips_per_hour" in report:
        trips_per_hour_linechart = render_trips_per_hour(report["trips_per_hour"])

    template_structure = get_template("overview_segment.html")
    return template_structure.render(
        dataset_stats_table=dataset_stats_table,
        extra_var_barchart=extra_var_barchart,
        missing_values_table=missing_values_table,
        trips_over_time_linechart=trips_over_time_linechart,
        trips_over_time_summary_table=trips_over_time_summary_table,
        # outlier_count_trips_over_time=outlier_count_trips_over_time_info,
        trips_per_weekday_barchart=trips_per_weekday_barchart,
        trips_per_hour_linechart=trips_per_hour_linechart,
    )


##### render single elements of the report #####
### render overview functions
def render_dataset_statistics(dataset_statistics, extra_var=None):

    dataset_stats_list = [
        {"name": "Number of records", "value": fmt(dataset_statistics["n_records"])},
        {"name": "Distinct trips", "value": fmt(dataset_statistics["n_trips"])},
        {
            "name": "Number of complete trips (start and and point)",
            "value": fmt(dataset_statistics["ntrips_double"]),
        },
        {
            "name": "Number of incomplete trips (single point)",
            "value": fmt(dataset_statistics["ntrips_single"]),
        },
        {"name": "Distinct users", "value": fmt(dataset_statistics["n_users"])},
        {
            "name": "Distinct locations (lat & lon combination)",
            "value": fmt(dataset_statistics["n_places"]),
        },
    ]

    if "n_extra_var" in dataset_statistics:
        dataset_stats_list.append(
            {
                "name": ("Distinct " + extra_var),
                "value": fmt(dataset_statistics["n_extra_var"]),
            }
        )

    # create html from template
    template_table = get_template("table.html")
    dataset_stats_html = template_table.render(
        name="Dataset statistics", rows=dataset_stats_list
    )
    return dataset_stats_html


def render_extra_var(extra_var_counts, extra_var):
    barchart = plot.barchart(
        data=extra_var_counts.reset_index(),
        x="perc",
        y="index",
        x_axis_label="% of records",
        y_axis_label=extra_var,
    )
    return utils.fig_to_html(barchart)


def render_missing_values(missing_values, extra_var):
    missing_values_list = [
        {"name": "User ID (uid)", "value": fmt(missing_values["uid"])},
        {"name": "Trip ID (tid)", "value": fmt(missing_values["tid"])},
        {"name": "Timestamp (datetime)", "value": fmt(missing_values["datetime"])},
        {"name": "Latitude (lat)", "value": fmt(missing_values["lat"])},
        {"name": "Longitude (lng)", "value": fmt(missing_values["lng"])},
    ]

    if extra_var in missing_values:
        missing_values_list.append(
            {"name": (extra_var), "value": fmt(missing_values[extra_var])}
        )
    template_table = get_template("table.html")
    missing_values_html = template_table.render(
        name="Missing values", rows=missing_values_list
    )
    return missing_values_html


def render_trips_over_time(trips_over_time_section):
    title = (
        "Date"
        if trips_over_time_section.date_aggregation_level == "date"
        else "Date (grouped by week)"
    )
    if len(trips_over_time_section.data) <= 20:
        chart = plot.barchart(
            data=trips_over_time_section.data,
            x="datetime",
            y="trip_count",
            x_axis_label="Date",
            y_axis_label="Frequency",
            rotate_label=True,
        )
        html = utils.fig_to_html(chart)
    else:
        chart = plot.linechart(
            trips_over_time_section.data, "datetime", "trip_count", "Date", "Frequency"
        )
        html = utils.fig_to_html(chart)
    return html


def render_trips_per_weekday(trips_per_weekday):
    chart = plot.barchart(
        data=trips_per_weekday.reset_index(),
        x="day_name",
        y="tid",
        x_axis_label="Weekday",
        y_axis_label="Average trips per weekday",
        rotate_label=True,
        order_x=[
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
    )
    return utils.fig_to_html(chart)


def render_trips_per_hour(trips_per_hour):
    chart = plot.multi_linechart(
        trips_per_hour,
        "hour",
        "count",
        "time_category",
        hue_order=["weekday_start", "weekday_end", "weekend_start", "weekend_end"],
    )
    html = utils.fig_to_html(chart)
    return html