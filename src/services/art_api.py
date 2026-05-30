import httpx

from ..config import get_settings


class ArtInstituteClient:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def get_artwork(self, external_id: str) -> dict:
        response = httpx.get(
            f"{self.base_url}/artworks/{external_id}",
            params={"fields": "id,title"},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data")
        if not isinstance(data, dict):
            raise ValueError("invalid response from art institute api")
        return data

    def validate_place_exists(self, external_id: str) -> bool:
        try:
            self.get_artwork(external_id)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return False
            raise
        return True


def get_art_institute_client() -> ArtInstituteClient:
    settings = get_settings()
    return ArtInstituteClient(
        base_url=settings.art_api_base_url,
        timeout_seconds=settings.art_api_timeout_seconds,
    )
