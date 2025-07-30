import re
import csv
import hashlib
from enum import Enum
from typing import cast
from pathlib import Path
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime
from tabulate import tabulate


class FieldName(Enum):
    """CSV Field name to Model Field Name"""

    COMPANY_NAME = "Company"
    HQ_LOCATION = "Location HQ"
    NO_LAYOFF = "# Laid Off"
    DATE = "Date"
    PERCENTAGE = "%"
    INDUSTRY = "Industry"
    SOURCE = "Source"
    STAGE = "Stage"
    RAISED = "$ Raised (mm)"
    COUNTRY = "Country"
    DATE_ADDED = "Date Added"
    DATE_FORMAT_REGEX = r"(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})"


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""

    pass


class LayOff(Base):
    """LayOff model for SQLAlchemy ORM"""

    __tablename__ = "layoffs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company = Column(String, nullable=False)
    hq_location = Column(String, nullable=True)
    no_layoff = Column(Integer, nullable=True)
    date = Column(DateTime, nullable=True)
    percentage = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    source = Column(String, nullable=True)
    stage = Column(String, nullable=True)
    raised = Column(String, nullable=True)
    country = Column(String, nullable=True)
    date_added = Column(DateTime, nullable=True)

    row_signature = Column(String(32), nullable=True, index=True, unique=False)

    @staticmethod
    def as_context(layoffs: list["LayOff"]) -> str:

        headers = [
            "Company",
            "Location HQ",
            "# Laid Off",
            "Date",
            "%",
            "Industry",
            "Source",
            "Stage",
            "$ Raised (mm)",
            "Country",
            "Date Added",
        ]

        rows = [
            [
                layoff.company,
                layoff.hq_location,
                layoff.no_layoff,
                layoff.date.strftime("%Y-%m-%d"),
                layoff.percentage,
                layoff.industry,
                layoff.source,
                layoff.stage,
                layoff.raised,
                layoff.country,
                layoff.date_added.strftime("%Y-%m-%d"),
            ]
            for layoff in layoffs
        ]

        return f"```markdown\n### Layoffs\n{tabulate(rows, headers=headers, tablefmt='pipe')}\n```"

    @staticmethod
    def from_csv(csv_file_path: Path) -> list["LayOff"]:
        """Load Layoff data from CSV"""

        layoff_data: list[LayOff] = []

        with open(csv_file_path, mode="r", encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                layoff = LayOff(
                    company=row[FieldName.COMPANY_NAME.value],
                    hq_location=(
                        row[FieldName.HQ_LOCATION.value].strip().lower()
                        if FieldName.HQ_LOCATION.value in row
                        and row[FieldName.HQ_LOCATION.value]
                        else None
                    ),
                    no_layoff=(
                        int(row[FieldName.NO_LAYOFF.value])
                        if FieldName.NO_LAYOFF.value in row
                        and row[FieldName.NO_LAYOFF.value]
                        else None
                    ),
                    date=(
                        LayOff.parse_date(row[FieldName.DATE.value])
                        if FieldName.DATE.value in row and row[FieldName.DATE.value]
                        else None
                    ),
                    percentage=(
                        row[FieldName.PERCENTAGE.value].strip().lower()
                        if FieldName.PERCENTAGE.value in row
                        and row[FieldName.PERCENTAGE.value]
                        else None
                    ),
                    industry=(
                        row[FieldName.INDUSTRY.value].strip().lower()
                        if FieldName.INDUSTRY.value in row
                        and row[FieldName.INDUSTRY.value]
                        else None
                    ),
                    source=(
                        row[FieldName.SOURCE.value].strip().lower()
                        if FieldName.SOURCE.value in row and row[FieldName.SOURCE.value]
                        else None
                    ),
                    stage=(
                        row[FieldName.STAGE.value].strip().lower()
                        if FieldName.STAGE.value in row and row[FieldName.STAGE.value]
                        else None
                    ),
                    raised=(
                        row[FieldName.RAISED.value].strip().lower()
                        if FieldName.RAISED.value in row and row[FieldName.RAISED.value]
                        else None
                    ),
                    country=(
                        row[FieldName.COUNTRY.value].strip().lower()
                        if FieldName.COUNTRY.value in row
                        and row[FieldName.COUNTRY.value]
                        else None
                    ),
                    date_added=(
                        LayOff.parse_date(row[FieldName.DATE_ADDED.value])
                        if row[FieldName.DATE_ADDED.value]
                        else None
                    ),
                    row_signature=LayOff.compute_row_signature(
                        row[FieldName.COMPANY_NAME.value],
                        LayOff.parse_date(row[FieldName.DATE.value]),
                        row[FieldName.COUNTRY.value],
                        LayOff.parse_date(row[FieldName.DATE_ADDED.value]),
                    ),
                )
                layoff_data.append(layoff)

        return layoff_data

    @staticmethod
    def parse_date(date: str) -> datetime:
        # Convert date in mm/dd/yyyy or mm-dd-yy format to datetime
        matches = cast(re.Match[str], re.match(FieldName.DATE_FORMAT_REGEX.value, date))
        match_groups = matches.groups()

        assert match_groups is not None, "Date format is incorrect"

        month, day, year = match_groups

        # Add 20 infront of year if in yy format
        if len(year) == 2:
            year = "20" + year

        month, day, year = int(month), int(day), int(year)

        date_parsed = datetime(year=year, month=month, day=day)

        return date_parsed

    @staticmethod
    def compute_row_signature(company, date, country, date_added) -> str | None:
        if any(field is None for field in [company, date, country, date_added]):
            return None

        composite_string = f"{company.strip().lower()}|{date.isoformat()}|{country.strip().lower()}|{date_added.isoformat()}"
        return hashlib.md5(composite_string.encode()).hexdigest()
