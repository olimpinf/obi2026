import folium
import os
import sys
import numpy as np
from sklearn.cluster import DBSCAN
from haversine import haversine, Unit

from django.core.management.base import BaseCommand
from django.db.models import Count
from math import radians, cos, sin, asin, sqrt
from collections import defaultdict

from principal.models import States, Cities, School, Compet


LONGEST_DIST = 30 # in km

def draw_map(self, cities_map, clusters):
    # Center the map roughly on Brazil
    m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

    colors = [
        "black",
        "blue",
        "cadetblue",
        "darkblue",
        "darkgray",
        "darkgreen",
        "darkpurple",
        "darkred",
        "green",
        "lightblue",
        "lightgreen",
        "lightred",
        "orange",
        "purple",
        "red",
    ]

    print("len(clusters)" ,len(clusters))
    print("len(cities_map)", len(cities_map))

    for idx, cluster in clusters.items():
        #    for idx, cluster in enumerate(clusters, start=1):
        color = colors[(idx - 1) % len(colors)]
        for (city) in cluster:
            #city = cities_map.get((city_name, state))
            if not city:
                print("???")
                print(cluster)
                sys.exit(0)
            #label = f"Cluster {idx}: {city.name}/{city.state_id}"
            label = f"Cluster {idx}: {city.name}"
            folium.Marker(
                location=[city.lat, city.lng],
                radius=6,
                popup=label,
                color=color,
                icon=folium.Icon(color=color),
                fill=True,
                fill_color=color,
            ).add_to(m)

    # Save to file
    output_file = "clusters_map.html"
    m.save(output_file)

    self.stdout.write(self.style.SUCCESS(f"\nMap saved to {os.path.abspath(output_file)}"))



