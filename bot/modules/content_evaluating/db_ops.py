"""
MIT License

Copyright (c) 2024 Shandy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from .errors import EmojiSetNotFoundError
from .tables import Emoji, EmojiSet
from bot.models import Session


def get_emoji_sets():
    with Session() as session:
        sets = session.query(EmojiSet, Emoji).join(Emoji).all()
    return sets


def get_emoji_set(set_id: int):
    with Session() as session:
        emoji_set = session.query(EmojiSet).join(Emoji).filter_by(id=set_id).first()
    if not emoji_set:
        raise EmojiSetNotFoundError
    return emoji_set


def add_emoji_to_set(set_id: int, emoji_id: int):
    with Session() as session:
        session.add(Emoji(emoji_id=emoji_id, emoji_set_id=set_id))
        session.commit()


def add_emoji(emoji: str) -> Emoji:
    with Session() as session:
        emoji_obj = Emoji(emoji=emoji)
        session.add(emoji_obj)
        session.commit()
    return emoji_obj
