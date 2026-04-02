## Creates two tables for media and civil society component
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


#M1: Media NGO Activity
#Each row is one press release, publications, etc. from civil society orgs
#Source: NGO websites

class M1NgoActivity(Base):
    __tablename__ = "m1_ngo_activity"

    __table_args__ = (
        CheckConstraint(
            """ngo_name IN (
                'Big Brother Watch',
                'Privacy International',
                'Open Rights Group',
                'Liberty',
                'Foxglove',
                'Connected by Data',
                'MedConfidential',
                'Ada Lovelace Institute',
                'Alan Turing Institute',
                'EDRi',
                'The Future Society',
                'AI Whistleblower Initiative',
                'European AI and Society Fund',
                'Other'
            )""",
            name="ck_m1_ngo_name"
        ),
        CheckConstraint(
            """activity_type IN (
                'Publication',
                'Press Release',
                'Formal Complaint',
                'Legal Challenge',
                'Parliamentary Submission',
                'Open Letter',
                'Report'
            )""",
            name="ck_m1_activity_type"
        ),
        CheckConstraint(
            """enforcement_stance IN (
                'Pro-enforcement', 'Neutral',
                'Deregulatory', 'Mixed'
            )""",
            name="ck_m1_enforcement_stance"
        ),
        CheckConstraint(
            "topic_relevance_score BETWEEN 0 AND 1",
            name="ck_m1_relevance"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_m1_nlp_confidence"
        ),
    )

    # Primary key
    ngo_activity_id         = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Identity
    ngo_name                = Column(String(200), nullable=False, index=True)
    publication_date        = Column(Date, nullable=False, index=True)
    activity_type           = Column(String(50), nullable=False, index=True)
    title                   = Column(Text, nullable=False)


    # Target
    target_org              = Column(String(300))                        # Company or sector named as subject

    # ICO flags
    ico_named               = Column(Boolean, default=False, index=True) # Is the ICO explicitly called on to act?
    formal_complaint        = Column(Boolean, default=False, index=True) # Is this/does this accompany a formal ICO complaint?
    complaint_ref           = Column(String(100))                        # ICO complaint reference number if applicable

    # Legal action
    legal_action            = Column(Boolean, default=False, index=True) # Is legal action threatened or initiated?

    # Content
    content_summary         = Column(Text)

    # Routing + NLP
    processing_activities   = Column(String(500))
    topic_relevance_score   = Column(Float, index=True)
    enforcement_stance      = Column(String(20), index=True)
    gdpr_articles           = Column(String(500))

    # Provenance
    source_url              = Column(Text)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence          = Column(Float)
    manually_reviewed       = Column(Boolean, default=False, index=True)

    # Computed properties
    @property
    def is_high_impact(self) -> bool:
        """
        TRUE if activity combines formal complaint or legal action
        with high relevance — highest signal activities for scoring.
        """
        return (self.formal_complaint or self.legal_action) and \
               (self.topic_relevance_score is not None and self.topic_relevance_score >= 0.7)

    @property
    def days_since_publication(self) -> int:
        """Days since the activity was published."""
        return (date.today() - self.publication_date).days

    @property
    def is_recent(self) -> bool:
        """TRUE if published within the last 90 days."""
        return self.days_since_publication <= 90

    def __repr__(self) -> str:
        return f"<M1 {self.ngo_name} | {self.activity_type} | {self.publication_date}>"

print("✓ M1NgoActivity defined")


#M2: Media Press
#Tracks major press coverage of data privacy and AI regulation issues
#Source: News websites

