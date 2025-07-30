from typing import Optional
from contextvars import ContextVar
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from job_analyzer.database.models import LayOff
from utils.vars import get_layoff_db
from sqlalchemy import and_
from datetime import datetime, timedelta


layoff_db_context: ContextVar[AsyncSession] = ContextVar("layoff_context")

layoff_db_engine = create_async_engine(get_layoff_db())

layoff_db_session = async_sessionmaker(layoff_db_engine, expire_on_commit=False)


async def get_recent_layoff(
    company_name: Optional[str] = None,
    days: Optional[int] = 10,
    hq_location: Optional[str] = None,
    industry: Optional[str] = None,
    date: Optional[str] = None,
    stage: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    session: Optional[AsyncSession] = None,
) -> list[LayOff]:
    """Retrieve recent layoff records based on various filters."""

    # Session fallback logic
    close_session = False

    if session is None:
        try:
            session = layoff_db_context.get()
        except LookupError:
            session = layoff_db_session()
            close_session = True
    filters = []

    if company_name:
        filters.append(LayOff.company.ilike(company_name))
    if hq_location:
        filters.append(LayOff.hq_location.ilike(hq_location))
    if industry:
        filters.append(LayOff.industry.ilike(industry))
    if stage:
        filters.append(LayOff.stage.ilike(stage))
    if country:
        filters.append(LayOff.country.ilike(country))
    if date:
        filters.append(LayOff.date == date)
    elif days is not None:
        since_date = datetime.now() - timedelta(days=days)
        filters.append(LayOff.date >= since_date.date())

    stmt = select(LayOff)
    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.limit(limit).offset(offset)

    try:
        result = await session.execute(stmt)
        return list(result.scalars().all())

    except LookupError:
        async with layoff_db_session() as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())
    finally:
        if close_session:
            await session.close()


async def get_field_unique_values(
    field_name: str, session: Optional[AsyncSession] = None
) -> list[str]:
    """Get unique values for a specific field in the LayOff table."""
    if session is None:
        session = layoff_db_context.get()

    stmt = select(getattr(LayOff, field_name)).distinct()
    async with session as s:
        result = await s.execute(stmt)
        return [row[0] for row in result.fetchall() if row[0] is not None]


async def add_layoff(layoff: LayOff, session: Optional[AsyncSession] = None) -> None:
    """Add a layoff record to the database."""
    if session is None:
        session = layoff_db_context.get()

    async with session.begin():
        session.add(layoff)


async def add_layoff_bulk(
    layoffs: list[LayOff], session: Optional[AsyncSession] = None
) -> None:
    """Add list of multiple record to the database."""

    if session is None:
        session = layoff_db_context.get()

    async with session.begin():
        session.add_all(layoffs)


async def add_partial_layoff(
    layoffs: list[LayOff], session: Optional[AsyncSession] = None
) -> None:
    """Only Add Layoff records that do not already exist in the database.
    Terminates early if a duplicate is found as all subsequent records would be duplicates.
    """

    if session is None:
        session = layoff_db_context.get()

    incoming_signatures = {l.row_signature for l in layoffs}

    stmt = select(LayOff.row_signature).where(
        LayOff.row_signature.in_(incoming_signatures)
    )
    result = await session.execute(stmt)
    existing_signatures = {row[0] for row in result.fetchall()}

    new_layoffs = [l for l in layoffs if l.row_signature not in existing_signatures]

    if new_layoffs:
        async with session.begin():
            session.add_all(new_layoffs)


async def update_layoff(layoff: LayOff, session: Optional[AsyncSession] = None) -> None:
    """Update an existing layoff record in the database."""
    if session is None:
        session = layoff_db_context.get()

    async with session.begin():
        await session.merge(layoff)
        await session.commit()


async def delete_layoff(layoff_id: int, session: Optional[AsyncSession] = None) -> None:
    """Delete a layoff record from the database by its ID."""
    if session is None:
        session = layoff_db_context.get()

    async with session.begin():
        stmt = select(LayOff).where(LayOff.id == layoff_id)
        result = await session.execute(stmt)
        layoff_record = result.scalar_one_or_none()

        if layoff_record:
            await session.delete(layoff_record)
            await session.commit()
