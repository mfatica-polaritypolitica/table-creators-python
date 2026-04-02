## Creates all six regulatory tables
## Requirements: pip install sqlalchemy psycopg-binary pandas
## Install dependencies
import sys
# !{sys.executable} -m pip install sqlalchemy psycopg2-binary pandas

## Imports
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


## R1: ICO Enforcement Register
# Each row is one enforcement action or rgulatory outcome
#Source: ICO website enforcement register 

class R1EnforcementRegister(Base):
    __tablename__ = "r1_enforcement_register"

    __table_args__ = (
        CheckConstraint(
            "org_size IN ('Micro', 'Small', 'Medium', 'Large')",
            name="ck_r1_org_size"
        ),
        CheckConstraint(
            """action_type IN (
                'Monetary Penalty Notice',
                'Enforcement Notice',
                'Information Notice',
                'Assessment Notice',
                'Undertaking',
                'Reprimand',
                'Warning',
                'Prosecution',
                'Stop Processing Order',
                'Advisory Visit'
            )""",
            name="ck_r1_action_type"
        ),
        CheckConstraint(
            "outcome IN ('Upheld', 'Overturned on Appeal', 'Settled', 'Withdrawn')",
            name="ck_r1_outcome"
        ),
        CheckConstraint(
            "severity_tier IN ('Critical', 'High', 'Medium', 'Low', 'Advisory')",
            name="ck_r1_severity_tier"
        ),
        CheckConstraint(
            "penalty_as_max BETWEEN 0 AND 1",
            name="ck_r1_penalty_as_max"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_r1_nlp_confidence"
        ),
    )

    # Primary key
    enforcement_id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # ICO reference
    ico_reference           = Column(String(100), unique=True)

    # Organisation
    org_name                = Column(String(500), nullable=False)
    org_type                = Column(String(100), nullable=False)
    org_size                = Column(String(10))

    # Action
    action_date             = Column(Date, nullable=False, index=True)
    action_type             = Column(String(100), nullable=False, index=True)
    outcome                 = Column(String(30))

    # Penalty
    penalty_gbp             = Column(Numeric(15, 2))
    penalty_as_max          = Column(Float)                              # Computed: penalty / max possible fine
    severity_tier           = Column(String(20), index=True)

    # Factors
    aggravating_factors     = Column(String(500))
    mitigating_factors      = Column(String(500))

    # Appeal
    appealed                = Column(Boolean, default=False)
    appeal_outcome          = Column(String(20))                         # Nullable if not appealed

    # Routing
    processing_activities   = Column(String(500))
    legislation_breached    = Column(String(500))
    gdpr_principles         = Column(String(500))

    # Flags
    special_category_data   = Column(Boolean, default=False)
    cross_border            = Column(Boolean, default=False)
    ai_specific             = Column(Boolean, default=False, index=True)

    # Prior contact history
    prior_ico_contact       = Column(Boolean, default=False)
    prior_contact_types     = Column(String(500))
    prior_contact_count     = Column(Integer)
    days_prior_contact      = Column(Integer)                            # Computed: days since most recent prior contact

    # Recidivism
    org_type_recidivism_rate = Column(Float)                             # Computed: historical enforcement rate for org_type

    # NLP
    enforcement_signal      = Column(Float)
    nlp_confidence          = Column(Float)

    # Provenance
    source_url              = Column(Text)
    raw_summary             = Column(Text)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    manually_reviewed       = Column(Boolean, default=False, index=True)

    @property
    def computed_penalty_as_max(self) -> Optional[float]:
        """
        Penalty as % of maximum possible fine.
        Max fine under UK GDPR: higher of £17.5m or 4% global annual turnover.
        Uses £17.5m as the standard denominator for comparability.
        """
        if self.penalty_gbp:
            return round(float(self.penalty_gbp) / 17_500_000, 4)
        return None

    @property
    def is_high_severity(self) -> bool:
        return self.severity_tier in ('Critical', 'High')

    @property
    def penalty_gbp_millions(self) -> Optional[float]:
        if self.penalty_gbp:
            return round(float(self.penalty_gbp) / 1_000_000, 3)
        return None

    def __repr__(self) -> str:
        return f"<R1 {self.org_name} | {self.action_type} | £{self.penalty_gbp}>"

print("✓ R1EnforcementRegister defined")


##R2: ICO News and Blod
#Each row is one news item pr blog post from the ICO
#Source: ICO website