class M2MediaPress(Base):
    __tablename__ = "m2_media_press"

    __table_args__ = (
        CheckConstraint(
            """outlet IN (
                'The Guardian', 'The Times', 'Financial Times',
                'BBC', 'The Register', 'WIRED UK',
                'Computer Weekly', 'City A.M.', 'Other'
            )""",
            name="ck_m2_outlet"
        ),
        CheckConstraint(
            "outlet_tier IN (1, 2, 3)",
            name="ck_m2_outlet_tier"
        ),
        CheckConstraint(
            """story_type IN (
                'Investigation', 'Opinion', 'News',
                'Data Breach', 'Regulatory Response', 'Profile'
            )""",
            name="ck_m2_story_type"
        ),
        CheckConstraint(
            """enforcement_stance IN (
                'Pro-enforcement', 'Neutral',
                'Pro-regulatory', 'Mixed'
            )""",
            name="ck_m2_enforcement_stance"
        ),
        CheckConstraint(
            "topic_relevance_score BETWEEN 0 AND 1",
            name="ck_m2_relevance"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_m2_nlp_confidence"
        ),
    )

    # Primary key
    press_id                = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Identity
    publication_date        = Column(Date, nullable=False, index=True)
    outlet                  = Column(String(100), nullable=False, index=True)
    outlet_tier             = Column(Integer, nullable=False)            # 1=National/BBC, 2=Specialist trade, 3=Regional
    headline                = Column(Text, nullable=False)


    # Story classification
    story_type              = Column(String(50), nullable=False, index=True)
    target_org              = Column(String(300))                        # Subject of the story if applicable

    # ICO flags
    ico_mentioned           = Column(Boolean, default=False, index=True)
    ico_action              = Column(Boolean, default=False, index=True) # Does article call for ICO action?

    # Content
    content_summary         = Column(Text)                               # NLP generated summary

    # Routing + NLP
    processing_activities   = Column(String(500))
    topic_relevance_score   = Column(Float, index=True)
    enforcement_stance      = Column(String(20), index=True)

    # Provenance
    source_url              = Column(Text)
    author                  = Column(Text)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence          = Column(Float)
    manually_reviewed       = Column(Boolean, default=False, index=True)

    # Computed properties
    @property
    def is_tier_one(self) -> bool:
        """TRUE if published in a national outlet or BBC (tier 1)."""
        return self.outlet_tier == 1

    @property
    def is_high_impact(self) -> bool:
        """
        TRUE if tier 1 outlet + high relevance + calls for ICO action.
        Highest signal press items for scoring.
        """
        return self.is_tier_one and \
               self.ico_action and \
               (self.topic_relevance_score is not None and self.topic_relevance_score >= 0.7)

    @property
    def days_since_publication(self) -> int:
        return (date.today() - self.publication_date).days

    @property
    def is_recent(self) -> bool:
        """TRUE if published within the last 90 days."""
        return self.days_since_publication <= 90

    def __repr__(self) -> str:
        return f"<M2 {self.outlet} | {self.publication_date} | {self.headline[:60]}>"

print("✓ M2MediaPress defined")


#Create all tables

Base.metadata.create_all(engine, checkfirst=True)
print("✓ Tables created: m1_ngo_activity, m2_media_press")


#Demo data

