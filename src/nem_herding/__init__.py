"""NEM concentration risk and herding-synchronisation framework.

Three-layer information taxonomy:
  Layer A: Policy events  -> nem_herding.events
  Layer B: Corporate events -> nem_herding.corporate
  Layer C: Information environment -> nem_herding.info_env
"""

from nem_herding.events import (
    load_events,
    events_in_window,
    events_for_rez,
    events_of_category,
    events_of_coupling_layer,
    register_summary,
)

from nem_herding.corporate import (
    load_actors,
    load_corporate_events,
    events_for_actor,
    events_for_actor_type,
    events_in_rez,
    events_of_type,
    actor_lead_lag_pairs,
)

from nem_herding.info_env import (
    load_trade_press_counts,
    load_conferences,
    info_intensity_by_rez,
    info_intensity_comparison,
)

__all__ = [
    # Layer A
    "load_events",
    "events_in_window",
    "events_for_rez",
    "events_of_category",
    "events_of_coupling_layer",
    "register_summary",
    # Layer B
    "load_actors",
    "load_corporate_events",
    "events_for_actor",
    "events_for_actor_type",
    "events_in_rez",
    "events_of_type",
    "actor_lead_lag_pairs",
    # Layer C
    "load_trade_press_counts",
    "load_conferences",
    "info_intensity_by_rez",
    "info_intensity_comparison",
]
