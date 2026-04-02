## Creates two ICO complaint volume tables
#Requirements: pip install sqlalchemy psycopg2-binary pandas

#Install dependencies
import sys
# !{sys.executable} -m pip install sqlalchemy psycopg2-binary pandas

#Imports
import os
import uuid
from datetime import date, datetime, timezone
from typing import Optional
import pandas as pd
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Date, Float,
    Integer, String, Text, create_engine, text
)
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Session

#Connection, update password before running
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:yourpassword@localhost:5432/ers_db"  # <- update this
)
engine = create_engine(DATABASE_URL, echo=False, future=True)
print("✓ Engine created")

#Base class
class Base(DeclarativeBase):
    pass

print("✓ Base class ready")

#I1: ICO Volume statistics
#Each row is one sector per reprting period
#Source: ICO website

class I1VolumeStatistics(Base):
    __tablename__ = "i1_volume_statistics"

    __table_args__ = (
        CheckConstraint(
            "period_type IN ('Annual', 'Quarterly', 'FOI Response')",
            name="ck_i1_period_type"
        ),
        CheckConstraint(
            "sector_relevance IN ('Full', 'Partial', 'None')",
            name="ck_i1_sector_relevance"
        ),
        CheckConstraint(
            "period_end > period_start",
            name="ck_i1_period_dates"
        ),
        CheckConstraint(
            "complaint_count >= 0",
            name="ck_i1_complaint_count"
        ),
    )

    # Primary key
    stat_id                 = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Reporting period
    period_start            = Column(Date, nullable=False, index=True)
    period_end              = Column(Date, nullable=False, index=True)
    period_type             = Column(String(20), nullable=False)

    # Sector
    ico_sector              = Column(String(200), nullable=False)        # Verbatim from ICO publication
    sector_relevance        = Column(String(10), nullable=False)         # Full, Partial, None — manually set

    # Volume counts
    complaint_count         = Column(Integer, nullable=False)
    data_breach_count       = Column(Integer)                            # Nullable: not always published

    # Resolution
    complaint_resolved      = Column(Boolean)
    complaint_resolved_pct  = Column(Float)                              # Computed: % resolved in period

    # Computed trend fields
    yoy_change_pct          = Column(Float)                              # Year-on-year % change vs same period last year
    qoq_change_pct          = Column(Float)                              # Quarter-on-quarter % change (quarterly only)
    avg_3period             = Column(Float)                              # Rolling 3-period average complaint count for sector
    pct_above_avg           = Column(Float)                              # ((complaint_count / avg_3period) - 1) as percentage
    spike_flag              = Column(Boolean)                            # TRUE if complaint_count > 1.5 * avg_3period

    # Provenance
    source_doc              = Column(Text)
    source_url              = Column(Text)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    manually_reviewed       = Column(Boolean, default=False, index=True)

    # Computed properties
    @property
    def computed_pct_above_avg(self) -> Optional[float]:
        """((complaint_count / avg_3period) - 1) as a percentage."""
        if self.complaint_count is not None and self.avg_3period and self.avg_3period > 0:
            return round((self.complaint_count / self.avg_3period - 1) * 100, 2)
        return None

    @property
    def computed_spike_flag(self) -> Optional[bool]:
        """TRUE if complaint_count > 1.5 * avg_3period."""
        if self.complaint_count is not None and self.avg_3period and self.avg_3period > 0:
            return self.complaint_count > 1.5 * self.avg_3period
        return None

    @property
    def period_label(self) -> str:
        """Human-readable period label e.g. 'Q1 2025' or 'FY 2024/25'."""
        if self.period_type == 'Annual':
            return f"FY {self.period_start.year}/{str(self.period_end.year)[2:]}"
        elif self.period_type == 'Quarterly':
            q = (self.period_start.month - 1) // 3 + 1
            return f"Q{q} {self.period_start.year}"
        return str(self.period_start)

    def __repr__(self) -> str:
        return f"<I1 {self.ico_sector} | {self.period_type} | complaints={self.complaint_count}>"