class Command(BaseCommand):
    help = "Find clusters of cities (≤ LONGEST_DIST km apart), using capitals as seeds."

    def handle(self, *args, **options):
        # Step 1: Get all cities that match the compet filter
        states = States.objects.all()
        comps = Compet.objects.filter(
            #compet_type__in=[1, 2, 7],
            compet_type__in=[3,4,5,6],
            #compet_type__in=[3,5],
            #compet_type__in=[4,6],
            compet_classif_fase2=True
        ).select_related("compet_school")

        # Group counts per city+school
        city_school_counts = {}
        for c in comps:
            school = c.compet_school
            key = (school.school_city, school.school_state)
            city_school_counts.setdefault(key, {})
            city_school_counts[key].setdefault(school.school_name, 0)
            city_school_counts[key][school.school_name] += 1

        # Load Cities from DB for these schools
        all_city_keys = list(city_school_counts.keys())
        cities = []
        cities_map = {}
        for city_name, state in all_city_keys:
            try:
                state_obj = states.get(short_name=state)
                city_obj = Cities.objects.get(name=city_name,state_id=state_obj.id)
                cities_map[(city_name, state)] = city_obj
                cities.append(city_obj)
            except Cities.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"City not found in Cities table: {city_name} ({state})"
                ))

        if not cities:
            self.stdout.write(self.style.ERROR("No valid cities found"))
            return

        # Step 2: Prepare coordinates for DBSCAN
        coords = np.array([(c.lat, c.lng) for c in cities])

        # Custom haversine distance
        def haversine_distance(u, v):
            return haversine(u, v, unit=Unit.KILOMETERS)

        # Step 3: Run DBSCAN
        clustering = DBSCAN(eps=LONGEST_DIST, min_samples=1, metric=haversine_distance)
        labels = clustering.fit_predict(coords)

        # Step 4: Build clusters
        clusters = {}
        for label, city in zip(labels, cities):
            clusters.setdefault(label, []).append(city)

        # Step 5: Print results
        for cluster_id, cluster_cities in clusters.items():
            # Find a capital in the cluster (if exists)
            capital = next((c for c in cluster_cities if c.is_capital), None)
            cluster_name = capital.name if capital else cluster_cities[0].name

            total_students = 0
            self.stdout.write(self.style.SUCCESS(
                f"\nCluster {cluster_id} (site: {cluster_name})"
            ))

            for city in cluster_cities:
                city_key_matches = [
                    k for k in city_school_counts.keys() if k[0] == city.name
                ]
                for city_key in city_key_matches:
                    schools = city_school_counts[city_key]
                    for school_name, count in schools.items():
                        total_students += count
                        self.stdout.write(
                            f"   {city.name} - {school_name}: {count} compets"
                        )

            self.stdout.write(self.style.NOTICE(
                f"   >> Total compets in cluster: {total_students}"
            ))
            
        draw_map(self, cities_map, clusters)

    
    def handle2(self, *args, **options):
        states = States.objects.all()
        compets = (
            Compet.objects.select_related("compet_school")
            .filter(compet_type__in=[1, 2, 7], compet_classif_fase2=True)
        )

        # Get unique city/state combos from schools
        city_names = {(c.compet_school.school_city, c.compet_school.school_state) for c in compets}

        # Map city -> Cities object
        cities_map = {}
        for name, state in city_names:
            try:
                state_obj = states.get(short_name=state)
                city_obj = Cities.objects.get(name=name,state_id=state_obj.id)
                cities_map[(name, state)] = city_obj
            except Cities.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"City not found in Cities table: {name}/{state}"))

        # Separate capitals and non-capitals
        capitals = {k: v for k, v in cities_map.items() if v.is_capital}
        non_capitals = {k: v for k, v in cities_map.items() if not v.is_capital}

        
        
        assigned = set()
        clusters = []

        # Step 1. Build clusters around capitals
        for cap_key, cap_city in capitals.items():
            cluster = [cap_key]
            assigned.add(cap_key)

            for nc_key, nc_city in non_capitals.items():
                if nc_key in assigned:
                    continue
                dist = haversine(cap_city.lat, cap_city.lng, nc_city.lat, nc_city.lng)
                if dist <= LONGEST_DIST:
                    cluster.append(nc_key)
                    assigned.add(nc_key)

            clusters.append(cluster)

        # Step 2. Assign leftover non-capitals
        for nc_key, nc_city in non_capitals.items():
            if nc_key in assigned:
                continue

            # Find nearest capital
            nearest_cap, nearest_dist = None, float("inf")
            for cap_key, cap_city in capitals.items():
                dist = haversine(cap_city.lat, cap_city.lng, nc_city.lat, nc_city.lng)
                if dist < nearest_dist:
                    nearest_cap, nearest_dist = cap_key, dist

            if nearest_cap and nearest_dist <= LONGEST_DIST:
                # Attach to nearest capital cluster
                for cluster in clusters:
                    if nearest_cap in cluster:
                        cluster.append(nc_key)
                        assigned.add(nc_key)
                        break
            else:
                # Standalone cluster
                clusters.append([nc_key])
                assigned.add(nc_key)

        # Step 3. Summarize results
        for idx, cluster in enumerate(clusters, start=1):
            self.stdout.write(self.style.MIGRATE_HEADING(f"\nCluster {idx}"))

            total_compets = 0

            for (city_name, state) in cluster:
                city_compets = compets.filter(
                    compet_school__school_city=city_name,
                    compet_school__school_state=state,
                )
                count = city_compets.count()
                total_compets += count
                self.stdout.write(f"  City: {city_name}/{state} ({count} students)")

                schools = (
                    city_compets.values("compet_school__school_name")
                    .annotate(num=Count("compet_id"))
                    .order_by("-num")
                )
                for s in schools:
                    self.stdout.write(f"     - {s['compet_school__school_name']}: {s['num']}")

            self.stdout.write(self.style.SUCCESS(f"==> Total in cluster {idx}: {total_compets} compets"))

        draw_map(self, cities_map, clusters)
            