def load_demo_data():
    with Session(engine) as session:

        if session.query(M1NgoActivity).first() is not None:
            print("Demo data already loaded, skipping.")
            return

        # M1: NGO Activity 
        m1_rows = [
            M1NgoActivity(
                ngo_name="Big Brother Watch",
                publication_date=date(2025, 1, 14),
                activity_type="Formal Complaint",
                title="Complaint to ICO regarding unlawful facial recognition use by retail chains",
                source_url="https://bigbrotherwatch.org.uk/campaigns/face-off/",
                target_org="Major UK Retail Chains",
                ico_named=True,
                formal_complaint=True,
                complaint_ref="BBW-ICO-2025-001",
                legal_action=False,
                content_summary="Big Brother Watch filed a formal complaint with the ICO against several major UK retailers using live facial recognition technology without adequate legal basis or transparency.",
                processing_activities="Biometric data, automated decision-making, profiling",
                topic_relevance_score=0.95,
                enforcement_stance="Pro-enforcement",
                gdpr_articles="Article 9, Article 22, Article 13",
                nlp_confidence=0.92,
                manually_reviewed=True,
            ),
            M1NgoActivity(
                ngo_name="Foxglove",
                publication_date=date(2025, 1, 28),
                activity_type="Legal Challenge",
                title="Foxglove launches judicial review of government AI decision-making in benefits system",
                source_url="https://foxglove.org.uk/cases/ai-benefits/",
                target_org="Department for Work and Pensions",
                ico_named=True,
                formal_complaint=False,
                complaint_ref=None,
                legal_action=True,
                content_summary="Foxglove initiated judicial review proceedings against the DWP's use of AI to flag benefits claimants for investigation, arguing a breach of Article 22 UK GDPR and lack of meaningful human oversight.",
                processing_activities="Automated decision-making, profiling, special category data",
                topic_relevance_score=0.97,
                enforcement_stance="Pro-enforcement",
                gdpr_articles="Article 22, Article 5, Article 9",
                nlp_confidence=0.94,
                manually_reviewed=True,
            ),
            M1NgoActivity(
                ngo_name="Ada Lovelace Institute",
                publication_date=date(2025, 2, 10),
                activity_type="Report",
                title="Algorithmic accountability in the UK: gaps in the regulatory framework",
                source_url="https://www.adalovelaceinstitute.org/report/algorithmic-accountability-uk/",
                target_org=None,
                ico_named=True,
                formal_complaint=False,
                complaint_ref=None,
                legal_action=False,
                content_summary="The Ada Lovelace Institute published a report identifying gaps in the UK's regulatory framework for algorithmic systems, recommending the ICO be given expanded powers to audit AI systems in high-risk sectors.",
                processing_activities="Automated decision-making, AI model training",
                topic_relevance_score=0.88,
                enforcement_stance="Pro-enforcement",
                gdpr_articles="Article 22, Article 35",
                nlp_confidence=0.87,
                manually_reviewed=True,
            ),
            M1NgoActivity(
                ngo_name="Open Rights Group",
                publication_date=date(2025, 2, 20),
                activity_type="Parliamentary Submission",
                title="ORG submission to DSIT committee on Data (Use and Access) Bill — automated decision-making provisions",
                source_url="https://www.openrightsgroup.org/publications/data-use-access-bill-submission/",
                target_org="DSIT Select Committee",
                ico_named=True,
                formal_complaint=False,
                complaint_ref=None,
                legal_action=False,
                content_summary="Open Rights Group submitted evidence to the DSIT Select Committee arguing the Data (Use and Access) Bill's automated decision-making provisions are insufficient and calling for stronger ICO oversight powers.",
                processing_activities="Automated decision-making, data sharing",
                topic_relevance_score=0.84,
                enforcement_stance="Pro-enforcement",
                gdpr_articles="Article 22, Article 13",
                nlp_confidence=0.83,
                manually_reviewed=True,
            ),
            M1NgoActivity(
                ngo_name="Privacy International",
                publication_date=date(2024, 12, 5),
                activity_type="Publication",
                title="The ICO at a crossroads: enforcement trends and the challenge of AI",
                source_url="https://privacyinternational.org/report/ico-crossroads/",
                target_org=None,
                ico_named=True,
                formal_complaint=False,
                complaint_ref=None,
                legal_action=False,
                content_summary="Privacy International published an analysis of ICO enforcement trends, finding that AI-related enforcement actions have increased 34% year-on-year but remain low relative to the scale of AI deployment.",
                processing_activities="Automated decision-making, profiling, data sharing",
                topic_relevance_score=0.91,
                enforcement_stance="Pro-enforcement",
                gdpr_articles="Article 5, Article 22",
                nlp_confidence=0.89,
                manually_reviewed=True,
            ),
            M1NgoActivity(
                ngo_name="Connected by Data",
                publication_date=date(2025, 3, 3),
                activity_type="Open Letter",
                title="Open letter to ICO: call for mandatory algorithmic impact assessments in public sector AI",
                source_url="https://connectedbydata.org/resources/open-letter-ico-2025/",
                target_org="ICO",
                ico_named=True,
                formal_complaint=False,
                complaint_ref=None,
                legal_action=False,
                content_summary="Connected by Data coordinated an open letter signed by 47 civil society organisations calling on the ICO to require mandatory algorithmic impact assessments for all public sector AI deployments.",
                processing_activities="Automated decision-making, AI model training",
                topic_relevance_score=0.86,
                enforcement_stance="Pro-enforcement",
                gdpr_articles="Article 35, Article 22",
                nlp_confidence=0.84,
                manually_reviewed=True,
            ),
        ]

        # M2: Media Press
        m2_rows = [
            M2MediaPress(
                publication_date=date(2025, 2, 18),
                outlet="The Guardian",
                outlet_tier=1,
                headline="ICO launches investigation into AI hiring tools used by FTSE 100 companies",
                source_url="https://www.theguardian.com/technology/2025/feb/18/ico-ai-hiring-tools",
                author="Stephanie Kirchgaessner",
                story_type="News",
                target_org="FTSE 100 companies",
                ico_mentioned=True,
                ico_action=True,
                content_summary="The Guardian reports that the ICO has launched a formal investigation into the use of AI-powered hiring tools by major UK employers, focusing on compliance with Article 22 UK GDPR automated decision-making requirements.",
                processing_activities="Automated decision-making, profiling",
                topic_relevance_score=0.96,
                enforcement_stance="Pro-enforcement",
                nlp_confidence=0.93,
                manually_reviewed=True,
            ),
            M2MediaPress(
                publication_date=date(2025, 1, 30),
                outlet="Financial Times",
                outlet_tier=1,
                headline="UK data watchdog signals tougher stance on AI as enforcement actions double",
                source_url="https://www.ft.com/content/ico-ai-enforcement-2025",
                author="Madhumita Murgia",
                story_type="Investigation",
                target_org=None,
                ico_mentioned=True,
                ico_action=False,
                content_summary="The FT reports that ICO enforcement actions related to AI and automated decision-making doubled in 2024, with the regulator signalling a more assertive approach to AI compliance in the coming year.",
                processing_activities="Automated decision-making, AI model training",
                topic_relevance_score=0.93,
                enforcement_stance="Pro-enforcement",
                nlp_confidence=0.91,
                manually_reviewed=True,
            ),
            M2MediaPress(
                publication_date=date(2025, 2, 5),
                outlet="The Register",
                outlet_tier=2,
                headline="ICO fines HealthAI £1.2m for unlawful processing of patient data in diagnostic AI",
                source_url="https://www.theregister.com/2025/02/05/ico-healthai-fine/",
                author="Thomas Claburn",
                story_type="Regulatory Response",
                target_org="HealthAI Technologies Ltd",
                ico_mentioned=True,
                ico_action=False,
                content_summary="The Register covers the ICO's £1.2m fine against HealthAI Technologies for processing special category health data without adequate legal basis in an AI diagnostic tool.",
                processing_activities="Special category data, automated decision-making",
                topic_relevance_score=0.94,
                enforcement_stance="Pro-enforcement",
                nlp_confidence=0.90,
                manually_reviewed=True,
            ),
            M2MediaPress(
                publication_date=date(2025, 1, 15),
                outlet="BBC",
                outlet_tier=1,
                headline="Should AI be allowed to make decisions about your benefits?",
                source_url="https://www.bbc.co.uk/news/technology/ai-benefits-decisions",
                author="Zoe Kleinman",
                story_type="Investigation",
                target_org="Department for Work and Pensions",
                ico_mentioned=True,
                ico_action=True,
                content_summary="BBC investigation into the use of AI in the UK benefits system, questioning whether automated decision-making meets data protection standards and calling for ICO scrutiny of DWP AI systems.",
                processing_activities="Automated decision-making, profiling, special category data",
                topic_relevance_score=0.91,
                enforcement_stance="Pro-enforcement",
                nlp_confidence=0.88,
                manually_reviewed=True,
            ),
            M2MediaPress(
                publication_date=date(2025, 2, 25),
                outlet="WIRED UK",
                outlet_tier=2,
                headline="The quiet revolution in UK data protection enforcement — and what it means for AI companies",
                source_url="https://www.wired.co.uk/article/uk-data-protection-ai-enforcement",
                author="Matt Burgess",
                story_type="Investigation",
                target_org=None,
                ico_mentioned=True,
                ico_action=False,
                content_summary="WIRED UK analysis of the ICO's evolving enforcement approach to AI, noting a shift toward proactive investigations and increased penalties for AI-related data protection breaches.",
                processing_activities="Automated decision-making, AI model training, profiling",
                topic_relevance_score=0.89,
                enforcement_stance="Pro-enforcement",
                nlp_confidence=0.86,
                manually_reviewed=True,
            ),
            M2MediaPress(
                publication_date=date(2025, 3, 1),
                outlet="Computer Weekly",
                outlet_tier=2,
                headline="ICO guidance on AI and UK GDPR: what organisations need to know",
                source_url="https://www.computerweekly.com/news/ico-ai-gdpr-guidance-2025",
                author="Bill Goodwin",
                story_type="News",
                target_org=None,
                ico_mentioned=True,
                ico_action=False,
                content_summary="Computer Weekly covers the ICO's finalised guidance on AI and automated decision-making under UK GDPR, highlighting key compliance requirements for organisations deploying AI systems.",
                processing_activities="Automated decision-making, AI model training",
                topic_relevance_score=0.87,
                enforcement_stance="Neutral",
                nlp_confidence=0.84,
                manually_reviewed=True,
            ),
        ]

        session.add_all(m1_rows + m2_rows)
        session.commit()
        print(f"✓ Inserted {len(m1_rows)} M1 rows and {len(m2_rows)} M2 rows")

