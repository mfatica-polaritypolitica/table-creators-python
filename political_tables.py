## Creates six political tables
## Requirements: pip install sqlalchemy psycopg2-binary pandas

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

## Connection — update password before running
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


## P1: Government Speeches
# One row per published speech or press release
# Source: gov.uk, Primary departments: DSIT, Cabinet Office, Home Office

class P1GovernmentSpeeches(Base):
    __tablename__ = "p1_government_speeches"

    __table_args__ = (
        CheckConstraint(
            """department IN (
                'DSIT', 'Cabinet Office', 'Home Office',
                'HM Treasury', 'DCMS', 'MOJ', 'Other'
            )""",
            name="ck_p1_department"
        ),
        CheckConstraint(
            "priority_level IN ('Primary', 'Secondary', 'Peripheral', 'None')",
            name="ck_p1_priority_level"
        ),
        CheckConstraint(
            "regulatory_stance IN ('Pro-enforcement', 'Neutral', 'Deregulatory', 'Mixed')",
            name="ck_p1_regulatory_stance"
        ),
        CheckConstraint(
            "topic_relevance_score BETWEEN 0 AND 1",
            name="ck_p1_relevance"
        ),
        CheckConstraint(
            "enforcement_signal BETWEEN 0 AND 1",
            name="ck_p1_enforcement_signal"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_p1_nlp_confidence"
        ),
    )

    # Primary key
    speech_id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Identity
    title                   = Column(String(500), nullable=False)
    speaker_name            = Column(String(200))
    speaker_role            = Column(String(300))                        # e.g. Secretary of State for Science
    party                   = Column(String(100))
    department              = Column(String(100), nullable=False, index=True)
    speech_date             = Column(Date, nullable=False, index=True)
    speech_url              = Column(Text)

    # Deduplication
    rss_guid                = Column(String(500), unique=True)

    # NLP / relevance
    topic_relevance_score   = Column(Float, index=True)
    processing_activities   = Column(String(500))
    relevance_tag           = Column(String(500))
    priority_level          = Column(String(20))                         # How prominent is AI/data as topic?

    # Regulatory signal
    regulatory_stance       = Column(String(20), index=True)             # Pro-enforcement, Neutral, Deregulatory, Mixed
    enforcement_signal      = Column(Float)                              # Composite NLP enforcement intent score
    nlp_confidence          = Column(Float)

    # ICO flag
    ico_mentioned           = Column(Boolean, default=False)

    # Provenance
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    raw_text                = Column(Text)                               # Full text for NLP processing
    manually_reviewed       = Column(Boolean, default=False, index=True)

    @property
    def is_pro_enforcement(self) -> bool:
        return self.regulatory_stance == "Pro-enforcement"

    @property
    def is_high_relevance(self) -> bool:
        return self.topic_relevance_score is not None and self.topic_relevance_score >= 0.7

    def __repr__(self) -> str:
        return f"<P1 {self.department} | {self.speech_date} | {self.title[:60]}>"

print("✓ P1GovernmentSpeeches defined")


## P2: Party Manifestos
# One row per relevant commitment from a party manifesto 
# Source: MAnifesto project, political party websites

class P2PartyManifestos(Base):
    __tablename__ = "p2_party_manifestos"

    __table_args__ = (
        CheckConstraint(
            "obligation_direction IN ('Increases', 'Decreases', 'Clarifies', 'Mixed')",
            name="ck_p2_obligation_direction"
        ),
        CheckConstraint(
            "priority_level IN ('Primary', 'Secondary', 'Peripheral')",
            name="ck_p2_priority_level"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_p2_nlp_confidence"
        ),
    )

    # Primary key
    manifesto_id            = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Identity
    party                   = Column(String(100), nullable=False, index=True)
    election_year           = Column(Integer, nullable=False, index=True)
    commitment_text         = Column(Text, nullable=False)

    # Routing
    processing_activities   = Column(String(500))
    topic_tags              = Column(String(500))

    # Signal
    obligation_direction    = Column(String(20))                         # Increases, Decreases, Clarifies, Mixed
    priority_level          = Column(String(20))                         # How prominently does this feature?

    # Context
    governing_party         = Column(Boolean, default=False)             # Is this party currently in government?
    manifesto_project_id    = Column(String(100))                        # e.g. UK_2024_LAB_042

    # Provenance
    source_url              = Column(Text)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence          = Column(Float)
    manually_reviewed       = Column(Boolean, default=False, index=True)

    @property
    def is_governing_commitment(self) -> bool:
        """TRUE if this commitment is from the current governing party."""
        return self.governing_party is True

    def __repr__(self) -> str:
        return f"<P2 {self.party} | {self.election_year} | {self.commitment_text[:60]}>"

