import asyncio
import os
import logging
import re

import telethonpatch  # import for its side effects

from telethon import TelegramClient
from telethon import Button
from telethon.events import NewMessage, CallbackQuery
from telethon.utils import get_display_name


# strings
_START_STR = """
Hello {user}! 👋

Please click /numbers for to get all the Numbers.
"""


_NUMBER_STR = """
Thanks for showing your interest in my services.

Please Choose the Price range of your preference.
"""


# logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger("PriceBot")
log.info("Initiating Bot ...")


# asyncio loop
log.info("Starting asyncio Event loop ..")

try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


# load env if not on heroku
if not os.getenv("DYNO"):
    from dotenv import load_dotenv

    log.info("Loading ENV from File ..")
    load_dotenv()


# env checker
if not all(
    os.environ.get(i)
    for i in (
        "API_ID",
        "API_HASH",
        "BOT_TOKEN",
        "OWNER_USERNAME",
    )
):
    logger.critical("Missing some Variables! Check your ENV file..")
    quit(0)


# telethon client
log.info("Loading Telethon Client ..")

bot = TelegramClient(
    session=None if os.getenv("DYNO") else "PriceBot",
    # Use session file if not on Heroku.
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    base_logger=log,
    entity_cache_limit=3000,
)


log.info("Adding event Handlers ..")


@bot.on(
    NewMessage(
        incoming=True,
        pattern=re.compile("^/start$"),
        func=lambda e: e.is_private,
    )
)
async def _click_start(e):
    sender = e.sender or await e.get_sender()
    sender_name = get_display_name(sender)
    log.info(f"{sender_name} Just Started me!")
    tag = f"[{sender_name}](tg://user?id={sender.id})"
    buttons = (
        [Button.mention(sender_name, await e.client.get_input_entity(sender))]
        if sender.username
        else None
    )
    out = await asyncio.gather(
        e.respond(_START_STR.format(user=sender_name)),
        e.client.send_message(
            os.getenv("OWNER_USERNAME"),
            f"Started by - {sender.id} - {tag}",
            buttons=buttons,
        ),
        return_exceptions=True,
    )
    for r in out:
        if isinstance(r, Exception):
            log.exception(r)


@bot.on(
    NewMessage(
        incoming=True,
        pattern=re.compile("^/numbers$"),
        func=lambda e: e.is_private,
    )
)
async def _get_numbers(e):
    owner = await e.client.get_input_entity(os.getenv("OWNER_USERNAME"))
    buttons = [
        [
            Button.inline("Cheap Numbers", data="_all_cheap_numbers"),
            Button.inline("Expensive Numbers", data="_all_expensive_numbers"),
        ],
        [Button.mention("Link to My Owner!", owner)],
    ]
    await e.respond(_NUMBER_STR, buttons=buttons)


def get_numbers(of_type):
    nums = []
    _type = "CHEAPNUM_" if of_type == "cheap" else "EXPENSIVENUM_"
    for k, v in os.environ.items():
        if k.startswith(_type):
            nums.append((k.lstrip(_type).replace("_", " "), v))
    return nums


@bot.on(CallbackQuery(data=re.compile("^_get_numbers$")))
async def _cb_get_numbers(e):
    owner = await e.client.get_input_entity(os.getenv("OWNER_USERNAME"))
    buttons = [
        [
            Button.inline("Cheap Numbers", data="_all_cheap_numbers"),
            Button.inline("Expensive Numbers", data="_all_expensive_numbers"),
        ],
        [Button.mention("Link to My Owner!", owner)],
    ]
    await e.edit(_NUMBER_STR, buttons=buttons)


@bot.on(CallbackQuery(data=re.compile("^_all_cheap_numbers$")))
async def _cb_cheap_num(e):
    numbers = get_numbers("cheap")
    if not numbers:
        msg = "We do not have any number of this type right now.."
        await asyncio.sleep(1)
        return await e.answer(msg, alert=True)

    await e.answer("Please wait, getting your numbers.")
    out = "**Here's a list of all the cheap numbers you can get!**"
    buttons = [
        [Button.inline(i, data=f"buy_num_1_{i.replace(' ', '_')}")] for i, _ in numbers
    ]
    buttons = buttons[:48]
    owner = await e.client.get_input_entity(os.getenv("OWNER_USERNAME"))
    buttons.append(
        [
            Button.inline("Go Back", data="_get_numbers"),
            Button.mention("Talk to My Owner!", owner),
        ]
    )
    await asyncio.sleep(0.6)
    await e.edit(out, buttons=buttons)


@bot.on(CallbackQuery(data=re.compile("^_all_expensive_numbers$")))
async def _cb_expensive_num(e):
    numbers = get_numbers("expensive")
    if not numbers:
        msg = "We do not have any number of this type right now.."
        await asyncio.sleep(1)
        return await e.answer(msg, alert=True)

    await e.answer("Please wait, getting your numbers.")
    out = "**Here's a list of all the Expensive numbers you can get!**"
    buttons = [
        [Button.inline(i, data=f"buy_num_2_{i.replace(' ', '_')}")] for i, _ in numbers
    ]
    buttons = buttons[:48]
    owner = await e.client.get_input_entity(os.getenv("OWNER_USERNAME"))
    buttons.append(
        [
            Button.inline("Go Back", data="_get_numbers"),
            Button.mention("Talk to My Owner!", owner),
        ]
    )
    await asyncio.sleep(0.6)
    await e.edit(out, buttons=buttons)


@bot.on(CallbackQuery(data=re.compile(r"^buy_num_(\d)_(.+)")))
async def _cb_buy_numbers(e):
    of_type = e.data_match.group(1).decode()
    num = e.data_match.group(2).decode().replace("_", " ")
    numbers = get_numbers("cheap" if of_type == "1" else "expensive")
    price = next(filter(lambda i: i[0] == num, numbers))[1]
    await e.answer(f'Price for "{num}" is {price} !!', alert=True)


async def main():
    log.info("Connecting bot ..")
    await bot.start(bot_token=os.getenv("BOT_TOKEN"))
    await asyncio.sleep(1)
    bot.me = await bot.get_me()
    log.info(f"PriceBot Started Successfully - @{bot.me.username} ..")


loop.run_until_complete(main())
re.purge()
log.info("Running Loop forever ..")
bot.run_until_disconnected()