load_demo_data()


# DataFrame helpers

def get_m1_dataframe() -> pd.DataFrame:
    """Return full M1 table with computed columns added."""
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT * FROM m1_ngo_activity ORDER BY publication_date DESC"),
            conn
        )
    df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce").dt.date
    today = date.today()
    df["days_since_publication"] = df["publication_date"].apply(
        lambda d: (today - d).days if pd.notnull(d) else None
    )
    df["is_recent"]     = df["days_since_publication"].apply(
        lambda d: d <= 90 if pd.notnull(d) else False
    )
    df["is_high_impact"] = (
        (df["formal_complaint"] | df["legal_action"]) &
        (df["topic_relevance_score"] >= 0.7)
    )
    return df


def get_m2_dataframe() -> pd.DataFrame:
    """Return full M2 table with computed columns added."""
    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT * FROM m2_media_press ORDER BY publication_date DESC"),
            conn
        )
    df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce").dt.date
    today = date.today()
    df["days_since_publication"] = df["publication_date"].apply(
        lambda d: (today - d).days if pd.notnull(d) else None
    )
    df["is_recent"]      = df["days_since_publication"].apply(
        lambda d: d <= 90 if pd.notnull(d) else False
    )
    df["is_tier_one"]    = df["outlet_tier"] == 1
    df["is_high_impact"] = (
        (df["outlet_tier"] == 1) &
        (df["ico_action"] == True) &
        (df["topic_relevance_score"] >= 0.7)
    )
    return df


