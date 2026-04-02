## Creates four judicial tables
# Requirements pip install sqlalchemy psycopg2-binary pandas

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
    Integer, Numeric, String, Text, create_engine, text
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

## J1: UK Supreme Court
#Each row is one case/decision of the UK Supreme Court
#Source: UK Supreme Court Website

class J1SupremeCourt(Base):
    __tablename__ = "j1_supreme_court"

    __table_args__ = (
        CheckConstraint(
            """appellant_type IN (
                'Data Subject', 'Controller', 'Processor',
                'Regulator', 'Government'
            )""",
            name="ck_j1_appellant_type"
        ),
        CheckConstraint(
            """respondent_type IN (
                'Data Subject', 'Controller', 'Processor',
                'Regulator', 'Government'
            )""",
            name="ck_j1_respondent_type"
        ),
        CheckConstraint(
            """ico_role IN (
                'Party (Appellant)', 'Party (Respondent)',
                'Intervener', 'Amicus', 'None'
            )""",
            name="ck_j1_ico_role"
        ),
        CheckConstraint(
            """outcome_direction IN (
                'Controller', 'Data Subject', 'ICO',
                'Mixed', 'Procedural'
            )""",
            name="ck_j1_outcome_direction"
        ),
        CheckConstraint(
            """precedent_weight IN (
                'Binding', 'Highly Persuasive', 'Persuasive'
            )""",
            name="ck_j1_precedent_weight"
        ),
        CheckConstraint(
            "enforcement_signal BETWEEN 0 AND 1",
            name="ck_j1_enforcement_signal"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_j1_nlp_confidence"
        ),
    )

    # Primary key
    supreme_id                  = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Case identity
    case_name                   = Column(String(500), nullable=False)
    neutral_citation            = Column(String(100), unique=True)
    decision_date               = Column(Date, nullable=False, index=True)

    # Subject matter
    subject_matter              = Column(String(200))                    # e.g. Data protection, privacy, AI liability

    # Parties
    appellant                   = Column(String(300))
    respondent                  = Column(String(300))
    appellant_type              = Column(String(50), index=True)
    respondent_type             = Column(String(50), index=True)

    # ICO involvement
    ico_role                    = Column(String(30), index=True)
    ico_position_upheld         = Column(Boolean)                        # Nullable if ICO not involved

    # Outcome
    outcome_direction           = Column(String(20), index=True)
    outcome_summary             = Column(Text)
    precedent_weight            = Column(String(30), nullable=False)

    # Routing
    processing_activities       = Column(String(500))
    gdpr_articles               = Column(String(500))
    gdpr_principles             = Column(String(500))

    # Damages
    damages_awarded             = Column(Boolean, default=False)
    damages_amount              = Column(Numeric(15, 2))

    # Flags
    ai_specific                 = Column(Boolean, default=False, index=True)
    widens_controller_liability = Column(Boolean, default=False, index=True)
    restricts_ico_powers        = Column(Boolean, default=False, index=True)

    # Signal
    enforcement_signal          = Column(Float)

    # Provenance
    case_url                    = Column(Text)
    ingested_at                 = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence              = Column(Float)
    manually_reviewed           = Column(Boolean, default=False, index=True)

    # Computed properties
    @property
    def is_ico_win(self) -> bool:
        """TRUE if outcome favoured the ICO."""
        return self.outcome_direction == "ICO" or self.ico_position_upheld is True

    @property
    def days_since_decision(self) -> int:
        """Days since the decision was handed down."""
        return (date.today() - self.decision_date).days

    @property
    def damages_amount_thousands(self) -> Optional[float]:
        """Damages expressed in £k for display."""
        if self.damages_amount:
            return round(float(self.damages_amount) / 1_000, 1)
        return None

    def __repr__(self) -> str:
        return f"<J1 {self.case_name} | {self.decision_date} | {self.outcome_direction}>"

print("✓ J1SupremeCourt defined")


## J2: Court of Appeal
#One row per case
#Source: National Archives