class R2IcoNews(Base):
    __tablename__ = "r2_ico_news"

    __table_args__ = (
        CheckConstraint(
            """content_type IN (
                'News', 'Blog', 'Press Release',
                'Statement', 'Investigation Announcement'
            )""",
            name="ck_r2_content_type"
        ),
        CheckConstraint("topic_relevance_score BETWEEN 0 AND 1", name="ck_r2_relevance"),
        CheckConstraint("enforcement_signal BETWEEN 0 AND 1",    name="ck_r2_enforcement_signal"),
        CheckConstraint("nlp_confidence BETWEEN 0 AND 1",        name="ck_r2_nlp_confidence"),
    )

    news_id                 = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title                   = Column(String(500), nullable=False)
    publication_date        = Column(Date, nullable=False, index=True)
    content_type            = Column(String(50), nullable=False)
    processing_activities   = Column(String(500))
    topic_tags              = Column(String(500))
    topic_relevance_score   = Column(Float, index=True)
    signal_investigation    = Column(Boolean, default=False)
    signal_consultation     = Column(Boolean, default=False)
    enforcement_signal      = Column(Float)
    source_url              = Column(Text)
    rss_guid                = Column(String(500), unique=True)
    raw_text                = Column(Text)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence          = Column(Float)
    manually_reviewed       = Column(Boolean, default=False, index=True)

    def __repr__(self) -> str:
        return f"<R2 {self.content_type} | {self.publication_date} | {self.title[:60]}>"

print("✓ R2IcoNews defined")


## R3: ICO Consultations and Guidance
#Each row is one document/step in a consultation
#Source: ICO website

class R3IcoConsultations(Base):
    __tablename__ = "r3_ico_consultations"

    __table_args__ = (
        CheckConstraint(
            """document_type IN (
                'Consultation', 'Guidance', 'Audit Framework',
                'Call for Evidence', 'Opinion', 'Code of Practice'
            )""",
            name="ck_r3_document_type"
        ),
        CheckConstraint(
            "consultation_status IN ('Open', 'Closed', 'Response Published', 'Finalised')",
            name="ck_r3_consultation_status"
        ),
        CheckConstraint(
            "obligation_direction IN ('Tightens', 'Relaxes', 'Clarifies', 'Mixed')",
            name="ck_r3_obligation_direction"
        ),
        CheckConstraint("topic_relevance_score BETWEEN 0 AND 1", name="ck_r3_relevance"),
        CheckConstraint("enforcement_signal BETWEEN 0 AND 1",    name="ck_r3_enforcement_signal"),
        CheckConstraint("nlp_confidence BETWEEN 0 AND 1",        name="ck_r3_nlp_confidence"),
    )

    consultation_id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title                   = Column(String(500), nullable=False)
    publication_date        = Column(Date, nullable=False, index=True)
    document_type           = Column(String(50), nullable=False)
    consultation_status     = Column(String(30), index=True)
    consultation_closes     = Column(Date)                               # Nullable if not open
    processing_activities   = Column(String(500))
    topic_tags              = Column(String(500))
    topic_relevance_score   = Column(Float, index=True)
    obligation_direction    = Column(String(20))
    enforcement_signal      = Column(Float)
    follows_enforcement     = Column(Boolean, default=False)
    source_url              = Column(Text)
    rss_guid                = Column(String(500), unique=True)
    raw_text                = Column(Text)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence          = Column(Float)
    manually_reviewed       = Column(Boolean, default=False, index=True)

    @property
    def days_until_closes(self) -> Optional[int]:
        if self.consultation_closes:
            return (self.consultation_closes - date.today()).days
        return None

    def __repr__(self) -> str:
        return f"<R3 {self.document_type} | {self.consultation_status} | {self.title[:60]}>"

print("✓ R3IcoConsultations defined")

##R4: Secondary Regulators
#Each row is one action from CMA, Ofcom, FCA, or AI Safety Institute
#Source: Websites of secondary regulators