print("✓ P2PartyManifestos defined")


## P3: Budget Documents
#One row per relevant budget line or commitment
#Source: gov.uk

class P3BudgetDocuments(Base):
    __tablename__ = "p3_budget_documents"

    __table_args__ = (
        CheckConstraint(
            """item_type IN (
                'ICO Allocation', 'Tech Regulation Fund',
                'AI Safety Spending', 'Digital Infrastructure',
                'Enforcement Budget', 'Other'
            )""",
            name="ck_p3_item_type"
        ),
        CheckConstraint(
            "yoy_direction IN ('Increase', 'Decrease', 'Flat', 'New Item')",
            name="ck_p3_yoy_direction"
        ),
        CheckConstraint(
            "enforcement_signal BETWEEN 0 AND 1",
            name="ck_p3_enforcement_signal"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_p3_nlp_confidence"
        ),
    )

    # Primary key
    budget_id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Identity
    budget_year             = Column(Integer, nullable=False, index=True) # e.g. 2025 for FY 2025/26
    budget_date             = Column(Date, nullable=False)
    item_type               = Column(String(100), nullable=False, index=True)
    item_description        = Column(Text, nullable=False)

    # Financials
    amount_gbp              = Column(Numeric(15, 2))
    yoy_change_pct          = Column(Float)                              # Computed: year-on-year % change
    yoy_direction           = Column(String(20))                         # Increase, Decrease, Flat, New Item

    # Flags
    ico_budget_flag         = Column(Boolean, default=False, index=True) # Is this the ICO's core resource budget?

    # Signal
    enforcement_signal      = Column(Float)

    # Provenance
    source_url              = Column(Text)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence          = Column(Float)
    manually_reviewed       = Column(Boolean, default=False, index=True)

    # Computed properties
    @property
    def amount_gbp_millions(self) -> Optional[float]:
        """Amount expressed in £ millions for display."""
        if self.amount_gbp:
            return round(float(self.amount_gbp) / 1_000_000, 3)
        return None

    @property
    def is_ico_budget(self) -> bool:
        return self.ico_budget_flag is True

    def __repr__(self) -> str:
        return f"<P3 FY{self.budget_year} | {self.item_type} | £{self.amount_gbp}>"

print("✓ P3BudgetDocuments defined")


## P4: Electoral Sinals
# One row per electoral snapshot, used to estimate probability of government change within 12 months
# Source: Polling data

