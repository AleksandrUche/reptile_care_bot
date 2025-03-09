import logging

import httpx

from config_data.config import URL_API_GEO, API_KEY_GEO

logger = logging.getLogger(__name__)


class GeoAPIClient:
    """http://api.geonames.org/"""
    def __init__(self, url: str = URL_API_GEO, api_key: str = API_KEY_GEO):
        self.url_geo = url
        self.api_key = api_key

    async def get_coord_by_city(self, city_name: str) -> dict | None:
        """
        Получение координат по названию города
        :param city_name: Название города.
        :return {'lng': 28.03372, 'lat': -32.6749}
        """
        params = {
            "q": city_name,
            "username": self.api_key
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.url_geo + "searchJSON", params=params
            )
            data = response.json()

            try:
                coords = data['geonames'][0]
                return {'lng': float(coords['lng']), 'lat': float(coords['lat'])}
            except Exception as e:
                logger.error(
                    "Не удалось определить координаты для "
                    f"города {city_name} ошибка: {e}", exc_info=True
                )

    async def get_timezone_by_coord(self, coord: dict) -> dict | None:
        """
        Получение тайм зоны по координатам
        :param coord: Принимает словарь {'lng': float, 'lat': float}
        :return {'timezone': 'Africa/Johannesburg', 'offset': 2}
        """
        params = {
            'lat': coord['lat'],
            'lng': coord['lng'],
            "username": self.api_key,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.url_geo + 'timezoneJSON', params=params
            )
            data = response.json()

            try:
                return {'timezone': data["timezoneId"], 'offset': data['gmtOffset']}
            except Exception as e:
                logger.error(
                    f"Не удалось определить часовой пояс и смещение по {coord} ошибка: {e}",
                    exc_info=True
                )