class J2CourtOfAppeal(Base):
    __tablename__ = "j2_court_of_appeal"

    __table_args__ = (
        CheckConstraint(
            "division IN ('Civil', 'Criminal')",
            name="ck_j2_division"
        ),
        CheckConstraint(
            """appellant_type IN (
                'Data Subject', 'Controller', 'Processor',
                'Regulator', 'Government'
            )""",
            name="ck_j2_appellant_type"
        ),
        CheckConstraint(
            """respondent_type IN (
                'Data Subject', 'Controller', 'Processor',
                'Regulator', 'Government'
            )""",
            name="ck_j2_respondent_type"
        ),
        CheckConstraint(
            """ico_role IN (
                'Party (Appellant)', 'Party (Respondent)',
                'Intervener', 'Amicus', 'None'
            )""",
            name="ck_j2_ico_role"
        ),
        CheckConstraint(
            """outcome_direction IN (
                'Controller', 'Data Subject', 'ICO',
                'Mixed', 'Procedural'
            )""",
            name="ck_j2_outcome_direction"
        ),
        CheckConstraint(
            """precedent_weight IN (
                'Binding', 'Highly Persuasive', 'Persuasive'
            )""",
            name="ck_j2_precedent_weight"
        ),
        CheckConstraint(
            "enforcement_signal BETWEEN 0 AND 1",
            name="ck_j2_enforcement_signal"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_j2_nlp_confidence"
        ),
    )

    # Primary key
    appeal_id                   = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Case identity
    case_name                   = Column(String(500), nullable=False)
    neutral_citation            = Column(String(100), unique=True)
    decision_date               = Column(Date, nullable=False, index=True)
    division                    = Column(String(20), nullable=False)
    subject_matter              = Column(String(200))

    # Parties
    appellant_type              = Column(String(50), index=True)
    respondent_type             = Column(String(50), index=True)

    # ICO involvement
    ico_role                    = Column(String(30), index=True)
    ico_position_upheld         = Column(Boolean)

    # Outcome
    outcome_direction           = Column(String(20), index=True)
    outcome_summary             = Column(Text)
    precedent_weight            = Column(String(30), nullable=False)

    # Routing
    processing_activities       = Column(String(500))
    gdpr_articles               = Column(String(500))
    gdpr_principles             = Column(String(500))

    # Damages
    damages_awarded             = Column(Boolean, default=False)
    damages_amount              = Column(Numeric(15, 2))

    # Flags
    ai_specific                 = Column(Boolean, default=False, index=True)
    widens_controller_liability = Column(Boolean, default=False, index=True)
    restricts_ico_powers        = Column(Boolean, default=False, index=True)

    # Signal
    enforcement_signal          = Column(Float)

    # Provenance
    case_url                    = Column(Text)
    ingested_at                 = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence              = Column(Float)
    manually_reviewed           = Column(Boolean, default=False, index=True)

    @property
    def is_ico_win(self) -> bool:
        return self.outcome_direction == "ICO" or self.ico_position_upheld is True

    @property
    def days_since_decision(self) -> int:
        return (date.today() - self.decision_date).days

    def __repr__(self) -> str:
        return f"<J2 {self.case_name} | {self.decision_date} | {self.outcome_direction}>"

print("✓ J2CourtOfAppeal defined")


## J3: Information Rights Tribunal
#One row per case, most important court given highest volume of directly relevant cases
#Source: National Archives