class P4ElectoralSignals(Base):
    __tablename__ = "p4_electoral_signals"

    __table_args__ = (
        CheckConstraint(
            "governing_poll_ptc BETWEEN 0 AND 100",
            name="ck_p4_governing_poll_ptc"
        ),
        CheckConstraint(
            "opposition_poll_ptc BETWEEN 0 AND 100",
            name="ck_p4_opposition_poll_ptc"
        ),
        CheckConstraint(
            "prediction_market_prob BETWEEN 0 AND 1",
            name="ck_p4_prediction_market_prob"
        ),
        CheckConstraint(
            "gov_change_12m BETWEEN 0 AND 1",
            name="ck_p4_gov_change_12m"
        ),
    )

    # Primary key
    electoral_id            = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Snapshot timing
    record_date             = Column(Date, nullable=False, index=True)
    last_election_date      = Column(Date, nullable=False)
    next_election_due       = Column(Date, nullable=False)               # Latest statutory date for next election

    # Governing party
    governing_party         = Column(String(100), nullable=False)

    # Polling
    governing_poll_ptc      = Column(Float)                              # Average poll share for governing party
    opposition_poll_ptc     = Column(Float)                              # Average poll share for largest opposition
    poll_source             = Column(String(200))

    # Prediction market
    prediction_market_prob  = Column(Float)                              # Probability of governing party winning next election

    # Modelled probability of government change in next 12 months
    # Computed: based on prediction_market_prob, polling gap, time until election
    gov_change_12m          = Column(Float, index=True)

    # Provenance
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Computed properties
    @property
    def polling_gap(self) -> Optional[float]:
        """Governing party lead/deficit vs largest opposition party."""
        if self.governing_poll_ptc is not None and self.opposition_poll_ptc is not None:
            return round(self.governing_poll_ptc - self.opposition_poll_ptc, 1)
        return None

    @property
    def days_to_election(self) -> Optional[int]:
        """Days until the latest statutory election date."""
        if self.next_election_due:
            return (self.next_election_due - date.today()).days
        return None

    @property
    def gov_change_likely(self) -> bool:
        """
        TRUE if gov_change_12m > 0.5.
        When TRUE, current government signals should be down-weighted
        to prevent over-indexing on a potentially outgoing government.
        """
        return self.gov_change_12m is not None and self.gov_change_12m > 0.5

    @property
    def computed_gov_change_12m(self) -> Optional[float]:
        """
        Model: gov_change_12m estimate from available inputs.
        Uses prediction market probability as primary signal,
        adjusted by polling gap and time remaining.
        Only used if gov_change_12m not already set by pipeline.
        """
        if self.prediction_market_prob is None:
            return None
        # Probability of NOT winning = probability of change
        base = 1 - self.prediction_market_prob
        # Adjust slightly for time: closer to election = more certain
        if self.days_to_election is not None and self.days_to_election < 365:
            time_factor = 1 + (1 - self.days_to_election / 365) * 0.1
            base = min(base * time_factor, 1.0)
        return round(base, 4)

    def __repr__(self) -> str:
        return f"<P4 {self.governing_party} | {self.record_date} | change_12m={self.gov_change_12m}>"

print("✓ P4ElectoralSignals defined")

##P5: Social Listening/X
#One row per monitored post, monitored accounts: prominent ministers, shadow spokespeople
# Source: social media data provider

class P5SocialListening(Base):
    __tablename__ = "p5_social_listening"

    __table_args__ = (
        CheckConstraint(
            """account_category IN (
                'Minister', 'Shadow Minister', 'MP',
                'Aide', 'Party Account', 'Other'
            )""",
            name="ck_p5_account_category"
        ),
        CheckConstraint(
            "priority_level IN ('Primary', 'Secondary', 'Peripheral')",
            name="ck_p5_priority_level"
        ),
        CheckConstraint(
            "regulatory_stance IN ('Pro-enforcement', 'Neutral', 'Deregulatory', 'Mixed')",
            name="ck_p5_regulatory_stance"
        ),
        CheckConstraint(
            "topic_relevance_score BETWEEN 0 AND 1",
            name="ck_p5_relevance"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_p5_nlp_confidence"
        ),
    )

    # Primary key
    social_id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Account identity
    platform                = Column(String(50), nullable=False, default="X/Twitter")
    account_handle          = Column(String(200), nullable=False, index=True)
    account_name            = Column(String(200))
    account_category        = Column(String(50), nullable=False, index=True)
    party                   = Column(String(100), index=True)
    party_power             = Column(Boolean, default=False)             # Is account holder's party in government?

    # Post
    post_date               = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    post_id_platform        = Column(String(200), unique=True)           # Native post ID from X

    # Content
    raw_text                = Column(Text)

    # Routing + NLP
    processing_activities   = Column(String(500))
    topic_relevance_score   = Column(Float, index=True)
    topic_tags              = Column(String(500))
    priority_level          = Column(String(20))
    regulatory_stance       = Column(String(20), index=True)

    # Engagement (proxy for reach at time of ingestion)
    engagement_score        = Column(Integer)                            # Likes + reposts

    # Provenance
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence          = Column(Float)
    manually_reviewed       = Column(Boolean, default=False, index=True)

    @property
    def is_governing_party(self) -> bool:
        return self.party_power is True

    @property
    def is_high_reach(self) -> bool:
        """Proxy for high-reach post: engagement > 100."""
        return self.engagement_score is not None and self.engagement_score > 100

    def __repr__(self) -> str:
        return f"<P5 @{self.account_handle} | {self.post_date} | stance={self.regulatory_stance}>"