print("✓ I1VolumeStatistics defined")


#I2: ICO Volume Scores
#Each row is one scored sector snapshot
#Derived scoring table, computed from I1

class I2VolumeScores(Base):
    __tablename__ = "i2_volume_scores"

    __table_args__ = (
        CheckConstraint(
            "trend_direction IN ('Rising', 'Stable', 'Falling')",
            name="ck_i2_trend_direction"
        ),
        CheckConstraint(
            "volume_factor >= 0",
            name="ck_i2_volume_factor"
        ),
        CheckConstraint(
            "data_lag >= 0",
            name="ck_i2_data_lag"
        ),
    )

    # Primary key
    score_id                = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Links back to I1 sector
    ico_sector              = Column(String(200), nullable=False, index=True)

    # Reference period used for this score
    ref_period_start        = Column(Date, nullable=False)
    ref_period_end          = Column(Date, nullable=False)

    # Input values from I1
    complaint_count_used    = Column(Integer, nullable=False)            # complaint_count from reference period
    avg_3period_used        = Column(Float, nullable=False)              # avg_3period value used in computation

    # Computed scoring fields
    volume_factor           = Column(Float)                              # complaint_count / avg_3period
    trend_direction         = Column(String(10))                         # Rising, Stable, Falling
    spike_active            = Column(Boolean)                            # TRUE if spike_flag active in reference period

    # sector_risk_modifier = volume_factor * trend_multiplier * spike_modifier
    sector_risk_modifier    = Column(Float)

    # Data freshness
    data_lag                = Column(Integer)                            # Months between ref_period_end and computed_at
    stale_flag              = Column(Boolean)                            # TRUE if data_lag > 9 months
    computed_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Computed properties 
    @property
    def computed_volume_factor(self) -> Optional[float]:
        """Ratio of complaint_count to avg_3period."""
        if self.complaint_count_used and self.avg_3period_used and self.avg_3period_used > 0:
            return round(self.complaint_count_used / self.avg_3period_used, 4)
        return None

    @property
    def computed_data_lag(self) -> Optional[int]:
        """Months between ref_period_end and today."""
        if self.ref_period_end:
            today = date.today()
            return (today.year - self.ref_period_end.year) * 12 + \
                   (today.month - self.ref_period_end.month)
        return None

    @property
    def computed_stale_flag(self) -> Optional[bool]:
        """TRUE if data is more than 9 months old."""
        lag = self.computed_data_lag
        return lag > 9 if lag is not None else None

    @property
    def computed_sector_risk_modifier(self) -> Optional[float]:
        """
        sector_risk_modifier = volume_factor * trend_multiplier * spike_modifier
        trend_multiplier:  Rising=1.2, Stable=1.0, Falling=0.8
        spike_modifier:    spike_active=1.5, otherwise=1.0
        """
        vf = self.computed_volume_factor
        if vf is None:
            return None
        trend_multiplier = {'Rising': 1.2, 'Stable': 1.0, 'Falling': 0.8}.get(
            self.trend_direction, 1.0
        )
        spike_modifier = 1.5 if self.spike_active else 1.0
        return round(vf * trend_multiplier * spike_modifier, 4)

    def __repr__(self) -> str:
        return f"<I2 {self.ico_sector} | risk={self.sector_risk_modifier} | stale={self.stale_flag}>"


print("✓ I2VolumeScores defined")


#Create all tables

Base.metadata.create_all(engine, checkfirst=True)
print("✓ Tables created: i1_volume_statistics, i2_volume_scores")


#Demo data