class R4SecondaryRegulators(Base):
    __tablename__ = "r4_secondary_regulators"

    __table_args__ = (
        CheckConstraint(
            """regulator IN (
                'Competition and Markets Authority',
                'Ofcom',
                'Financial Conduct Authority',
                'AI Safety Institute',
                'Other'
            )""",
            name="ck_r4_regulator"
        ),
        CheckConstraint(
            "action_type IN ('Enforcement', 'Investigation', 'Guidance', 'Market Study', 'Statement')",
            name="ck_r4_action_type"
        ),
        CheckConstraint("topic_relevance_score BETWEEN 0 AND 1", name="ck_r4_relevance"),
        CheckConstraint("enforcement_signal BETWEEN 0 AND 1",    name="ck_r4_enforcement_signal"),
        CheckConstraint("nlp_confidence BETWEEN 0 AND 1",        name="ck_r4_nlp_confidence"),
    )

    secondary_id            = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    regulator               = Column(String(100), nullable=False, index=True)
    action_date             = Column(Date, nullable=False, index=True)
    action_type             = Column(String(50), nullable=False)
    org_name                = Column(String(500))
    org_type                = Column(String(100))
    topic_tags              = Column(String(500))
    processing_activities   = Column(String(500))
    topic_relevance_score   = Column(Float, index=True)
    cross_regulator_flag    = Column(Boolean, default=False)
    ico_referral            = Column(Boolean, default=False)
    enforcement_signal      = Column(Float)
    source_url              = Column(Text)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence          = Column(Float)
    manually_reviewed       = Column(Boolean, default=False, index=True)

    def __repr__(self) -> str:
        return f"<R4 {self.regulator} | {self.action_type} | {self.action_date}>"

print("✓ R4SecondaryRegulators defined")

##R5: EU/International Bodies
#Each row is one action from EDPB, Irish DPC, CNIL, German BfDI, Spanish AEPD
#Source: Websites of international regulators

class R5InternationalBodies(Base):
    __tablename__ = "r5_international_bodies"

    __table_args__ = (
        CheckConstraint(
            """action_type IN (
                'Enforcement Decision', 'Binding Opinion',
                'Guideline', 'Joint Investigation'
            )""",
            name="ck_r5_action_type"
        ),
        CheckConstraint("topic_relevance_score BETWEEN 0 AND 1", name="ck_r5_relevance"),
        CheckConstraint("ico_signal_strength BETWEEN 0 AND 1",   name="ck_r5_ico_signal"),
        CheckConstraint("nlp_confidence BETWEEN 0 AND 1",        name="ck_r5_nlp_confidence"),
    )

    international_id        = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    body                    = Column(String(200), nullable=False, index=True)
    jurisdiction            = Column(String(100), nullable=False)
    action_date             = Column(Date, nullable=False, index=True)
    action_type             = Column(String(50), nullable=False)
    org_name                = Column(String(500))
    org_type                = Column(String(100))
    penalty_eur             = Column(Numeric(15, 2))
    processing_activities   = Column(String(500))
    topic_tags              = Column(String(500))
    topic_relevance_score   = Column(Float, index=True)
    uk_company_involved     = Column(Boolean, default=False)
    gdpr_articles           = Column(String(500))
    ico_signal_strength     = Column(Float)
    source_url              = Column(Text)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence          = Column(Float)
    manually_reviewed       = Column(Boolean, default=False, index=True)

    @property
    def penalty_eur_millions(self) -> Optional[float]:
        if self.penalty_eur:
            return round(float(self.penalty_eur) / 1_000_000, 3)
        return None

    def __repr__(self) -> str:
        return f"<R5 {self.body} | {self.action_type} | €{self.penalty_eur}>"

print("✓ R5InternationalBodies defined")


##R6: DRCF
#Each row is one publication/statement from the Digital Regulation Cooperation Forum
#Source: DRCF website

class R6DRCF(Base):
    __tablename__ = "r6_drcf"

    __table_args__ = (
        CheckConstraint(
            """document_type IN (
                'Joint Statement', 'Work Programme',
                'Report', 'Consultation Response'
            )""",
            name="ck_r6_document_type"
        ),
        CheckConstraint("topic_relevance_score BETWEEN 0 AND 1", name="ck_r6_relevance"),
        CheckConstraint("enforcement_signal BETWEEN 0 AND 1",    name="ck_r6_enforcement_signal"),
        CheckConstraint("nlp_confidence BETWEEN 0 AND 1",        name="ck_r6_nlp_confidence"),
    )

    drcf_id                 = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    publication_date        = Column(Date, nullable=False, index=True)
    document_type           = Column(String(50), nullable=False)
    participating_bodies    = Column(String(500))
    title                   = Column(String(500), nullable=False)
    processing_activities   = Column(String(500))
    topic_tags              = Column(String(500))
    topic_relevance_score   = Column(Float, index=True)
    ico_lead                = Column(Boolean, default=False)
    enforcement_signal      = Column(Float)
    coordinated_action_flag = Column(Boolean, default=False)
    source_url              = Column(Text)
    raw_text                = Column(Text)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence          = Column(Float)
    manually_reviewed       = Column(Boolean, default=False, index=True)

    def __repr__(self) -> str:
        return f"<R6 DRCF | {self.document_type} | {self.publication_date} | {self.title[:60]}>"

