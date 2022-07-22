from typing import TYPE_CHECKING

from dp_mobility_report.report.html.html_utils import fmt, get_template

if TYPE_CHECKING:
    from dp_mobility_report.md_report import MobilityDataReport


def render_config(mdreport: "MobilityDataReport") -> str:

    config_table = render_config_table(mdreport)
    privacy_info = render_privacy_info(mdreport.privacy_budget is not None)

    template_structure = get_template("config_segment.html")
    return template_structure.render(
        config_table=config_table, privacy_info=privacy_info
    )


def render_config_table(mdreport: "MobilityDataReport") -> str:

    config_list = [
        {"name": "Max. trips per user", "value": fmt(mdreport.max_trips_per_user)},
        {"name": "Privacy budget", "value": fmt(mdreport.privacy_budget)},
        {"name": "User privacy", "value": fmt(mdreport.user_privacy)},
        {"name": "Analysis selection", "value": fmt(mdreport.analysis_selection)},
        {"name": "Evaluation dev. mode", "value": fmt(mdreport.evalu)},
    ]

    # create html from template
    template_table = get_template("table.html")
    dataset_stats_html = template_table.render(name="Configuration", rows=config_list)
    return dataset_stats_html


def render_privacy_info(with_privacy: bool) -> str:
    if with_privacy:
        return "Noise has been added to provide differential privacy. The 95%-confidence interval gives an intuition about the reliability of the noisy results."
    else:
        return "No noise has been added."