import requests
import os


# Movie API
class TakeMovie():

    def data_without_description(self, movie_name):
        API_URL = "https://api.themoviedb.org/3/search/movie"
        API_KEY = os.environ.get("VAR_NAME")

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
                    "year": movie["release_date"].split("-")[0]
                }
            except KeyError:
                pass
            else:
                movie_data.append(data)

        return movie_data