print("✓ R6DRCF defined")


##Create all tables

Base.metadata.create_all(engine, checkfirst=True)
print("✓ Tables created: r1_enforcement_register, r2_ico_news, r3_ico_consultations,")
print("                  r4_secondary_regulators, r5_international_bodies, r6_drcf")


## Demo data

def load_demo_data():
    with Session(engine) as session:

        if session.query(R1EnforcementRegister).first() is not None:
            print("Demo data already loaded, skipping.")
            return

        r1_rows = [
            R1EnforcementRegister(
                ico_reference="ENF-2024-001",
                org_name="DataTech Solutions Ltd",
                org_type="AI Start-up",
                org_size="Small",
                action_date=date(2024, 9, 12),
                action_type="Monetary Penalty Notice",
                outcome="Upheld",
                penalty_gbp=450000,
                penalty_as_max=round(450000 / 17_500_000, 4),
                severity_tier="High",
                aggravating_factors="Repeated breach, large-scale processing, deliberate",
                mitigating_factors=None,
                appealed=False,
                appeal_outcome=None,
                processing_activities="Automated decision-making, profiling",
                legislation_breached="UK GDPR Article 22, Article 5(1)(a)",
                gdpr_principles="Lawfulness, fairness and transparency",
                special_category_data=False,
                cross_border=False,
                ai_specific=True,
                prior_ico_contact=True,
                prior_contact_types="Reprimand",
                prior_contact_count=1,
                days_prior_contact=412,
                org_type_recidivism_rate=0.18,
                enforcement_signal=0.87,
                nlp_confidence=0.91,
                source_url="https://ico.org.uk/action-weve-taken/enforcement/datatech-solutions/",
                raw_summary="ICO issued a monetary penalty notice of £450,000 to DataTech Solutions Ltd for unlawful automated decision-making in their recruitment platform.",
                manually_reviewed=True,
            ),
            R1EnforcementRegister(
                ico_reference="ENF-2024-002",
                org_name="MegaRetail Group plc",
                org_type="Large Retail",
                org_size="Large",
                action_date=date(2024, 11, 3),
                action_type="Enforcement Notice",
                outcome="Upheld",
                penalty_gbp=None,
                penalty_as_max=None,
                severity_tier="Medium",
                aggravating_factors="Large-scale processing of customer data",
                mitigating_factors="Self-reported, remediation taken",
                appealed=False,
                appeal_outcome=None,
                processing_activities="Data sharing, profiling",
                legislation_breached="UK GDPR Article 13, Article 6",
                gdpr_principles="Transparency, lawful basis",
                special_category_data=False,
                cross_border=True,
                ai_specific=False,
                prior_ico_contact=False,
                prior_contact_count=0,
                org_type_recidivism_rate=0.09,
                enforcement_signal=0.62,
                nlp_confidence=0.85,
                source_url="https://ico.org.uk/action-weve-taken/enforcement/megaretail/",
                raw_summary="ICO issued an enforcement notice requiring MegaRetail Group to update privacy notices and establish lawful basis for cross-border data transfers.",
                manually_reviewed=True,
            ),
            R1EnforcementRegister(
                ico_reference="ENF-2025-001",
                org_name="HealthAI Technologies Ltd",
                org_type="Health Tech",
                org_size="Medium",
                action_date=date(2025, 2, 18),
                action_type="Monetary Penalty Notice",
                outcome="Upheld",
                penalty_gbp=1_200_000,
                penalty_as_max=round(1_200_000 / 17_500_000, 4),
                severity_tier="Critical",
                aggravating_factors="Special category data, deliberate, repeated breach",
                mitigating_factors=None,
                appealed=True,
                appeal_outcome="Upheld",
                processing_activities="Special category data, automated decision-making",
                legislation_breached="UK GDPR Article 9, Article 22, Article 5(1)(f)",
                gdpr_principles="Integrity and confidentiality, lawfulness",
                special_category_data=True,
                cross_border=False,
                ai_specific=True,
                prior_ico_contact=True,
                prior_contact_types="Warning, Reprimand",
                prior_contact_count=2,
                days_prior_contact=198,
                org_type_recidivism_rate=0.24,
                enforcement_signal=0.95,
                nlp_confidence=0.93,
                source_url="https://ico.org.uk/action-weve-taken/enforcement/healthai/",
                raw_summary="ICO issued a £1.2m monetary penalty to HealthAI Technologies for unlawful processing of special category health data in an AI diagnostic tool.",
                manually_reviewed=True,
            ),
            R1EnforcementRegister(
                ico_reference="ENF-2025-002",
                org_name="AdNet Digital Ltd",
                org_type="AdTech",
                org_size="Small",
                action_date=date(2025, 3, 5),
                action_type="Reprimand",
                outcome="Upheld",
                penalty_gbp=None,
                penalty_as_max=None,
                severity_tier="Low",
                aggravating_factors=None,
                mitigating_factors="Self-reported, small organisation, remediation taken",
                appealed=False,
                appeal_outcome=None,
                processing_activities="Profiling, data sharing",
                legislation_breached="UK GDPR Article 6, PECR Regulation 6",
                gdpr_principles="Lawful basis",
                special_category_data=False,
                cross_border=False,
                ai_specific=False,
                prior_ico_contact=False,
                prior_contact_count=0,
                org_type_recidivism_rate=0.14,
                enforcement_signal=0.38,
                nlp_confidence=0.79,
                source_url="https://ico.org.uk/action-weve-taken/enforcement/adnet/",
                raw_summary="ICO issued a reprimand to AdNet Digital Ltd for cookie consent violations on their advertising platform.",
                manually_reviewed=False,
            ),
        ]

        session.add_all(r1_rows)
        session.flush()
        print(f"✓ Inserted {len(r1_rows)} R1 rows")

        # R2-R6 stub rows
        r2_stub = R2IcoNews(
            title="ICO opens investigation into AI recruitment tools",
            publication_date=date(2025, 1, 15),
            content_type="News",
            processing_activities="Automated decision-making, profiling",
            topic_tags="ai,recruitment,automated_decision_making",
            topic_relevance_score=0.92,
            signal_investigation=True,
            signal_consultation=False,
            enforcement_signal=0.78,
            source_url="https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2025/01/ico-ai-recruitment/",
            rss_guid="ico.org.uk/news/2025/01/ai-recruitment",
            nlp_confidence=0.88,
            manually_reviewed=True,
        )

        r3_stub = R3IcoConsultations(
            title="Guidance on AI and automated decision-making under UK GDPR",
            publication_date=date(2025, 2, 1),
            document_type="Guidance",
            consultation_status="Finalised",
            consultation_closes=None,
            processing_activities="Automated decision-making, profiling",
            topic_tags="ai,automated_decision_making,uk_gdpr",
            topic_relevance_score=0.97,
            obligation_direction="Tightens",
            enforcement_signal=0.81,
            follows_enforcement=True,
            source_url="https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/",
            rss_guid="ico.org.uk/guidance/ai-adm-2025",
            nlp_confidence=0.94,
            manually_reviewed=True,
        )

        r4_stub = R4SecondaryRegulators(
            regulator="Competition and Markets Authority",
            action_date=date(2025, 1, 20),
            action_type="Market Study",
            org_name=None,
            org_type="AI Foundation Models",
            topic_tags="ai,foundation_models,competition",
            processing_activities="AI model training, automated decision-making",
            topic_relevance_score=0.83,
            cross_regulator_flag=True,
            ico_referral=False,
            enforcement_signal=0.55,
            source_url="https://www.gov.uk/cma-cases/ai-foundation-models",
            nlp_confidence=0.82,
            manually_reviewed=True,
        )

        r5_stub = R5InternationalBodies(
            body="European Data Protection Board",
            jurisdiction="European Union",
            action_date=date(2024, 12, 10),
            action_type="Binding Opinion",
            org_name="Major Social Media Platform",
            org_type="Large Tech",
            penalty_eur=None,
            processing_activities="Profiling, data sharing, automated decision-making",
            topic_tags="profiling,consent,social_media",
            topic_relevance_score=0.76,
            uk_company_involved=True,
            gdpr_articles="Article 5, Article 6, Article 22",
            ico_signal_strength=0.65,
            source_url="https://edpb.europa.eu/our-work-tools/our-documents/",
            nlp_confidence=0.80,
            manually_reviewed=False,
        )

        r6_stub = R6DRCF(
            publication_date=date(2025, 3, 1),
            document_type="Joint Statement",
            participating_bodies="ICO, CMA, Ofcom, FCA",
            title="DRCF 2025/26 Work Programme: AI and Data Regulation",
            processing_activities="AI model training, automated decision-making, data sharing",
            topic_tags="ai,cross_regulator,work_programme",
            topic_relevance_score=0.89,
            ico_lead=True,
            enforcement_signal=0.60,
            coordinated_action_flag=True,
            source_url="https://www.drcf.org.uk/publications/",
            nlp_confidence=0.86,
            manually_reviewed=True,
        )

        session.add_all([r2_stub, r3_stub, r4_stub, r5_stub, r6_stub])
        session.commit()
        print("✓ Inserted stub rows for R2, R3, R4, R5, R6")

