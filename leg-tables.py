## Creates both legislative tables
## Requirements: pip install sqlalchemy, psycopg2-binary, pandas, uuid

#Import dependencies
import sys
#!{sys.executable} -m pip install sqlalchemy psycopg2-binary pandas

## Imports
import os
import uuid
from datetime import date, datetime, timezone
from typing import Optional
import pandas as pd
from sqlalchemy import (
    Boolean, CheckConstraint, Column, Date, Float, ForeignKey,
    Integer, Numeric, String, Text, create_engine, text
)
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Session, relationship

## Connection, update password before running
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:yourpassword@localhost:5432/ers_db"  # <- update this
)
engine = create_engine(DATABASE_URL, echo=False, future=True)
print("✓ Engine created")

## Base class
class Base(DeclarativeBase): 
    pass
print("✓ Base class ready")

## L1-Bills
# One row per parliamentary event, single bill can have multiple rows as it passes through parliament
#Source: bills.parliament.uk
class L1Bill(Base):
    
    __tablename__ = "l1_bills_in_parliament"
 
    __table_args__ = (
            CheckConstraint(
                "bill_type IN ('Government','Private Members','Hybrid','Private')",
                name="ck_l1_bill_type"
            ),
            CheckConstraint(
                """event_type IN (
                    'Introduced','First Reading','Second Reading',
                    'Committee Stage','Report Stage','Third Reading',
                    'Lords Introduction','Lords Amendments',
                    'Ping Pong','Royal Assent','Withdrawal','Lapse'
                )""",
                name="ck_l1_event_type"
            ),
            CheckConstraint("house IN ('Commons','Lords','Both')", name="ck_l1_house"),
            CheckConstraint(
                "bill_status IN ('Active','Passed','Withdrawn','Lapsed')",
                name="ck_l1_bill_status"
            ),
            CheckConstraint(
                "obligation_direction IN ('Increases','Decreases','Clarifies','Mixed')",
                name="ck_l1_obligation_direction"
            ),
            CheckConstraint("relevance_score BETWEEN 0 AND 1",  name="ck_l1_relevance_score"),
            CheckConstraint("nlp_confidence BETWEEN 0 AND 1",   name="ck_l1_nlp_confidence"),
        )
 
    # Primary key — UUID auto-generated in Python (mirrors PostgreSQL gen_random_uuid())
    bill_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
 
    # Identity & linking
    parliament_bill_id      = Column(String(50),  nullable=False, index=True)
    bill_type               = Column(String(50),  nullable=False)
    bill_title              = Column(String(500), nullable=False)
    session                 = Column(String(20),  nullable=False)
    
    #Event tracking
    event_type              = Column(String(100), nullable=False)
    event_date              = Column(Date,         nullable=False, index=True)
    house                   = Column(String(10),  nullable=False)
    bill_stage_numeric      = Column(Integer,      nullable=False)

    #Status, nullable
    bill_status             = Column(String(20),  nullable=False, index=True)
    expected_commencement   = Column(Date)  

    # NLP / relevance
    processing_activities   = Column(String(500))
    relevance_score         = Column(Float,        index=True)
    relevance_tag           = Column(String(500))  # comma-separated tags
    nlp_confidence          = Column(Float)
 
    # Regulatory signal
    obligation_direction    = Column(String(20))
    affects_ico             = Column(Boolean, default=False, index=True)
 
    # Provenance
    source_url              = Column(Text)
    rss_guid                = Column(String(500), unique=True)
    ingested_at             = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    manually_reviewed       = Column(Boolean, default=False, index=True)
 
    # Relationship: one bill can spawn many SIs
    statutory_instruments   = relationship("L2StatutoryInstrument", back_populates="parent_act")
 
    # Computed properties
    @property
    def days_to_commencement(self) -> Optional[int]:
        """Days between today and expected_commencement (positive = future)."""
        if self.expected_commencement:
             return (self.expected_commencement - date.today()).days
        return None
 
    @property
    def is_high_relevance(self) -> bool:
        """Quick flag: relevance_score >= 0.7."""
        return self.relevance_score is not None and self.relevance_score >= 0.7
 
    def __repr__(self) -> str:
        return f"<L1Bill {self.parliament_bill_id} | {self.event_type} | {self.event_date}>"

print("✓ L1Bills defined")