class J3InformationRightsTribunal(Base):
    __tablename__ = "j3_information_rights_tribunal"

    __table_args__ = (
        CheckConstraint(
            "tier IN ('First-tier', 'Upper Tribunal')",
            name="ck_j3_tier"
        ),
        CheckConstraint(
            """case_type IN (
                'Enforcement Notice Appeal',
                'Monetary Penalty Appeal',
                'Information Notice Appeal',
                'Data Subject Rights Appeal'
            )""",
            name="ck_j3_case_type"
        ),
        CheckConstraint(
            """appellant_type IN (
                'Controller', 'Processor', 'Data Subject', 'ICO'
            )""",
            name="ck_j3_appellant_type"
        ),
        CheckConstraint(
            """ico_role IN (
                'Respondent', 'Appellant', 'None'
            )""",
            name="ck_j3_ico_role"
        ),
        CheckConstraint(
            """outcome_direction IN (
                'Controller', 'Data Subject', 'ICO',
                'Mixed', 'Procedural'
            )""",
            name="ck_j3_outcome_direction"
        ),
        CheckConstraint(
            """precedent_weight IN (
                'Binding', 'Highly Persuasive', 'Persuasive'
            )""",
            name="ck_j3_precedent_weight"
        ),
        CheckConstraint(
            "enforcement_signal BETWEEN 0 AND 1",
            name="ck_j3_enforcement_signal"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_j3_nlp_confidence"
        ),
    )

    # Primary key
    tribunal_id                 = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Case identity
    case_reference              = Column(String(100), nullable=False, unique=True)
    tier                        = Column(String(20), nullable=False, index=True)
    decision_date               = Column(Date, nullable=False, index=True)
    case_type                   = Column(String(50), nullable=False, index=True)

    # Parties
    appellant_type              = Column(String(50), index=True)
    ico_role                    = Column(String(20), index=True)
    ico_position_upheld         = Column(Boolean)

    # Outcome
    outcome_direction           = Column(String(20), index=True)

    # Penalty fields (for penalty appeals)
    original_penalty_gbp        = Column(Numeric(15, 2))                 # Original ICO penalty under appeal
    revised_penalty_gbp         = Column(Numeric(15, 2))                 # Revised penalty after tribunal
    penalty_reduction_pct       = Column(Float)                          # Computed: % reduction in penalty

    # Grounds
    appeals_ground              = Column(String(500))

    # Routing
    processing_activities       = Column(String(500))
    gdpr_articles               = Column(String(500))

    # Flags
    ai_specific                 = Column(Boolean, default=False, index=True)
    precedent_weight            = Column(String(30))

    # Signal
    enforcement_signal          = Column(Float)

    # Provenance
    case_url                    = Column(Text)
    ingested_at                 = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence              = Column(Float)
    manually_reviewed           = Column(Boolean, default=False, index=True)

    # Computed properties
    @property
    def computed_penalty_reduction_pct(self) -> Optional[float]:
        """Percentage reduction in penalty from original to revised."""
        if self.original_penalty_gbp and self.revised_penalty_gbp:
            orig = float(self.original_penalty_gbp)
            revised = float(self.revised_penalty_gbp)
            if orig > 0:
                return round((orig - revised) / orig * 100, 2)
        return None

    @property
    def is_ico_win(self) -> bool:
        """ICO wins if its position is upheld or outcome favours ICO."""
        return self.outcome_direction == "ICO" or self.ico_position_upheld is True

    @property
    def penalty_reduced(self) -> bool:
        """TRUE if tribunal reduced the ICO's penalty."""
        if self.original_penalty_gbp and self.revised_penalty_gbp:
            return float(self.revised_penalty_gbp) < float(self.original_penalty_gbp)
        return False

    def __repr__(self) -> str:
        return f"<J3 {self.case_reference} | {self.case_type} | {self.outcome_direction}>"

print("✓ J3InformationRightsTribunal defined")


## J4: High Court
#One row per case
#Source: National Archives