##Load demo data
load_demo_data()


##DataFrame Helpers

def get_r1_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT * FROM r1_enforcement_register ORDER BY action_date DESC"),
            conn
        )
    df["action_date"] = pd.to_datetime(df["action_date"], errors="coerce").dt.date
    df["penalty_as_max_check"] = df["penalty_gbp"].apply(
        lambda p: round(float(p) / 17_500_000, 4) if pd.notnull(p) else None
    )
    df["penalty_gbp_millions"] = df["penalty_gbp"].apply(
        lambda p: round(float(p) / 1_000_000, 3) if pd.notnull(p) else None
    )
    df["is_high_severity"] = df["severity_tier"].isin(["Critical", "High"])
    return df


def get_r2_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM r2_ico_news ORDER BY publication_date DESC"), conn)
    df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce").dt.date
    return df


def get_r3_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM r3_ico_consultations ORDER BY publication_date DESC"), conn)
    for col in ["publication_date", "consultation_closes"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    today = date.today()
    df["days_until_closes"] = df["consultation_closes"].apply(
        lambda d: (d - today).days if pd.notnull(d) else None
    )
    return df


def get_r4_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM r4_secondary_regulators ORDER BY action_date DESC"), conn)
    df["action_date"] = pd.to_datetime(df["action_date"], errors="coerce").dt.date
    return df


def get_r5_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM r5_international_bodies ORDER BY action_date DESC"), conn)
    df["action_date"] = pd.to_datetime(df["action_date"], errors="coerce").dt.date
    df["penalty_eur_millions"] = df["penalty_eur"].apply(
        lambda p: round(float(p) / 1_000_000, 3) if pd.notnull(p) else None
    )
    return df


def get_r6_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM r6_drcf ORDER BY publication_date DESC"), conn)
    df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce").dt.date
    return df


def get_enforcement_summary() -> pd.DataFrame:
    """Grouped summary: action counts, total penalties, avg signal by severity and AI flag."""
    with engine.connect() as conn:
        df = pd.read_sql(text("""
            SELECT
                severity_tier,
                ai_specific,
                COUNT(*)                    AS action_count,
                SUM(penalty_gbp)            AS total_penalties_gbp,
                AVG(enforcement_signal)     AS avg_enforcement_signal,
                SUM(CASE WHEN appealed THEN 1 ELSE 0 END) AS appeal_count
            FROM r1_enforcement_register
            GROUP BY severity_tier, ai_specific
            ORDER BY severity_tier, ai_specific
        """), conn)
    return df

##Display

r1_df = get_r1_dataframe()
print("\n── R1: ICO Enforcement Register ───────────────────────────────")
print(r1_df[[
    "org_name", "org_type", "action_date", "action_type",
    "severity_tier", "penalty_gbp_millions", "ai_specific",
    "enforcement_signal", "is_high_severity"
]].to_string(index=False))

print("\n── R1: Enforcement Summary ─────────────────────────────────────")
print(get_enforcement_summary().to_string(index=False))

print("\n── R2: ICO News (stub) ─────────────────────────────────────────")
print(get_r2_dataframe()[["title", "content_type", "publication_date", "enforcement_signal"]].to_string(index=False))

print("\n── R3: Consultations (stub) ────────────────────────────────────")
print(get_r3_dataframe()[["title", "document_type", "consultation_status", "obligation_direction"]].to_string(index=False))

print("\n── R4: Secondary Regulators (stub) ─────────────────────────────")
print(get_r4_dataframe()[["regulator", "action_type", "action_date", "cross_regulator_flag"]].to_string(index=False))

print("\n── R5: International Bodies (stub) ─────────────────────────────")
print(get_r5_dataframe()[["body", "jurisdiction", "action_type", "uk_company_involved", "ico_signal_strength"]].to_string(index=False))

print("\n── R6: DRCF (stub) ─────────────────────────────────────────────")
print(get_r6_dataframe()[["title", "document_type", "publication_date", "ico_lead", "coordinated_action_flag"]].to_string(index=False))
