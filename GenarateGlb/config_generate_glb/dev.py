
import os

from .clients import (init_msclient_common, init_msclient_media,
                            init_msclient_threed,
                            init_msclient_shop, init_msclient_transaction,
                            init_msclient_user)
from core_msclients.redis.client import RedisClient
from core_msclients.settings import (COMMON_CLIENT_DEFAULTS,
                                     MEDIA_CLIENT_DEFAULTS,
                                     SHOP_CLIENT_DEFAULTS,
                                     TRANSACTION_CLIENT_DEFAULTS,
                                     THREED_CLIENT_DEFAULTS,
                                     USER_CLIENT_DEFAULTS, AppSettings)
from core_sharedlib import logging as sharedlib_logging

DEBUG = True
MODE = "dev"
MICROSERVICE = "shop"
PROJECT = os.environ.get("PROJECT_NAME")
LOGGER = sharedlib_logging.get_logger(MICROSERVICE, MODE)
REDIS_CONF = {
    "host": "coolnas.synology.me",
    "port": 9071,
    "db": 5
}

CDN_HOSTNAME = "coolnas.synology.me:9091/jewel-dev-media-public" #9091
BUCKET = {"AWS_S3_ENDPOINT_URL": "coolnas.synology.me:9905", "AWS_S3_REGION": "us-east-1", "AWS_S3_BUCKET_CDN_HOST": ""},

if os.environ.get("devops", "False") == "True":

    #########################################
    # logger
    #########################################

    LOGGER = sharedlib_logging.get_logger(MICROSERVICE, MODE)

    #########################################
    #  Clients
    #########################################

    SHOP_CLIENT_SETTINGS = {
        "LOCAL_SERVICE": MICROSERVICE.upper(),
        "REMOTE_SERVICE_URL": "coolnas.synology.me:9091/shop/graphql/",
        "REMOTE_SERVICE_PROTOCOL": "http",
        "REMOTE_SERVICE_APIKEY": "s/kiB06Xg^bcX[C*zB0KF*nZ$</g33",
        "REDIS_CACHE_HOST": "redis://{}".format(REDIS_CONF.get("host")),
        "REDIS_CACHE_DB": 5,
        "REDIS_CACHE_ADDRESS": [{
            "host": REDIS_CONF.get("host"),
            "port": REDIS_CONF.get("port"),
            "db": REDIS_CONF.get("db")
        }]
    }


    MEDIA_CLIENT_SETTINGS = {
        "LOCAL_SERVICE": MICROSERVICE.upper(),
        "REMOTE_SERVICE_URL": "coolnas.synology.me:9083/media/graphql/",
        "REMOTE_SERVICE_PROTOCOL": "http",
        "REMOTE_SERVICE_APIKEY": "s/kiB06Xg^bcX[C*zB0KF*nZ$</g33",
        "REDIS_CACHE_HOST": "redis://{}".format(REDIS_CONF.get("host")),
        "REDIS_CACHE_DB": 3,
        "CDN_HOSTNAME": CDN_HOSTNAME,
        "REDIS_CACHE_ADDRESS": [{
            "host": REDIS_CONF.get("host"),
            "port": REDIS_CONF.get("port"),
            "db": 3
        }]
    }

    media_client_settings = AppSettings(
        user_settings=MEDIA_CLIENT_SETTINGS,
        defaults=MEDIA_CLIENT_DEFAULTS,
    )

    shop_client_settings = AppSettings(
        user_settings=SHOP_CLIENT_SETTINGS,
        defaults=SHOP_CLIENT_DEFAULTS,
    )

    media_redis_client = RedisClient(media_client_settings, ms="media")
    media_redis_client.connect()

    shop_redis_client = RedisClient(shop_client_settings, ms="media")
    shop_redis_client.connect()

    init_msclient_media(media_client_settings,
                        media_redis_client, LOGGER)

    init_msclient_shop(shop_client_settings,
                       shop_redis_client, LOGGER)