def get_media_summary() -> pd.DataFrame:
    """
    Cross-table summary of NGO and press activity.
    Feeds directly into the scoring layer.
    """
    with engine.connect() as conn:
        df = pd.read_sql(text("""
            SELECT
                'NGO Activity'          AS source,
                COUNT(*)                AS total_items,
                SUM(CASE WHEN ico_named THEN 1 ELSE 0 END)          AS ico_named_count,
                SUM(CASE WHEN formal_complaint THEN 1 ELSE 0 END)   AS formal_complaints,
                SUM(CASE WHEN legal_action THEN 1 ELSE 0 END)       AS legal_actions,
                AVG(topic_relevance_score)                          AS avg_relevance
            FROM m1_ngo_activity
            UNION ALL
            SELECT
                'Media Press'           AS source,
                COUNT(*)                AS total_items,
                SUM(CASE WHEN ico_mentioned THEN 1 ELSE 0 END)      AS ico_named_count,
                SUM(CASE WHEN ico_action THEN 1 ELSE 0 END)         AS formal_complaints,
                0                                                   AS legal_actions,
                AVG(topic_relevance_score)                          AS avg_relevance
            FROM m2_media_press
        """), conn)
    return df


def get_ngo_activity_by_org() -> pd.DataFrame:
    """Activity count and average relevance per NGO — useful for weighting."""
    with engine.connect() as conn:
        df = pd.read_sql(text("""
            SELECT
                ngo_name,
                COUNT(*)                                            AS activity_count,
                SUM(CASE WHEN formal_complaint THEN 1 ELSE 0 END)  AS complaints,
                SUM(CASE WHEN legal_action THEN 1 ELSE 0 END)      AS legal_actions,
                SUM(CASE WHEN ico_named THEN 1 ELSE 0 END)         AS ico_named,
                AVG(topic_relevance_score)                         AS avg_relevance
            FROM m1_ngo_activity
            GROUP BY ngo_name
            ORDER BY activity_count DESC
        """), conn)
    return df


def get_press_by_outlet() -> pd.DataFrame:
    """Article count and ICO action rate per outlet — useful for weighting by outlet tier."""
    with engine.connect() as conn:
        df = pd.read_sql(text("""
            SELECT
                outlet,
                outlet_tier,
                COUNT(*)                                        AS article_count,
                SUM(CASE WHEN ico_mentioned THEN 1 ELSE 0 END) AS ico_mentioned_count,
                SUM(CASE WHEN ico_action THEN 1 ELSE 0 END)    AS ico_action_count,
                AVG(topic_relevance_score)                     AS avg_relevance
            FROM m2_media_press
            GROUP BY outlet, outlet_tier
            ORDER BY outlet_tier, article_count DESC
        """), conn)
    return df


#Display demo data

m1_df = get_m1_dataframe()
print("\n── M1: NGO Activity ────────────────────────────────────────────")
print(m1_df[[
    "ngo_name", "activity_type", "publication_date",
    "ico_named", "formal_complaint", "legal_action",
    "topic_relevance_score", "is_high_impact", "is_recent"
]].to_string(index=False))

m2_df = get_m2_dataframe()
print("\n── M2: Media Press ─────────────────────────────────────────────")
print(m2_df[[
    "outlet", "outlet_tier", "publication_date", "story_type",
    "ico_mentioned", "ico_action", "enforcement_stance",
    "topic_relevance_score", "is_high_impact"
]].to_string(index=False))

print("\n── Media Summary (feeds scoring layer) ─────────────────────────")
print(get_media_summary().to_string(index=False))

print("\n── NGO Activity by Organisation ────────────────────────────────")
print(get_ngo_activity_by_org().to_string(index=False))

print("\n── Press Coverage by Outlet ────────────────────────────────────")
print(get_press_by_outlet().to_string(index=False))