print("✓ P5SocialListening defined")


## P6: Parliamentary Q&A
#One row per question and answer pair 
#Source: questions-statements.parliament.uk

class P6ParliamentaryQA(Base):
    __tablename__ = "p6_parliamentary_qa"

    __table_args__ = (
        CheckConstraint(
            "question_type IN ('Written', 'Oral', 'Urgent')",
            name="ck_p6_question_type"
        ),
        CheckConstraint(
            "priority_level IN ('Primary', 'Secondary', 'Peripheral')",
            name="ck_p6_priority_level"
        ),
        CheckConstraint(
            """government_position IN (
                'Supportive of Enforcement', 'Neutral',
                'Resistant', 'Unclear'
            )""",
            name="ck_p6_government_position"
        ),
        CheckConstraint(
            "topic_relevance_score BETWEEN 0 AND 1",
            name="ck_p6_relevance"
        ),
        CheckConstraint(
            "enforcement_signal BETWEEN 0 AND 1",
            name="ck_p6_enforcement_signal"
        ),
        CheckConstraint(
            "nlp_confidence BETWEEN 0 AND 1",
            name="ck_p6_nlp_confidence"
        ),
    )

    # Primary key
    pqa_id                  = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Timing
    question_date           = Column(Date, nullable=False, index=True)
    answer_date             = Column(Date, index=True)
    question_type           = Column(String(20), nullable=False)         # Written, Oral, Urgent

    # Asking MP
    asking_mp               = Column(String(200), nullable=False)
    asking_party            = Column(String(100))
    asking_party_gov        = Column(Boolean, default=False)             # Is asking MP's party the governing party?

    # Answering minister
    answering_minister      = Column(String(200))
    answering_department    = Column(String(200))
    answering_party         = Column(String(100))

    # Content
    question_text           = Column(Text, nullable=False)
    answer_text             = Column(Text)

    # Routing + NLP
    processing_activities   = Column(String(500))
    topic_tags              = Column(String(500))
    topic_relevance_score   = Column(Float, index=True)
    priority_level          = Column(String(20))
    government_position     = Column(String(50))                         # Government's stated position on enforcement
    ico_mentioned           = Column(Boolean, default=False, index=True)
    enforcement_signal      = Column(Float)

    # Provenance
    source_url              = Column(Text)
    rss_guid                = Column(String(500), unique=True)
    ingested_at             = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    nlp_confidence          = Column(Float)
    manually_reviewed       = Column(Boolean, default=False, index=True)

    # Computed properties
    @property
    def days_to_answer(self) -> Optional[int]:
        """Days between question being tabled and answer being published."""
        if self.question_date and self.answer_date:
            return (self.answer_date - self.question_date).days
        return None

    @property
    def is_opposition_question(self) -> bool:
        """TRUE if question is from an MP not in the governing party."""
        return self.asking_party_gov is False

    def __repr__(self) -> str:
        return f"<P6 {self.asking_mp} → {self.answering_department} | {self.question_date}>"

print("✓ P6ParliamentaryQA defined")


## Create all tables

Base.metadata.create_all(engine, checkfirst=True)
print("✓ Tables created: p1_government_speeches, p2_party_manifestos, p3_budget_documents,")
print("                  p4_electoral_signals, p5_social_listening, p6_parliamentary_qa")