def load_demo_data():
    with Session(engine) as session:

        if session.query(I1VolumeStatistics).first() is not None:
            print("Demo data already loaded, skipping.")
            return

        i1_rows = [
            # ── Information Technology sector — 3 consecutive quarters ────
            I1VolumeStatistics(
                period_start=date(2024, 4, 1),
                period_end=date(2024, 6, 30),
                period_type="Quarterly",
                ico_sector="Information Technology",
                sector_relevance="Full",
                complaint_count=312,
                data_breach_count=47,
                complaint_resolved=True,
                complaint_resolved_pct=71.2,
                yoy_change_pct=8.3,
                qoq_change_pct=2.1,
                avg_3period=298.0,
                pct_above_avg=4.7,
                spike_flag=False,
                source_doc="ICO Quarterly Complaints Report Q1 2024/25",
                source_url="https://ico.org.uk/about-the-ico/research-and-reports/",
                manually_reviewed=True,
            ),
            I1VolumeStatistics(
                period_start=date(2024, 7, 1),
                period_end=date(2024, 9, 30),
                period_type="Quarterly",
                ico_sector="Information Technology",
                sector_relevance="Full",
                complaint_count=389,
                data_breach_count=61,
                complaint_resolved=True,
                complaint_resolved_pct=68.5,
                yoy_change_pct=14.1,
                qoq_change_pct=24.7,
                avg_3period=318.3,
                pct_above_avg=22.2,
                spike_flag=True,
                source_doc="ICO Quarterly Complaints Report Q2 2024/25",
                source_url="https://ico.org.uk/about-the-ico/research-and-reports/",
                manually_reviewed=True,
            ),
            I1VolumeStatistics(
                period_start=date(2024, 10, 1),
                period_end=date(2024, 12, 31),
                period_type="Quarterly",
                ico_sector="Information Technology",
                sector_relevance="Full",
                complaint_count=401,
                data_breach_count=74,
                complaint_resolved=True,
                complaint_resolved_pct=66.0,
                yoy_change_pct=17.3,
                qoq_change_pct=3.1,
                avg_3period=367.3,
                pct_above_avg=9.2,
                spike_flag=False,
                source_doc="ICO Quarterly Complaints Report Q3 2024/25",
                source_url="https://ico.org.uk/about-the-ico/research-and-reports/",
                manually_reviewed=False,
            ),
            # ── Finance, Insurance and Credit sector ──────────────────────
            I1VolumeStatistics(
                period_start=date(2024, 7, 1),
                period_end=date(2024, 9, 30),
                period_type="Quarterly",
                ico_sector="Finance, Insurance and Credit",
                sector_relevance="Partial",
                complaint_count=521,
                data_breach_count=38,
                complaint_resolved=True,
                complaint_resolved_pct=74.1,
                yoy_change_pct=3.2,
                qoq_change_pct=1.4,
                avg_3period=509.0,
                pct_above_avg=2.4,
                spike_flag=False,
                source_doc="ICO Quarterly Complaints Report Q2 2024/25",
                source_url="https://ico.org.uk/about-the-ico/research-and-reports/",
                manually_reviewed=True,
            ),
            # ── Annual row ────────────────────────────────────────────────
            I1VolumeStatistics(
                period_start=date(2023, 4, 1),
                period_end=date(2024, 3, 31),
                period_type="Annual",
                ico_sector="Information Technology",
                sector_relevance="Full",
                complaint_count=1189,
                data_breach_count=171,
                complaint_resolved=True,
                complaint_resolved_pct=70.3,
                yoy_change_pct=11.2,
                qoq_change_pct=None,
                avg_3period=1089.0,
                pct_above_avg=9.2,
                spike_flag=False,
                source_doc="ICO Annual Report 2023/24",
                source_url="https://ico.org.uk/about-the-ico/research-and-reports/",
                manually_reviewed=True,
            ),
        ]

        session.add_all(i1_rows)
        session.flush()

        i2_rows = [
            I2VolumeScores(
                ico_sector="Information Technology",
                ref_period_start=date(2024, 10, 1),
                ref_period_end=date(2024, 12, 31),
                complaint_count_used=401,
                avg_3period_used=367.3,
                volume_factor=round(401 / 367.3, 4),
                trend_direction="Rising",
                spike_active=False,
                sector_risk_modifier=round((401 / 367.3) * 1.2 * 1.0, 4),
                data_lag=3,
                stale_flag=False,
                computed_at=datetime.now(timezone.utc),
            ),
            I2VolumeScores(
                ico_sector="Finance, Insurance and Credit",
                ref_period_start=date(2024, 7, 1),
                ref_period_end=date(2024, 9, 30),
                complaint_count_used=521,
                avg_3period_used=509.0,
                volume_factor=round(521 / 509.0, 4),
                trend_direction="Stable",
                spike_active=False,
                sector_risk_modifier=round((521 / 509.0) * 1.0 * 1.0, 4),
                data_lag=6,
                stale_flag=False,
                computed_at=datetime.now(timezone.utc),
            ),
        ]

        session.add_all(i2_rows)
        session.commit()
        print(f"✓ Inserted {len(i1_rows)} I1 rows and {len(i2_rows)} I2 rows")

