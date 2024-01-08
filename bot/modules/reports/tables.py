"""
MIT License

Copyright (c) 2024 ArtyomK

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

from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime, Text, Boolean

from bot.models import Base


class Report(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False)
    applicant_discord_id = Column(BigInteger, nullable=False)
    defendant_discord_id = Column(BigInteger, nullable=False)
    judge_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    rule = Column(Integer, ForeignKey("reports_rule.id"))
    photo_proof_url = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="Open")


class Rule(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False)
    code = Column(String(5), nullable=False)
    description = Column(String(1000), nullable=False)
    violation_action = Column(Text, nullable=False)


class Settings(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False)
    auto_action = Column(Boolean, nullable=False, default=False)
    moderator_roles = Column(Text, nullable=False, default="")
    channels_category = Column(BigInteger, nullable=True)