## Demo data

def load_demo_data():
    with Session(engine) as session:

        if session.query(P1GovernmentSpeeches).first() is not None:
            print("Demo data already loaded, skipping.")
            return

        # P1: Government Speeches 
        p1_rows = [
            P1GovernmentSpeeches(
                title="Secretary of State speech: Building a trusted AI ecosystem",
                speaker_name="Peter Kyle",
                speaker_role="Secretary of State for Science, Innovation and Technology",
                party="Labour",
                department="DSIT",
                speech_date=date(2025, 1, 20),
                speech_url="https://www.gov.uk/government/speeches/building-trusted-ai",
                rss_guid="gov.uk/speeches/building-trusted-ai-2025",
                topic_relevance_score=0.93,
                processing_activities="Automated decision-making, AI model training",
                relevance_tag="ai,regulation,enforcement,ico",
                priority_level="Primary",
                regulatory_stance="Pro-enforcement",
                enforcement_signal=0.82,
                nlp_confidence=0.88,
                ico_mentioned=True,
                raw_text="The government is committed to ensuring AI systems are trustworthy and accountable...",
                manually_reviewed=True,
            ),
            P1GovernmentSpeeches(
                title="Press release: New guidance on data sharing in the public sector",
                speaker_name="Cabinet Office",
                speaker_role=None,
                party="Labour",
                department="Cabinet Office",
                speech_date=date(2025, 2, 5),
                speech_url="https://www.gov.uk/government/news/data-sharing-guidance",
                rss_guid="gov.uk/news/data-sharing-guidance-2025",
                topic_relevance_score=0.78,
                processing_activities="Data sharing",
                relevance_tag="data_sharing,public_sector,guidance",
                priority_level="Secondary",
                regulatory_stance="Neutral",
                enforcement_signal=0.45,
                nlp_confidence=0.82,
                ico_mentioned=False,
                raw_text="The Cabinet Office has published updated guidance on data sharing between government departments...",
                manually_reviewed=True,
            ),
            P1GovernmentSpeeches(
                title="Oral statement: AI Opportunities Action Plan",
                speaker_name="Peter Kyle",
                speaker_role="Secretary of State for Science, Innovation and Technology",
                party="Labour",
                department="DSIT",
                speech_date=date(2025, 1, 13),
                speech_url="https://www.gov.uk/government/speeches/ai-opportunities-action-plan",
                rss_guid="gov.uk/speeches/ai-action-plan-2025",
                topic_relevance_score=0.88,
                processing_activities="AI model training, automated decision-making",
                relevance_tag="ai,action_plan,regulation",
                priority_level="Primary",
                regulatory_stance="Mixed",
                enforcement_signal=0.58,
                nlp_confidence=0.85,
                ico_mentioned=True,
                raw_text="The AI Opportunities Action Plan sets out how the UK will become a global leader in AI...",
                manually_reviewed=True,
            ),
        ]

        #P2: Party Manifestos
        p2_rows = [
            P2PartyManifestos(
                party="Labour",
                election_year=2024,
                commitment_text="We will ensure the ICO has the powers and resources it needs to enforce data protection law effectively, including in the context of AI systems.",
                processing_activities="Automated decision-making, data protection",
                topic_tags="ico,enforcement,ai,data_protection",
                obligation_direction="Increases",
                priority_level="Primary",
                governing_party=True,
                manifesto_project_id="UK_2024_LAB_088",
                source_url="https://labour.org.uk/change/",
                nlp_confidence=0.91,
                manually_reviewed=True,
            ),
            P2PartyManifestos(
                party="Labour",
                election_year=2024,
                commitment_text="We will introduce legislation to regulate the most powerful AI models and ensure algorithmic transparency in public sector decision-making.",
                processing_activities="AI model training, automated decision-making",
                topic_tags="ai_regulation,algorithmic_transparency,public_sector",
                obligation_direction="Increases",
                priority_level="Primary",
                governing_party=True,
                manifesto_project_id="UK_2024_LAB_091",
                source_url="https://labour.org.uk/change/",
                nlp_confidence=0.89,
                manually_reviewed=True,
            ),
            P2PartyManifestos(
                party="Conservative",
                election_year=2024,
                commitment_text="We will take a pro-innovation approach to AI regulation, avoiding heavy-handed rules that stifle growth and competitiveness.",
                processing_activities="AI model training",
                topic_tags="ai_regulation,pro_innovation,deregulation",
                obligation_direction="Decreases",
                priority_level="Secondary",
                governing_party=False,
                manifesto_project_id="UK_2024_CON_044",
                source_url="https://www.conservatives.com/our-plan",
                nlp_confidence=0.84,
                manually_reviewed=True,
            ),
        ]

        # P3: Budget Documents 
        p3_rows = [
            P3BudgetDocuments(
                budget_year=2024,
                budget_date=date(2024, 10, 30),
                item_type="ICO Allocation",
                item_description="ICO resource budget allocation for FY 2025/26 including expanded AI enforcement capabilities",
                amount_gbp=43_200_000,
                yoy_change_pct=8.5,
                yoy_direction="Increase",
                ico_budget_flag=True,
                enforcement_signal=0.78,
                source_url="https://www.gov.uk/government/publications/autumn-budget-2024",
                nlp_confidence=0.92,
                manually_reviewed=True,
            ),
            P3BudgetDocuments(
                budget_year=2024,
                budget_date=date(2024, 10, 30),
                item_type="AI Safety Spending",
                item_description="Funding for AI Safety Institute and frontier AI evaluation programmes",
                amount_gbp=100_000_000,
                yoy_change_pct=None,
                yoy_direction="New Item",
                ico_budget_flag=False,
                enforcement_signal=0.55,
                source_url="https://www.gov.uk/government/publications/autumn-budget-2024",
                nlp_confidence=0.87,
                manually_reviewed=True,
            ),
        ]

        # P4: Electoral Signals 
        p4_rows = [
            P4ElectoralSignals(
                record_date=date(2025, 3, 1),
                last_election_date=date(2024, 7, 4),
                next_election_due=date(2029, 8, 29),
                governing_party="Labour",
                governing_poll_ptc=38.2,
                opposition_poll_ptc=27.4,
                poll_source="YouGov/Times average",
                prediction_market_prob=0.72,
                gov_change_12m=0.08,
            ),
        ]

        # P5: Social Listening 
        p5_rows = [
            P5SocialListening(
                platform="X/Twitter",
                account_handle="@peterkyle_mp",
                account_name="Peter Kyle",
                account_category="Minister",
                party="Labour",
                party_power=True,
                post_date=datetime(2025, 2, 14, 10, 30, tzinfo=timezone.utc),
                post_id_platform="1760123456789",
                raw_text="The ICO is doing vital work keeping pace with AI. We're committed to giving them the tools they need to protect people's data rights in an AI-driven world.",
                processing_activities="Automated decision-making, data protection",
                topic_relevance_score=0.91,
                topic_tags="ico,ai,data_protection,enforcement",
                priority_level="Primary",
                regulatory_stance="Pro-enforcement",
                engagement_score=847,
                nlp_confidence=0.86,
                manually_reviewed=True,
            ),
            P5SocialListening(
                platform="X/Twitter",
                account_handle="@KemiBadenoch",
                account_name="Kemi Badenoch",
                account_category="Shadow Minister",
                party="Conservative",
                party_power=False,
                post_date=datetime(2025, 2, 10, 14, 15, tzinfo=timezone.utc),
                post_id_platform="1759987654321",
                raw_text="Labour's approach to AI regulation risks making the UK uncompetitive. We need smart rules, not a regulatory maze that drives investment overseas.",
                processing_activities="AI model training",
                topic_relevance_score=0.79,
                topic_tags="ai_regulation,competitiveness,deregulation",
                priority_level="Secondary",
                regulatory_stance="Deregulatory",
                engagement_score=1243,
                nlp_confidence=0.81,
                manually_reviewed=True,
            ),
        ]

        # P6: Parliamentary Q&A 
        p6_rows = [
            P6ParliamentaryQA(
                question_date=date(2025, 2, 3),
                answer_date=date(2025, 2, 10),
                question_type="Written",
                asking_mp="Caroline Nokes",
                asking_party="Conservative",
                asking_party_gov=False,
                answering_minister="Peter Kyle",
                answering_department="DSIT",
                answering_party="Labour",
                question_text="To ask the Secretary of State for Science, Innovation and Technology, what assessment he has made of the adequacy of the ICO's resources for regulating AI systems.",
                answer_text="The ICO has received increased resource allocation in the 2024 Autumn Budget specifically to strengthen its AI enforcement capabilities. We are working with the ICO to ensure it has the powers needed under the Data (Use and Access) Act.",
                processing_activities="Automated decision-making, AI model training",
                topic_tags="ico,ai,enforcement,resources",
                topic_relevance_score=0.94,
                priority_level="Primary",
                government_position="Supportive of Enforcement",
                ico_mentioned=True,
                enforcement_signal=0.81,
                source_url="https://questions-statements.parliament.uk/written-questions/detail/2025-02-03/12345",
                rss_guid="parliament.qa/written/2025-02-03/12345",
                nlp_confidence=0.90,
                manually_reviewed=True,
            ),
            P6ParliamentaryQA(
                question_date=date(2025, 1, 28),
                answer_date=date(2025, 2, 4),
                question_type="Written",
                asking_mp="Lord Clement-Jones",
                asking_party="Liberal Democrat",
                asking_party_gov=False,
                answering_minister="Baroness Jones",
                answering_department="DSIT",
                answering_party="Labour",
                question_text="To ask His Majesty's Government what steps they are taking to ensure algorithmic accountability in automated decision-making systems used in the public sector.",
                answer_text="The Government is committed to algorithmic transparency and is developing a framework for public sector use of automated decision-making, working closely with the ICO and the AI Safety Institute.",
                processing_activities="Automated decision-making, profiling",
                topic_tags="algorithmic_accountability,public_sector,automated_decision_making",
                topic_relevance_score=0.89,
                priority_level="Primary",
                government_position="Supportive of Enforcement",
                ico_mentioned=True,
                enforcement_signal=0.73,
                source_url="https://questions-statements.parliament.uk/written-questions/detail/2025-01-28/67890",
                rss_guid="parliament.qa/written/2025-01-28/67890",
                nlp_confidence=0.87,
                manually_reviewed=True,
            ),
        ]

        session.add_all(p1_rows + p2_rows + p3_rows + p4_rows + p5_rows + p6_rows)
        session.commit()
        print(f"✓ Inserted {len(p1_rows)} P1, {len(p2_rows)} P2, {len(p3_rows)} P3,")
        print(f"          {len(p4_rows)} P4, {len(p5_rows)} P5, {len(p6_rows)} P6 rows")