class J4HighCourt(Base):
    __tablename__ = "j4_high_court"

    __table_args__ = (
        CheckConstraint(
            "division IN ('King''s Bench', 'Chancery', 'Family')",
            name="ck_j4_division"
        ),
        CheckConstraint(
            """case_type IN (
                'Judicial Review', 'Civil Damages Claim',
                'Injunction', 'Declaration'
            )""",
            name="ck_j4_case_type"
        ),
        CheckConstraint(
            """ico_role IN (
                'Defendant', 'Party', 'Intervener', 'None'
            )""",
            name="ck_j4_ico_role"
        ),
        CheckConstraint(
            """outcome_direction IN (
                'Controller', 'Data Subject', 'ICO',
                'Mixed', 'Procedural'
            )""",
            name="ck_j4_outcome_direction"
        ),
        CheckConstraint(
            """precedent_weight IN (
                'Binding', 'Highly Persuasive', 'Persuasive'
            )""",
            name="ck_j4_precedent_weight"
        ),
        CheckConstraint(
            "enforcement_signal BETWEEN 0 AND 1",
            name="ck_j4_enforcement_signal"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_j4_nlp_confidence"
        ),
    )

    # Primary key
    highcourt_id                = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Case identity
    case_name                   = Column(String(500), nullable=False)
    neutral_citation            = Column(String(100), unique=True)
    decision_date               = Column(Date, nullable=False, index=True)
    division                    = Column(String(30), nullable=False)
    case_type                   = Column(String(50), nullable=False, index=True)

    # ICO involvement
    ico_role                    = Column(String(20), index=True)
    ico_position_upheld         = Column(Boolean)
    jr_permission_granted       = Column(Boolean)                        # Was JR permission granted?

    # Outcome
    outcome_direction           = Column(String(20), index=True)
    outcome_summary             = Column(Text)
    precedent_weight            = Column(String(30), nullable=False)

    # Routing
    processing_activities       = Column(String(500))
    gdpr_articles               = Column(String(500))
    gdpr_principles             = Column(String(500))

    # Damages
    damages_awarded             = Column(Boolean, default=False)
    damages_amount              = Column(Numeric(15, 2))

    # Flags
    ai_specific                 = Column(Boolean, default=False, index=True)
    widens_controller_liability = Column(Boolean, default=False, index=True)
    restricts_ico_powers        = Column(Boolean, default=False, index=True)

    # Signal
    enforcement_signal          = Column(Float)

    # Provenance
    case_url                    = Column(Text)
    ingested_at                 = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence              = Column(Float)
    manually_reviewed           = Column(Boolean, default=False, index=True)

    @property
    def is_ico_win(self) -> bool:
        return self.outcome_direction == "ICO" or self.ico_position_upheld is True

    @property
    def damages_amount_thousands(self) -> Optional[float]:
        if self.damages_amount:
            return round(float(self.damages_amount) / 1_000, 1)
        return None

    def __repr__(self) -> str:
        return f"<J4 {self.case_name} | {self.division} | {self.outcome_direction}>"

print("✓ J4HighCourt defined")


#Create all tables

Base.metadata.create_all(engine, checkfirst=True)
print("✓ Tables created: j1_supreme_court, j2_court_of_appeal,")
print("                  j3_information_rights_tribunal, j4_high_court")


