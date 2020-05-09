msclient_user = None
msclient_media = None
msclient_shop = None
msclient_common = None
msclient_transaction = None
msclient_threed = None


def init_msclient_user(user_client_settings, user_redis_client, logger):
    from core_msclients import user as msclients_user

    global msclient_user
    msclient_user = msclients_user.UserServiceClient(
        user_client_settings, user_redis_client, logger)


def init_msclient_transaction(transaction_client_settings, transaction_redis_client, logger):
    from core_msclients import transaction as msclients_transaction

    global msclient_transaction
    msclient_transaction = msclients_transaction.TransactionServiceClient(
        transaction_client_settings, transaction_redis_client, logger)


def init_msclient_shop(shop_client_settings, shop_redis_client, logger):
    from core_msclients import shop as msclients_shop

    global msclient_shop
    msclient_shop = msclients_shop.ShopServiceClient(
        shop_client_settings, shop_redis_client, logger)


def init_msclient_media(media_client_settings, media_redis_client, logger):
    from core_msclients import media as msclients_media

    global msclient_media
    msclient_media = msclients_media.MediaServiceClient(
        media_client_settings, media_redis_client, logger)


def init_msclient_common(common_client_settings, common_redis_client, logger):
    from core_msclients import common as msclients_common

    global msclient_common
    msclient_common = msclients_common.CommonServiceClient(
        common_client_settings, common_redis_client, logger)


def init_msclient_threed(common_client_settings, common_redis_client, logger):
    from core_msclients import threed as msclients_threed

    global msclient_threed
    msclient_threed = msclients_threed.ThreedServiceClient(
        common_client_settings, common_redis_client, logger)