## Load demo data
load_demo_data()


## DataFrame helpers

def get_p1_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM p1_government_speeches ORDER BY speech_date DESC"), conn)
    df["speech_date"] = pd.to_datetime(df["speech_date"], errors="coerce").dt.date
    df["is_pro_enforcement"] = df["regulatory_stance"] == "Pro-enforcement"
    df["is_high_relevance"]  = df["topic_relevance_score"] >= 0.7
    return df


def get_p2_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM p2_party_manifestos ORDER BY election_year DESC"), conn)
    return df


def get_p3_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM p3_budget_documents ORDER BY budget_year DESC"), conn)
    df["budget_date"] = pd.to_datetime(df["budget_date"], errors="coerce").dt.date
    df["amount_gbp_millions"] = df["amount_gbp"].apply(
        lambda p: round(float(p) / 1_000_000, 3) if pd.notnull(p) else None
    )
    return df


def get_p4_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM p4_electoral_signals ORDER BY record_date DESC"), conn)
    for col in ["record_date", "last_election_date", "next_election_due"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    today = date.today()
    df["polling_gap"] = df["governing_poll_ptc"] - df["opposition_poll_ptc"]
    df["days_to_election"] = df["next_election_due"].apply(
        lambda d: (d - today).days if pd.notnull(d) else None
    )
    df["gov_change_likely"] = df["gov_change_12m"] > 0.5
    return df


def get_p5_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM p5_social_listening ORDER BY post_date DESC"), conn)
    df["is_governing_party"] = df["party_power"] == True
    df["is_high_reach"]      = df["engagement_score"] > 100
    return df


def get_p6_dataframe() -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM p6_parliamentary_qa ORDER BY question_date DESC"), conn)
    for col in ["question_date", "answer_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    df["days_to_answer"] = df.apply(
        lambda r: (r["answer_date"] - r["question_date"]).days
        if pd.notnull(r["answer_date"]) and pd.notnull(r["question_date"]) else None,
        axis=1
    )
    df["is_opposition_question"] = df["asking_party_gov"] == False
    return df


def get_political_summary() -> pd.DataFrame:
    """Aggregated enforcement signal by source type — feeds directly into scoring layer."""
    with engine.connect() as conn:
        df = pd.read_sql(text("""
            SELECT 'Speeches'    AS source, COUNT(*) AS count, AVG(enforcement_signal) AS avg_signal
            FROM p1_government_speeches WHERE topic_relevance_score >= 0.5
            UNION ALL
            SELECT 'Q&A'         AS source, COUNT(*) AS count, AVG(enforcement_signal) AS avg_signal
            FROM p6_parliamentary_qa WHERE topic_relevance_score >= 0.5
            UNION ALL
            SELECT 'Budget'      AS source, COUNT(*) AS count, AVG(enforcement_signal) AS avg_signal
            FROM p3_budget_documents
            UNION ALL
            SELECT 'Social'      AS source, COUNT(*) AS count, AVG(topic_relevance_score) AS avg_signal
            FROM p5_social_listening WHERE topic_relevance_score >= 0.5
            ORDER BY avg_signal DESC
        """), conn)
    return df


## Display Dataframes

p1_df = get_p1_dataframe()
print("\n── P1: Government Speeches ─────────────────────────────────────")
print(p1_df[[
    "title", "department", "speech_date", "regulatory_stance",
    "enforcement_signal", "ico_mentioned", "is_high_relevance"
]].to_string(index=False))

print("\n── P2: Party Manifestos ────────────────────────────────────────")
p2_df = get_p2_dataframe()
print(p2_df[[
    "party", "election_year", "obligation_direction",
    "priority_level", "governing_party"
]].to_string(index=False))

print("\n── P3: Budget Documents ────────────────────────────────────────")
p3_df = get_p3_dataframe()
print(p3_df[[
    "budget_year", "item_type", "amount_gbp_millions",
    "yoy_direction", "ico_budget_flag", "enforcement_signal"
]].to_string(index=False))

print("\n── P4: Electoral Signals ───────────────────────────────────────")
p4_df = get_p4_dataframe()
print(p4_df[[
    "record_date", "governing_party", "polling_gap",
    "prediction_market_prob", "gov_change_12m",
    "days_to_election", "gov_change_likely"
]].to_string(index=False))

print("\n── P5: Social Listening ────────────────────────────────────────")
p5_df = get_p5_dataframe()
print(p5_df[[
    "account_handle", "account_category", "party",
    "regulatory_stance", "engagement_score", "is_governing_party"
]].to_string(index=False))

print("\n── P6: Parliamentary Q&A ───────────────────────────────────────")
p6_df = get_p6_dataframe()
print(p6_df[[
    "asking_mp", "answering_department", "question_date",
    "government_position", "enforcement_signal", "ico_mentioned"
]].to_string(index=False))

print("\n── Political Summary (feeds scoring layer) ─────────────────────")
print(get_political_summary().to_string(index=False))
