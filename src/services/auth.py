from functools import lru_cache


class AuthService:
    pass


@lru_cache()
def get_auth_service(
    cache: ICache = Depends(get_cache),
    elastic: ElasticStorage = Depends(get_elastic),
) -> AuthService:
    cache_handler = CachePersonHandler(cache, PERSON_CACHE_EXPIRE_IN_SECONDS)
    storage_handler = ElasticPersonHandler(elastic)

    return AuthService(cache_handler, storage_handler)