#Demo data
def load_demo_data():
    with Session(engine) as session:

        if session.query(J1SupremeCourt).first() is not None:
            print("Demo data already loaded, skipping.")
            return

        # J1: UK Supreme Court  
        j1_rows = [
            J1SupremeCourt(
                case_name="Experian Ltd v Information Commissioner",
                neutral_citation="[2024] UKSC 44",
                decision_date=date(2024, 11, 20),
                subject_matter="Data protection; automated decision-making; credit scoring",
                appellant="Experian Ltd",
                respondent="Information Commissioner",
                appellant_type="Controller",
                respondent_type="Regulator",
                ico_role="Party (Respondent)",
                ico_position_upheld=True,
                outcome_direction="ICO",
                outcome_summary="Supreme Court upheld the ICO's enforcement notice requiring Experian to provide meaningful information to data subjects about automated credit scoring decisions under Article 22 UK GDPR.",
                precedent_weight="Binding",
                processing_activities="Automated decision-making, profiling",
                gdpr_articles="Article 22, Article 15",
                gdpr_principles="Transparency, fairness",
                damages_awarded=False,
                damages_amount=None,
                ai_specific=True,
                widens_controller_liability=True,
                restricts_ico_powers=False,
                enforcement_signal=0.92,
                case_url="https://www.supremecourt.uk/cases/uksc-2024-0044.html",
                nlp_confidence=0.94,
                manually_reviewed=True,
            ),
        ]

        # J2: Court of Appeal
        j2_rows = [
            J2CourtOfAppeal(
                case_name="Lloyd v Google LLC",
                neutral_citation="[2024] EWCA Civ 1142",
                decision_date=date(2024, 9, 15),
                division="Civil",
                subject_matter="Data protection; representative actions; damages",
                appellant_type="Data Subject",
                respondent_type="Controller",
                ico_role="Intervener",
                ico_position_upheld=True,
                outcome_direction="Data Subject",
                outcome_summary="Court of Appeal allowed a representative action for damages under UK GDPR, clarifying that data subjects may seek compensation without proving individual damage in mass data breach cases.",
                precedent_weight="Binding",
                processing_activities="Data sharing, profiling",
                gdpr_articles="Article 82, Article 79",
                gdpr_principles="Integrity and confidentiality",
                damages_awarded=True,
                damages_amount=750,
                ai_specific=False,
                widens_controller_liability=True,
                restricts_ico_powers=False,
                enforcement_signal=0.76,
                case_url="https://www.bailii.org/ew/cases/EWCA/Civ/2024/1142.html",
                nlp_confidence=0.89,
                manually_reviewed=True,
            ),
        ]

        # J3: Information Rights Tribunal 
        j3_rows = [
            J3InformationRightsTribunal(
                case_reference="EA/2024/0187",
                tier="First-tier",
                decision_date=date(2024, 10, 8),
                case_type="Monetary Penalty Appeal",
                appellant_type="Controller",
                ico_role="Respondent",
                ico_position_upheld=True,
                outcome_direction="ICO",
                original_penalty_gbp=450_000,
                revised_penalty_gbp=450_000,
                penalty_reduction_pct=0.0,
                appeals_ground="Disproportionality; procedural irregularity",
                processing_activities="Automated decision-making, profiling",
                gdpr_articles="Article 22, Article 5(1)(a)",
                ai_specific=True,
                precedent_weight="Persuasive",
                enforcement_signal=0.85,
                case_url="https://www.nationalarchives.gov.uk/EA/2024/0187",
                nlp_confidence=0.88,
                manually_reviewed=True,
            ),
            J3InformationRightsTribunal(
                case_reference="EA/2024/0203",
                tier="First-tier",
                decision_date=date(2024, 12, 2),
                case_type="Monetary Penalty Appeal",
                appellant_type="Controller",
                ico_role="Respondent",
                ico_position_upheld=False,
                outcome_direction="Controller",
                original_penalty_gbp=1_200_000,
                revised_penalty_gbp=820_000,
                penalty_reduction_pct=round((1_200_000 - 820_000) / 1_200_000 * 100, 2),
                appeals_ground="Disproportionality; mitigating factors not adequately considered",
                processing_activities="Special category data, automated decision-making",
                gdpr_articles="Article 9, Article 83",
                ai_specific=True,
                precedent_weight="Persuasive",
                enforcement_signal=0.61,
                case_url="https://www.nationalarchives.gov.uk/EA/2024/0203",
                nlp_confidence=0.86,
                manually_reviewed=True,
            ),
        ]

        # J4: High Court 
        j4_rows = [
            J4HighCourt(
                case_name="R (Foxglove) v Secretary of State for Science",
                neutral_citation="[2025] EWHC 112 (Admin)",
                decision_date=date(2025, 1, 28),
                division="King's Bench",
                case_type="Judicial Review",
                ico_role="Intervener",
                ico_position_upheld=True,
                jr_permission_granted=True,
                outcome_direction="Data Subject",
                outcome_summary="High Court granted judicial review of the government's failure to implement algorithmic transparency requirements for public sector automated decision-making systems, finding a breach of Article 22 UK GDPR read with Article 8 ECHR.",
                precedent_weight="Binding",
                processing_activities="Automated decision-making, profiling",
                gdpr_articles="Article 22, Article 5",
                gdpr_principles="Transparency, fairness",
                damages_awarded=False,
                damages_amount=None,
                ai_specific=True,
                widens_controller_liability=True,
                restricts_ico_powers=False,
                enforcement_signal=0.88,
                case_url="https://www.bailii.org/ew/cases/EWHC/Admin/2025/112.html",
                nlp_confidence=0.91,
                manually_reviewed=True,
            ),
        ]

        session.add_all(j1_rows + j2_rows + j3_rows + j4_rows)
        session.commit()
        print(f"✓ Inserted {len(j1_rows)} J1, {len(j2_rows)} J2, "
              f"{len(j3_rows)} J3, {len(j4_rows)} J4 rows")

