import requests
import folium
from folium.plugins import MarkerCluster
import time

# URL de l'API pour toutes les stations (version 3)
api_url = "https://api.jcdecaux.com/vls/v3/stations?apiKey=e0a1bf2c844edb9084efc764c089dd748676cc14"

# Récupérer les données de l'API
def get_data_from_api(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Erreur lors de la récupération des données : ", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("Erreur de requête : ", e)
        return None
# Récupération et traitement des données des stations et affichage dans la console
def process_data(data):
    if data:
        cities = {}
        for station in data:
            city = station.get('contractName')
            bikes_available = station.get('totalStands').get('availabilities').get('bikes')
            bikes_electric = station.get('totalStands').get('availabilities').get('electricalBikes') if station.get('totalStands').get('availabilities').get('electricalBikes') is not None else 0
            bikes_mecanic = station.get('totalStands').get('availabilities').get('mechanicalBikes') if station.get('totalStands').get('availabilities').get('mechanicalBikes') is not None else 0
            # Ajout du nombre de vélos de chaque station par ville
            if city in cities:
                cities[city]['total_bikes'] += bikes_available
                cities[city]['electric_bikes'] += bikes_electric
                cities[city]['mechanical_bikes'] += bikes_mecanic
            else:
                cities[city] = {'total_bikes': bikes_available, 'electric_bikes': bikes_electric, "mechanical_bikes": bikes_mecanic}

        for city, info in cities.items():
            total_bikes = info['total_bikes']
            electric_bikes = info['electric_bikes']
            mechanical_bikes = info['mechanical_bikes']
            # Calcul des pourcentages
            if total_bikes > 0:
                percentage_electric = (electric_bikes / total_bikes) * 100
            else:
                percentage_electric = 0
            percentage_mechanical = 100 - percentage_electric
            
            # Affichage des données dans la console
            print("Ville :", city)
            print("Nombre total de vélos :", total_bikes, "Nombre de vélos électriques :", electric_bikes, "Nombre de vélos mécaniques :", mechanical_bikes)
            print("Pourcentage de vélos électriques :", round(percentage_electric, 2), "%" ) 
            print("Pourcentage de vélos mécaniques :", round(percentage_mechanical, 2), "%")
            print("-------------------")

        # Classement des villes en fonction du nombre total de vélos
        sorted_cities = sorted(cities.items(), key=lambda x: x[1]['total_bikes'] , reverse=True)
        print("\nClassement des villes avec le plus de vélos :")
        for i, (city, info) in enumerate(sorted_cities, start=1):
            print(f"{i}. {city} - {info['total_bikes']} vélos")

# Convertir les stations en GeoJSON
def stations_to_geojson(stations):
    features = []
    for station in stations:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [station['position']['longitude'], station['position']['latitude']]
            },
            "properties": {
                "name": station['name'],
                "bikes_available": station['totalStands']['availabilities']['bikes'],
                "stands_available": station['totalStands']['availabilities']['stands'],
                "status": station['status']
            }
        }
        features.append(feature)
    
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }
    return geojson_data

# Créer une carte avec un MarkerCluster et GeoJSON dynamique
def create_dynamic_map(geojson_data):
    # Initialiser la carte
    map = folium.Map(location=[48.8566, 2.3522], zoom_start=5)

    # Ajouter un MarkerCluster pour grouper les marqueurs
    marker_cluster = MarkerCluster().add_to(map)

    # Ajouter les données GeoJSON au cluster
    folium.GeoJson(
        geojson_data,
        name="Stations",
        popup=folium.GeoJsonPopup(fields=["name", "bikes_available", "stands_available", "status"]),
    ).add_to(marker_cluster)

    # Sauvegarder la carte dans un fichier HTML
    map.save("index.html")

# Fonction principale pour exécuter le script
def main():
    while True:
        # Récupérer les données de l'API
        api_data = get_data_from_api(api_url)
        
        if api_data:
            # Traiter les données
            process_data(api_data)
            
            # Convertir les stations en GeoJSON
            geojson_data = stations_to_geojson(api_data)

            # Créer la carte avec les données GeoJSON
            create_dynamic_map(geojson_data)
        
        time.sleep(60)  # Attendre 60 secondes avant de mettre à jour

if __name__ == "__main__":
    main()
