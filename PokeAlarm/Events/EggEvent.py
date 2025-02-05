# Standard Library Imports
from datetime import datetime

# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import (
    get_time_as_str,
    get_seconds_remaining,
    get_gmaps_link,
    get_applemaps_link,
    get_waze_link,
    get_dist_as_str,
    get_weather_emoji,
    get_team_emoji,
    get_ex_eligible_emoji,
)
from . import BaseEvent
from PokeAlarm import Unknown


class EggEvent(BaseEvent):
    """Event representing the change occurred in a Gym."""

    def __init__(self, data):
        """Creates a new Stop Event based on the given dict."""
        super(EggEvent, self).__init__("egg")
        check_for_none = BaseEvent.check_for_none

        # Identification
        self.gym_id = data.get("gym_id")

        # Time Remaining
        self.hatch_time = datetime.utcfromtimestamp(
            data.get("start") or data.get("raid_begin")
        )  # RM or Monocle
        self.time_left = get_seconds_remaining(self.hatch_time)
        self.raid_end = datetime.utcfromtimestamp(
            data.get("end") or data.get("raid_end")
        )  # RM or Monocle

        # Location
        self.lat = float(data["latitude"])
        self.lng = float(data["longitude"])
        self.distance = Unknown.SMALL  # Completed by Manager
        self.direction = Unknown.TINY  # Completed by Manager
        self.weather_id = check_for_none(int, data.get("weather"), Unknown.TINY)

        # Egg Info
        self.egg_lvl = check_for_none(int, data.get("level"), 0)

        # Gym Details (currently only sent from Monocle)
        self.gym_name = check_for_none(str, data.get("name"), Unknown.REGULAR).strip()
        self.gym_description = check_for_none(
            str, data.get("description"), Unknown.REGULAR
        ).strip()
        self.gym_image = check_for_none(str, data.get("url"), Unknown.REGULAR)
        self.slots_available = Unknown.TINY
        self.guard_count = Unknown.TINY

        self.sponsor_id = check_for_none(int, data.get("sponsor"), Unknown.TINY)
        self.park = check_for_none(str, data.get("park"), Unknown.REGULAR)
        self.ex_eligible = check_for_none(
            int, data.get("is_ex_raid_eligible"), Unknown.REGULAR
        )
        self.is_exclusive = check_for_none(
            int, data.get("is_exclusive"), Unknown.REGULAR
        )

        # Gym Team (this is only available from cache)
        self.current_team_id = check_for_none(
            int, data.get("team_id", data.get("team")), Unknown.TINY
        )

        self.name = self.gym_id
        self.geofence = Unknown.REGULAR
        self.custom_dts = {}

    def update_with_cache(self, cache):
        """Update event infos using cached data from previous events."""

        # Update available slots
        self.slots_available = cache.gym_slots(self.gym_id)
        self.guard_count = (
            (6 - self.slots_available)
            if Unknown.is_not(self.slots_available)
            else Unknown.TINY
        )

    def generate_dts(self, locale, timezone, units):
        """Return a dict with all the DTS for this event."""
        hatch_time = get_time_as_str(self.hatch_time, timezone)
        raid_end_time = get_time_as_str(self.raid_end, timezone)
        weather_name = locale.get_weather_name(self.weather_id)
        dts = self.custom_dts.copy()
        dts.update(
            {
                # Identification
                "gym_id": self.gym_id,
                # Hatch Time Remaining
                "hatch_time_left": hatch_time[0],
                "12h_hatch_time": hatch_time[1],
                "24h_hatch_time": hatch_time[2],
                "hatch_time_no_secs": hatch_time[3],
                "12h_hatch_time_no_secs": hatch_time[4],
                "24h_hatch_time_no_secs": hatch_time[5],
                "hatch_time_raw_hours": hatch_time[6],
                "hatch_time_raw_minutes": hatch_time[7],
                "hatch_time_raw_seconds": hatch_time[8],
                "hatch_time_utc": self.hatch_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                # Raid Time Remaining
                "raid_time_left": raid_end_time[0],
                "12h_raid_end": raid_end_time[1],
                "24h_raid_end": raid_end_time[2],
                "raid_time_no_secs": raid_end_time[3],
                "12h_raid_end_no_secs": raid_end_time[4],
                "24h_raid_end_no_secs": raid_end_time[5],
                "raid_time_raw_hours": raid_end_time[6],
                "raid_time_raw_minutes": raid_end_time[7],
                "raid_time_raw_seconds": raid_end_time[8],
                "raid_end_utc": self.raid_end,
                "current_timestamp_utc": datetime.utcnow(),
                # Location
                "lat": self.lat,
                "lng": self.lng,
                "lat_5": "{:.5f}".format(self.lat),
                "lng_5": "{:.5f}".format(self.lng),
                "distance": (
                    get_dist_as_str(self.distance, units)
                    if Unknown.is_not(self.distance)
                    else Unknown.SMALL
                ),
                "direction": self.direction,
                "gmaps": get_gmaps_link(self.lat, self.lng, False),
                "gnav": get_gmaps_link(self.lat, self.lng, True),
                "applemaps": get_applemaps_link(self.lat, self.lng, False),
                "applenav": get_applemaps_link(self.lat, self.lng, True),
                "waze": get_waze_link(self.lat, self.lng, False),
                "wazenav": get_waze_link(self.lat, self.lng, True),
                "geofence": self.geofence,
                "weather_id": self.weather_id,
                "weather": weather_name,
                "weather_or_empty": Unknown.or_empty(weather_name),
                "weather_emoji": get_weather_emoji(self.weather_id),
                # Egg info
                "egg_lvl": self.egg_lvl,
                # Gym Details
                "gym_name": self.gym_name,
                "gym_description": self.gym_description,
                "gym_image": self.gym_image,
                "slots_available": self.slots_available,
                "guard_count": self.guard_count,
                "sponsor_id": self.sponsor_id,
                "sponsored": self.sponsor_id > 0
                if Unknown.is_not(self.sponsor_id)
                else Unknown.REGULAR,
                "ex_eligible": self.ex_eligible > 0
                if Unknown.is_not(self.ex_eligible)
                else Unknown.REGULAR,
                "ex_eligible_emoji": get_ex_eligible_emoji(self.ex_eligible),
                "is_exclusive": self.is_exclusive > 0
                if Unknown.is_not(self.is_exclusive)
                else Unknown.REGULAR,
                "park": self.park,
                "team_id": self.current_team_id,
                "team_emoji": get_team_emoji(self.current_team_id),
                "team_name": locale.get_team_name(self.current_team_id),
                "team_color": locale.get_team_color(self.current_team_id),
                "team_leader": locale.get_leader_name(self.current_team_id),
            }
        )
        return dts
