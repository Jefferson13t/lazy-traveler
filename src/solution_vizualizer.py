import plotly.graph_objects as go
import plotly.express as px
import json
from src.data_types import HolidayData
from collections import defaultdict

class SolutionVizualizer:
    """Displays the evolution of holidays across a Brazil map."""

    GEOJSON_PATH = "data/brazil_states.geojson"
    OUTPUT_FILE = "output/animated_solution.html"
    BRAZIL_CENTER = dict(lat=-15, lon=-54)
    REPRODUCTION_SPEED = 500
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
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title="Brazil Holiday Evolution Map",
            updatemenus=[{"type": "buttons", "buttons": [play_btn, pause_btn]}]
        )

    def draw_travel_schedule(
        self,
        holidays: list[HolidayData],
        solutions: list[list[dict[str, float]]]
    ) -> None:
        """Animate multiple travel solutions, each with its own color."""

        colors = px.colors.qualitative.Plotly

        by_day = defaultdict(list)
        for h in holidays:
            by_day[h.day_of_year].append(h)

        frames = []
        days = sorted(by_day.keys())

        num_solutions = len(solutions)

        for step, day in enumerate(days):

            if any(step >= len(sol) - 1 for sol in solutions):
                break

            cities = by_day[day]
            lons = [c.lon for c in cities]
            lats = [c.lat for c in cities]
            date_label = cities[0].date.strftime("%d/%m/%Y")

            frame_data = []

            # Feridos do dia
            frame_data.append(
                go.Scattergeo(
                    lon=lons,
                    lat=lats,
                    mode="markers",
                    marker=dict(size=7, color="green"),
                    name=f"Day {day}",
                )
            )

            # Segmentos de soluções
            for idx, sol in enumerate(solutions):
                city_from = sol[step]
                city_to = sol[step + 1]
                color = colors[idx % len(colors)]

                frame_data.append(
                    go.Scattergeo(
                        lon=[city_from["lon"], city_to["lon"]],
                        lat=[city_from["lat"], city_to["lat"]],
                        mode="lines+markers",
                        line=dict(width=2, color=color),
                        marker=dict(size=6, color="red"),
                        name=f"Sol {idx+1}: {city_from['name']} → {city_to['name']}",
                    )
                )

            # Anotações
            annotations = [
                dict(
                    text=date_label,
                    x=1, y=0.95,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=18),
                )
            ]

            for idx, sol in enumerate(solutions):
                city_from = sol[step]
                city_to = sol[step + 1]
                color = colors[idx % len(colors)]

                annotations.append(
                    dict(
                        text=f"<span style='color:{color}'>Sol {idx+1}: {city_from['name']} → {city_to['name']}</span>",
                        x=1, y=0.90 - idx * 0.07,
                        xref="paper", yref="paper",
                        showarrow=False,
                        font=dict(size=16),
                    )
                )

            frames.append(
                go.Frame(
                    name=str(step),
                    data=frame_data,
                    layout=go.Layout(annotations=annotations),
                )
            )

        self.fig.frames = frames
        self.fig.write_html(self.OUTPUT_FILE)
        self.fig.show()