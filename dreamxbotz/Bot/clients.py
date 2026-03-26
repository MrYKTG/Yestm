import asyncio
import logging
from info import *
from pyrogram import Client
from . import multi_clients, work_loads, dreamxbotz


async def initialize_clients():
    multi_clients[0] = dreamxbotz
    work_loads[0] = 0
    print("Using default client only (streaming removed)")
