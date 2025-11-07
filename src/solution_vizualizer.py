import plotly.graph_objects as go
from src.read_holiday import read_holidays
import json
from src.data_types import HolidayData, Solution


class SolutionVizualizer:
    """Displays the evolution of holidays across a Brazil map."""

    GEOJSON_PATH = "data/brazil_states.geojson"
    BRAZIL_CENTER = dict(lat=-15, lon=-54)
    REPRODUCTION_SPEED = 300
    LAT_RANGE = [-35, 6] 
    LON_RANGE = [-75, -30]

    def __init__(self) -> None:
        self.fig = go.Figure()
        self._setup_map()
        self._draw_states_contour()

    def _draw_states_contour(self) -> None:
        """Draw Brazil's state borders from a GeoJSON file."""
        with open(self.GEOJSON_PATH, encoding="utf-8") as f:
            geo = json.load(f)

        for feature in geo.get("features", []):
            if feature.get("geometry", {}).get("type") != "MultiPolygon":
                continue

            for multipolygon in feature["geometry"]["coordinates"]:
                for polygon in multipolygon:
                    lon, lat = zip(*polygon)
                    self.fig.add_trace(go.Scattergeo(
                        lon=lon, lat=lat,
                        mode="lines",
                        line=dict(width=1, color="black"),
                        showlegend=False
                    ))

    def _setup_map(self) -> None:
        """Configure base map layout and animation buttons."""

        play_btn = dict(
            label="▶️ Play",
            method="animate",
            args=[None, {"frame": {"duration": self.REPRODUCTION_SPEED, "redraw": True}}]
        )
        pause_btn = dict(
            label="⏸ Pause",
            method="animate",
            args=[[None], {"mode": "immediate", "frame": {"duration": 0}}]
        )

        self.fig.update_layout(
            geo=dict(
                projection_type="mercator",
                showcountries=False,
                showland=False,
                showocean=False,
                showcoastlines=False,
                showframe=True,
                bgcolor="rgba(0,0,0,0)",
                center=self.BRAZIL_CENTER,
                lataxis=dict(range=self.LAT_RANGE),
                lonaxis=dict(range=self.LON_RANGE),
            ),
            paper_bgcolor="rgba(0,0,0,0)",  # remove fundo branco do gráfico
            plot_bgcolor="rgba(0,0,0,0)",
            title="Brazil Holiday Evolution Map",
            updatemenus=[{"type": "buttons", "buttons": [play_btn, pause_btn]}]
        )

    def draw_travel_schedule(self, holidays: list[HolidayData], solution: Solution) -> None:
        """Animate holidays by day of the year."""
        frames = []

        for day in sorted({h.day_of_year for h in holidays}):
            cities = [h for h in holidays if h.day_of_year == day]
            if not cities:
                continue

            if(day >= len(solution) - 1):
                break

            lons = [h.lon for h in cities]
            lats = [h.lat for h in cities]
            date_label = cities[0].date.strftime("%d/%m/%Y")

            city_from = holidays[solution[day]]
            city_to = holidays[solution[day + 1]]

            frame = go.Frame(
                name=str(day),
                data=[
                    go.Scattergeo(
                        lon=lons, lat=lats,
                        mode="markers",
                        marker=dict(size=7, color="green"),
                        name=f"Day {day}"
                    ),
                    go.Scattergeo(
                        lon=[city_from.lon, city_to.lon],
                        lat=[city_from.lat, city_to.lat],
                        mode="lines+markers",
                        line=dict(width=2, color="blue"),
                        marker=dict(size=6, color="red"),
                        name=f"{city_from.city_name} → {city_to.city_name}",
                    )
                ],
                
                layout=go.Layout(
                    annotations=[
                        dict(
                            text=date_label,
                            x=1, y=0.95,
                            xref="paper", yref="paper",
                            showarrow=False,
                            font=dict(size=18, color="black")
                        ),
                        dict(
                            text=f"{city_from.city_name} -> {city_to.city_name}",
                            x=1, y=0.90,
                            xref="paper", yref="paper",
                            showarrow=False,
                            font=dict(size=18, color="black")
                        ),
                    ]
                )
            )

            frames.append(frame)

        self.fig.frames = frames
        self.fig.show()
