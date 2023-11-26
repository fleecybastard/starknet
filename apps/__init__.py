from client import Client
from enums import AppTypeEnum

from .BaseApp import BaseApp
from .dexes.BaseDex import BaseDex
from .Dmail import Dmail
from .ZkLendCollateral import ZkLendCollateral
from .StarknetId import StarknetId
from .StarkVerse import StarkVerse
from .dexes import SithSwap
from .dexes import MySwap
from .dexes import JediSwap
from .dexes import TenKSwap
from .lendings import BaseLending
from .lendings import ZkLend


apps_classes = [
    Dmail,
    StarknetId,
    ZkLendCollateral,
    JediSwap,
    MySwap,
    SithSwap,
    TenKSwap,
    ZkLend,
    StarkVerse
]


def get_apps(client: Client, app_type: AppTypeEnum) -> list[BaseApp]:
    apps = []
    for app_class in apps_classes:
        if app_class.app_type_ == app_type:
            apps.append(app_class(client))
    return apps