#Load demo data
load_demo_data()


# DataFrame helpers

def get_i1_dataframe() -> pd.DataFrame:
    """Return full I1 table with computed columns added."""
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT * FROM i1_volume_statistics ORDER BY period_start DESC"),
            conn
        )
    for col in ["period_start", "period_end"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    df["spike_flag_check"] = df.apply(
        lambda r: r["complaint_count"] > 1.5 * r["avg_3period"]
        if pd.notnull(r["avg_3period"]) and r["avg_3period"] > 0
        else None,
        axis=1
    )
    df["pct_above_avg_check"] = df.apply(
        lambda r: round((r["complaint_count"] / r["avg_3period"] - 1) * 100, 2)
        if pd.notnull(r["avg_3period"]) and r["avg_3period"] > 0
        else None,
        axis=1
    )
    return df


def get_i2_dataframe() -> pd.DataFrame:
    """Return full I2 table with computed columns added."""
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT * FROM i2_volume_scores ORDER BY computed_at DESC"),
            conn
        )
    for col in ["ref_period_start", "ref_period_end"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    today = date.today()
    df["data_lag_check"] = df["ref_period_end"].apply(
        lambda d: (today.year - d.year) * 12 + (today.month - d.month)
        if pd.notnull(d) else None
    )
    df["stale_flag_check"] = df["data_lag_check"].apply(
        lambda d: d > 9 if pd.notnull(d) else None
    )
    return df


def get_sector_trend_dataframe() -> pd.DataFrame:
    """Complaint counts by sector and period for trend analysis."""
    with engine.connect() as conn:
        df = pd.read_sql(text("""
            SELECT
                ico_sector,
                period_type,
                period_start,
                period_end,
                complaint_count,
                yoy_change_pct,
                avg_3period,
                spike_flag,
                sector_relevance
            FROM i1_volume_statistics
            ORDER BY ico_sector, period_start
        """), conn)
    return df


# Display demo data

i1_df = get_i1_dataframe()
print("\n── I1: Volume Statistics ──────────────────────────────────────")
print(i1_df[[
    "ico_sector", "period_type", "period_start", "period_end",
    "complaint_count", "avg_3period", "pct_above_avg",
    "spike_flag", "yoy_change_pct"
]].to_string(index=False))

i2_df = get_i2_dataframe()
print("\n── I2: Volume Scores ──────────────────────────────────────────")
print(i2_df[[
    "ico_sector", "ref_period_start", "ref_period_end",
    "volume_factor", "trend_direction", "spike_active",
    "sector_risk_modifier", "data_lag", "stale_flag"
]].to_string(index=False))

print("\n── Sector Trend View ──────────────────────────────────────────")
trend_df = get_sector_trend_dataframe()
print(trend_df.to_string(index=False))