## L2 Table
# One row per statutory instrument/commencement order, single act can have multiple SIs, each tracked seperately
#Source: bills.parliament.uk
class L2StatutoryInstrument(Base):
    __tablename__ = "l2_statutory_instruments"
 
    __table_args__ = (
        CheckConstraint(
            "si_type IN ('Commencement Order','Amendment SI','Regulatory Reform Order','Other')",
            name="ck_l2_si_type"
         ),
        CheckConstraint(
            "si_status IN ('Made','In Force','Revoked','Amended')",
            name="ck_l2_si_status"
        ),
        CheckConstraint(
            "obligation_type IN ('New Duty','Removal of Exemption','New ICO Power','Penalty Uplift','Other')",
            name="ck_l2_obligation_type"
        ),
        CheckConstraint("relevance_score BETWEEN 0 AND 1", name="ck_l2_relevance_score"),
        CheckConstraint("nlp_confidence BETWEEN 0 AND 1",  name="ck_l2_nlp_confidence"),
    )

    # Primary key
    si_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
 
    # Identity
    si_number               = Column(String(50),  nullable=False, unique=True)
    si_title                = Column(String(500), nullable=False)
    si_type                 = Column(String(100), nullable=False)
 
    # Foreign key to parent act
    parent_act_id = Column(
        String(36),
        ForeignKey("l1_bills_in_parliament.bill_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    parent_act_name         = Column(String(500))
 
    # Key dates
    made_date               = Column(Date)
    laid_date               = Column(Date)
    force_date              = Column(Date, index=True)
 
    # Scope
    provisions_commenced    = Column(Text)
    si_status               = Column(String(20), index=True)
 
    # NLP / relevance
    processing_activities   = Column(String(500))
    relevance_score         = Column(Float, index=True)
    relevance_tag           = Column(String(500))
    nlp_confidence          = Column(Float)
 
    # Regulatory signal
    obligation_type         = Column(String(100))
    affects_ico             = Column(Boolean, default=False, index=True)
 
    # Provenance
    source_url              = Column(Text)
    rss_guid                = Column(String(500), unique=True)
    ingested_at             = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    manually_reviewed       = Column(Boolean, default=False, index=True)
 
    # Relationship
    parent_act              = relationship("L1Bill", back_populates="statutory_instruments")
 
    # Computed properties 
    @property
    def days_to_force(self) -> Optional[int]:
        """
        Days between made_date and force_date.
        Mirrors the GENERATED ALWAYS column in PostgreSQL.
        """
        if self.made_date and self.force_date:
            return (self.force_date - self.made_date).days
        return None
 
    @property
    def days_until_force(self) -> Optional[int]:
        """Days from today until force_date (positive = future, negative = past)."""
        if self.force_date:
            return (self.force_date - date.today()).days
        return None
 
    @property
    def is_imminent(self) -> bool:
        """TRUE if force_date is within the next 90 days."""
        d = self.days_until_force
        return d is not None and 0 <= d <= 90
 
    def __repr__(self) -> str:
        return f"<L2SI {self.si_number} | force={self.force_date} | days_to_force={self.days_to_force}>"

print("✓ L2SI defined")

## Create all tables
Base.metadata.create_all(engine, checkfirst=True)
print("✓ Tables created: l1_bills, l2_si,")

def load_demo_data():
    with Session(engine) as session:
        
        if session.query(L1Bill).first() is not None:
            print("Demo data already loaded, skipping.")
            return

        dua_bill_id = str(uuid.uuid4())

        l1_rows = [
            L1Bill(
                bill_id=dua_bill_id,
                parliament_bill_id="1234",
                bill_type="Government",
                bill_title="Data (Use and Access) Bill",
                session="2024-2025",
                event_type="Introduced",
                event_date=date(2024, 10, 23),
                house="Commons",
                bill_stage_numeric=1,
                bill_status="Active",
                expected_commencement=date(2025, 10, 1),
                processing_activities="Automated decision-making, profiling, data sharing",
                relevance_score=0.95,
                relevance_tag="automated_decision_making,profiling,data_sharing,ico_powers",
                nlp_confidence=0.87,
                obligation_direction="Increases",
                affects_ico=True,
                source_url="https://bills.parliament.uk/bills/3825",
                rss_guid="bills.parliament.uk/bills/3825/event/introduced",
                manually_reviewed=True,
            ),
            L1Bill(
                parliament_bill_id="1234",
                bill_type="Government",
                bill_title="Data (Use and Access) Bill",
                session="2024-2025",
                event_type="Second Reading",
                event_date=date(2024, 11, 12),
                house="Commons",
                bill_stage_numeric=3,
                bill_status="Active",
                expected_commencement=date(2025, 10, 1),
                processing_activities="Automated decision-making, profiling, data sharing",
                relevance_score=0.95,
                relevance_tag="automated_decision_making,profiling,data_sharing,ico_powers",
                nlp_confidence=0.87,
                obligation_direction="Increases",
                affects_ico=True,
                source_url="https://bills.parliament.uk/bills/3825/stages/second-reading",
                rss_guid="bills.parliament.uk/bills/3825/event/second-reading",
                manually_reviewed=True,
            ),
            L1Bill(
                parliament_bill_id="1234",
                bill_type="Government",
                bill_title="Data (Use and Access) Bill",
                session="2024-2025",
                event_type="Committee Stage",
                event_date=date(2025, 1, 14),
                house="Commons",
                bill_stage_numeric=4,
                bill_status="Active",
                expected_commencement=date(2025, 10, 1),
                processing_activities="Automated decision-making, profiling, data sharing",
                relevance_score=0.95,
                relevance_tag="automated_decision_making,profiling,data_sharing,ico_powers",
                nlp_confidence=0.82,
                obligation_direction="Increases",
                affects_ico=True,
                source_url="https://bills.parliament.uk/bills/3825/stages/committee-stage",
                rss_guid="bills.parliament.uk/bills/3825/event/committee-stage",
                manually_reviewed=False,
            ),
            L1Bill(
                parliament_bill_id="2201",
                bill_type="Private Members",
                bill_title="Artificial Intelligence (Regulation) Bill",
                session="2024-2025",
                event_type="First Reading",
                event_date=date(2024, 9, 4),
                house="Lords",
                bill_stage_numeric=2,
                bill_status="Active",
                processing_activities="AI model training, automated decision-making",
                relevance_score=0.72,
                relevance_tag="ai_regulation,automated_decision_making",
                nlp_confidence=0.68,
                obligation_direction="Clarifies",
                affects_ico=False,
                source_url="https://bills.parliament.uk/bills/3734",
                rss_guid="bills.parliament.uk/bills/3734/event/first-reading",
                manually_reviewed=False,
            ),
        ]
        l2_rows = [
            L2StatutoryInstrument(
                si_number="SI 2025/412",
                si_title="Data (Use and Access) Act 2025 (Commencement No. 1) Order 2025",
                si_type="Commencement Order",
                parent_act_id=dua_bill_id,
                parent_act_name="Data (Use and Access) Act 2025",
                made_date=date(2025, 6, 1),
                laid_date=date(2025, 5, 20),
                force_date=date(2025, 10, 1),
                provisions_commenced="Sections 1-15, 22, Schedule 1",
                si_status="Made",
                processing_activities="Automated decision-making, data sharing",
                relevance_score=0.93,
                relevance_tag="commencement,automated_decision_making",
                nlp_confidence=0.90,
                obligation_type="New Duty",
                affects_ico=True,
                source_url="https://www.legislation.gov.uk/uksi/2025/412/contents",
                rss_guid="legislation.gov.uk/uksi/2025/412",
                manually_reviewed=True,
            ),
            L2StatutoryInstrument(
                si_number="SI 2025/618",
                si_title="Data (Use and Access) Act 2025 (Commencement No. 2 and Transitional Provisions) Order 2025",
                si_type="Commencement Order",
                parent_act_id=dua_bill_id,
                parent_act_name="Data (Use and Access) Act 2025",
                made_date=date(2025, 9, 15),
                laid_date=date(2025, 9, 5),
                force_date=date(2026, 1, 1),
                provisions_commenced="Sections 16-21, 23-30, Schedules 2-4",
                si_status="Made",
                processing_activities="Profiling, data sharing, ICO enforcement powers",
                relevance_score=0.91,
                relevance_tag="commencement,profiling,ico_powers",
                nlp_confidence=0.88,
                obligation_type="New ICO Power",
                affects_ico=True,
                source_url="https://www.legislation.gov.uk/uksi/2025/618/contents",
                rss_guid="legislation.gov.uk/uksi/2025/618",
                manually_reviewed=False,
            ),
        ]

        session.add_all(l1_rows + l2_rows)
        session.commit()
        print(f"✓ Inserted {len(l1_rows)} L1 rows and {len(l2_rows)} L2 rows")


#Load demo data
load_demo_data()

#Dataframe helpers
def get_l1_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT * FROM l1_bills_in_parliament ORDER BY event_date DESC"),
            conn
        )
    today = date.today()
    df["expected_commencement"] = pd.to_datetime(df["expected_commencement"], errors="coerce").dt.date  # fix: convert string -> date
    df["days_to_commencement"] = df["expected_commencement"].apply(
        lambda d: (d - today).days if pd.notnull(d) else None
    )
    df["is_high_relevance"] = df["relevance_score"].apply(
        lambda s: s >= 0.7 if pd.notnull(s) else False
    )
    return df

def get_l2_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT * FROM l2_statutory_instruments ORDER BY force_date ASC"),
            conn
        )
    today = date.today()

    for col in ["made_date", "laid_date", "force_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    df["days_to_force"] = df.apply(
        lambda r: (r["force_date"] - r["made_date"]).days
        if pd.notnull(r["force_date"]) and pd.notnull(r["made_date"])
        else None,
        axis=1
    )
    df["days_until_force"] = df["force_date"].apply(
        lambda d: (d - today).days if pd.notnull(d) else None
    )
    df["is_imminent"] = df["days_until_force"].apply(
        lambda d: 0 <= d <= 90 if pd.notnull(d) else False
    )
    return df

#Display demo data

print("── L1 Bills ──────────────────────────────────────────")
l1_df = get_l1_dataframe()
print(l1_df[["parliament_bill_id", "bill_title", "event_type", 
             "event_date", "relevance_score", "days_to_commencement"]].to_string(index=False))

print("\n── L2 Statutory Instruments ──────────────────────────")
l2_df = get_l2_dataframe()
print(l2_df[["si_number", "si_type", "force_date", 
             "days_to_force", "days_until_force", "is_imminent"]].to_string(index=False))