#Load demo data
load_demo_data()


# DataFrame helpers 

def get_j1_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM j1_supreme_court ORDER BY decision_date DESC"), conn)
    df["decision_date"] = pd.to_datetime(df["decision_date"], errors="coerce").dt.date
    df["is_ico_win"]    = df["outcome_direction"] == "ICO"
    df["days_since_decision"] = df["decision_date"].apply(
        lambda d: (date.today() - d).days if pd.notnull(d) else None
    )
    return df


def get_j2_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM j2_court_of_appeal ORDER BY decision_date DESC"), conn)
    df["decision_date"] = pd.to_datetime(df["decision_date"], errors="coerce").dt.date
    df["is_ico_win"]    = df["outcome_direction"] == "ICO"
    return df


def get_j3_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM j3_information_rights_tribunal ORDER BY decision_date DESC"), conn)
    df["decision_date"] = pd.to_datetime(df["decision_date"], errors="coerce").dt.date
    df["computed_penalty_reduction_pct"] = df.apply(
        lambda r: round((float(r["original_penalty_gbp"]) - float(r["revised_penalty_gbp"]))
                  / float(r["original_penalty_gbp"]) * 100, 2)
        if pd.notnull(r["original_penalty_gbp"]) and pd.notnull(r["revised_penalty_gbp"])
        and float(r["original_penalty_gbp"]) > 0 else None,
        axis=1
    )
    df["penalty_reduced"] = df.apply(
        lambda r: float(r["revised_penalty_gbp"]) < float(r["original_penalty_gbp"])
        if pd.notnull(r["original_penalty_gbp"]) and pd.notnull(r["revised_penalty_gbp"]) else False,
        axis=1
    )
    df["is_ico_win"] = df["outcome_direction"] == "ICO"
    return df


def get_j4_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM j4_high_court ORDER BY decision_date DESC"), conn)
    df["decision_date"] = pd.to_datetime(df["decision_date"], errors="coerce").dt.date
    df["is_ico_win"]    = df["outcome_direction"] == "ICO"
    return df


def get_judicial_summary() -> pd.DataFrame:
    """
    Cross-court summary — ICO win rate, AI-specific cases, enforcement signal.
    Feeds directly into the scoring layer and dashboard enforcement timeline.
    """
    with engine.connect() as conn:
        df = pd.read_sql(text("""
            SELECT
                'Supreme Court'              AS court,
                COUNT(*)                     AS total_cases,
                SUM(CASE WHEN outcome_direction = 'ICO'
                    OR ico_position_upheld THEN 1 ELSE 0 END) AS ico_wins,
                SUM(CASE WHEN ai_specific THEN 1 ELSE 0 END)  AS ai_cases,
                AVG(enforcement_signal)      AS avg_enforcement_signal
            FROM j1_supreme_court
            UNION ALL
            SELECT
                'Court of Appeal'            AS court,
                COUNT(*)                     AS total_cases,
                SUM(CASE WHEN outcome_direction = 'ICO'
                    OR ico_position_upheld THEN 1 ELSE 0 END) AS ico_wins,
                SUM(CASE WHEN ai_specific THEN 1 ELSE 0 END)  AS ai_cases,
                AVG(enforcement_signal)      AS avg_enforcement_signal
            FROM j2_court_of_appeal
            UNION ALL
            SELECT
                'Information Rights Tribunal' AS court,
                COUNT(*)                      AS total_cases,
                SUM(CASE WHEN outcome_direction = 'ICO'
                    OR ico_position_upheld THEN 1 ELSE 0 END)  AS ico_wins,
                SUM(CASE WHEN ai_specific THEN 1 ELSE 0 END)   AS ai_cases,
                AVG(enforcement_signal)       AS avg_enforcement_signal
            FROM j3_information_rights_tribunal
            UNION ALL
            SELECT
                'High Court'                 AS court,
                COUNT(*)                     AS total_cases,
                SUM(CASE WHEN outcome_direction = 'ICO'
                    OR ico_position_upheld THEN 1 ELSE 0 END) AS ico_wins,
                SUM(CASE WHEN ai_specific THEN 1 ELSE 0 END)  AS ai_cases,
                AVG(enforcement_signal)      AS avg_enforcement_signal
            FROM j4_high_court
            ORDER BY avg_enforcement_signal DESC
        """), conn)
    df["ico_win_rate"] = df.apply(
        lambda r: round(r["ico_wins"] / r["total_cases"] * 100, 1)
        if r["total_cases"] > 0 else None,
        axis=1
    )
    return df


