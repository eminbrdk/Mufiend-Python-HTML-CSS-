import requests
import os


# Movie API
class TakeMovie():

    def data_without_description(self, movie_name):
        API_URL = "https://api.themoviedb.org/3/search/movie"
        API_KEY = "fe057624f880e42fb64f6a17f96892b4"

        params = {
            "api_key": API_KEY,
            "query": movie_name
        }
        response = requests.get(url=API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        movies = data["results"]
        movie_data = []

        for movie in movies:
            try:
                data = {
                    "title": movie["title"],
                    "poster_url": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",
                    "year": movie["release_date"].split("-")[0],
                    "overview": movie["overview"],
                    "vote": movie["vote_average"],
                    "data_id": movie["id"]
                }
            except KeyError:
                pass
            else:
                movie_data.append(data)

        return movie_data


    def data_with_movie_id(self, movie_id):
        API_URL = f"https://api.themoviedb.org/3/movie/{movie_id}"
        API_KEY = "fe057624f880e42fb64f6a17f96892b4"

        params = {
            "api_key": API_KEY
        }

        response = requests.get(url=API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        movie_data = []

        genre_data = []
        for genre in data["genres"]:
            try:
                genre_data.append(genre["name"])
            except KeyError:
                pass

        production_companies_data = []
        for com in data["production_companies"]:
            try:
                production_companies_data.append({
                    "company_name": com["name"],
                    "company_logo_url": f"https://image.tmdb.org/t/p/w500{com['logo_path']}"
                })
            except KeyError:
                pass

        production_countries_data = []
        for count in data["production_countries"]:
            try:
                production_countries_data.append(count["name"])
            except KeyError:
                pass

        movie_data = {
            "genres": genre_data,
            "companies": production_companies_data,
            "countries": production_countries_data
        }

        return movie_data