def get_enforcement_timeline() -> pd.DataFrame:
    """
    All judicial decisions across all courts in date order.
    Feeds the dashboard enforcement timeline panel.
    """
    with engine.connect() as conn:
        df = pd.read_sql(text("""
            SELECT
                decision_date,
                'Supreme Court'  AS court,
                case_name,
                outcome_direction,
                ai_specific,
                enforcement_signal,
                case_url
            FROM j1_supreme_court
            UNION ALL
            SELECT
                decision_date,
                'Court of Appeal' AS court,
                case_name,
                outcome_direction,
                ai_specific,
                enforcement_signal,
                case_url
            FROM j2_court_of_appeal
            UNION ALL
            SELECT
                decision_date,
                'Information Rights Tribunal' AS court,
                case_reference   AS case_name,
                outcome_direction,
                ai_specific,
                enforcement_signal,
                case_url
            FROM j3_information_rights_tribunal
            UNION ALL
            SELECT
                decision_date,
                'High Court'     AS court,
                case_name,
                outcome_direction,
                ai_specific,
                enforcement_signal,
                case_url
            FROM j4_high_court
            ORDER BY decision_date DESC
        """), conn)
    df["decision_date"] = pd.to_datetime(df["decision_date"], errors="coerce").dt.date
    return df


# Display 

print("\n── J1: Supreme Court ───────────────────────────────────────────")
j1_df = get_j1_dataframe()
print(j1_df[[
    "case_name", "decision_date", "outcome_direction",
    "ai_specific", "widens_controller_liability",
    "enforcement_signal", "is_ico_win"
]].to_string(index=False))

print("\n── J2: Court of Appeal ─────────────────────────────────────────")
j2_df = get_j2_dataframe()
print(j2_df[[
    "case_name", "decision_date", "division",
    "outcome_direction", "ai_specific", "enforcement_signal"
]].to_string(index=False))

print("\n── J3: Information Rights Tribunal ─────────────────────────────")
j3_df = get_j3_dataframe()
print(j3_df[[
    "case_reference", "case_type", "decision_date",
    "original_penalty_gbp", "revised_penalty_gbp",
    "computed_penalty_reduction_pct", "is_ico_win"
]].to_string(index=False))

print("\n── J4: High Court ──────────────────────────────────────────────")
j4_df = get_j4_dataframe()
print(j4_df[[
    "case_name", "division", "case_type", "decision_date",
    "outcome_direction", "ai_specific", "enforcement_signal"
]].to_string(index=False))

print("\n── Judicial Summary (feeds scoring layer) ──────────────────────")
print(get_judicial_summary().to_string(index=False))

print("\n── Enforcement Timeline (feeds dashboard) ──────────────────────")
print(get_enforcement_timeline()[[
    "decision_date", "court", "case_name",
    "outcome_direction", "ai_specific", "enforcement_signal"
]].to_string(index=False))
