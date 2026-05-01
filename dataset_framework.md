# Overall

## Structure

- Each component of the ERS has its own dataset/dataframe that then get fed into a dashboard/score calculator/etc
- Each component is made up of multiple tables depending on how many factors go into the component

# Legislative

- Two tables that are linked, one for each of the factors that determine the score
  - Bills in parliament, statutory instrument

## Table L1: Bills in Parliament

- One row per parliamentary event, a single bill has multiple rows as it passes through parliament
- Source: bills.parliament.uk

| **Field Name**        | **Variable Type** | **Description**                                                                               | **Example/Notes**                                                                                                                                                         |
| --------------------- | ----------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| bill_id               | UUID              | Primary key, unique per record                                                                | Auto-generated                                                                                                                                                            |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| parliament_bill_id    | VARCHAR           | ID from [bills.parliament.uk](http://bills.parliament.uk), used for deduplication and linking | e.g.'1234'                                                                                                                                                                |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| bill_type             | VARCHAR           | Classification of the bill                                                                    | Government, private members, hybrid                                                                                                                                       |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| bill_title            | VARCHAR           | Short title of bill/act                                                                       | Data (Use and Access) Bill                                                                                                                                                |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| session               | VARCHAR           | Parliamentary session                                                                         | 2024-2025                                                                                                                                                                 |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| event_type            | VARCHAR           | Parliamentary event being recorded                                                            | Introduced, first reading, second reading, committee stage, report stage, third reading, lords introduction, lords amendments, ping pong, royal assent, withdrawal, lapse |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| event_date            | DATE              | Date the event occurred                                                                       | 2026-03-14                                                                                                                                                                |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| house                 | VARCHAR           | House in which event occurred                                                                 | Commons, Lords, Both                                                                                                                                                      |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| bill_stage_numeric    | INTEGER           | Ordinal stage number for sequencing                                                           | Need to assign each event type a number                                                                                                                                   |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| bill_status           | VARCHAR           | Current overall status of bill                                                                | Active, passed, withdrawn, lapsed                                                                                                                                         |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| expected_commencement | DATE              | Anticipated commencement date if known                                                        | Nullable                                                                                                                                                                  |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| processing_activities | VARCHAR           | Processing activities/topic this bill materially affects                                      | Used to route score contributions                                                                                                                                         |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| relevance_score       | FLOAT             | 0-1 assigned relevance to topic                                                               | Need to figure out how to assign via NLP, probably need to get training data together                                                                                     |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| relevance_tag         | VARCHAR           | Array of topic tags                                                                           |                                                                                                                                                                           |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in relevance_score assignment                                         | Low confidence contribute less to score until manually reviewed                                                                                                           |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| obligation_direction  | VARCHAR           | Does this increase, decrease, or clarify obligations?                                         | Increased, decreases, clarifies, mixed                                                                                                                                    |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| affects_ico           | BOOLEAN           | Does the bill materially affect enforcement powers or budget of ICO?                          | TRUE/FALSE                                                                                                                                                                |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| source_url            | TEXT              | URL for this event on bills.parliament.uk                                                     |                                                                                                                                                                           |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| rss_guid              | VARCHAR           | Unique identifier from RSS feed entry for deduplication                                       |                                                                                                                                                                           |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| ingested_at           | TIMESTAMP         | When record is added to database                                                              |                                                                                                                                                                           |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields                                            | FALSE are included in scoring but weighted differently                                                                                                                    |
| ---                   | ---               | ---                                                                                           | ---                                                                                                                                                                       |

## Table L2: Statutory Instruments/Commencement Orders

- Statutory instruments/commencement orders are mechanisms by which Acts are implemented
- Single act can have multiple SI/COs, each get tracked separately
- Source: bills.parliament.uk

| **Field Name**        | **Variable Type** | **Description**                                                | **Example/Notes**                                                                     |
| --------------------- | ----------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| si_id                 | UUID              | Primary key                                                    | Auto-generated                                                                        |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| si_number             | VARCHAR           | Official SI Number                                             | SI 2025/412                                                                           |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| si_title              | VARCHAR           | Full title of the SI/CO                                        |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| si_type               | VARCHAR           | Classification                                                 | Commencement order, amendment SI, regulatory reform order                             |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| parent_act_id         | UUID              | Foreign key linking to Table 1 (parent act)                    |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| parent_act_name       | VARCHAR           | Name of parent act                                             |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| made_date             | DATE              | Date SI formally made                                          |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| laid_date             | DATE              | Date laid before Parliament                                    |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| force_date            | DATE              | Date provision takes effect, key enforcement trigger date      |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| provisions-commenced  | TEXT              | Sections or schedules of parent act brought into force         |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| si_status             | VARCHAR           | Current status                                                 | Made, in force, revoked, amended                                                      |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| processing_activities | VARCHAR           | Processing activities/topic referenced                         | Used to route score contributions                                                     |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| relevance_score       | FLOAT             | 0-1 assigned relevance to topic                                | Need to figure out how to assign via NLP, probably need to get training data together |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| relevance_tag         | VARCHAR           | Array of topic tags                                            |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in relevance_score assignment          | Low confidence contribute less to score until manually reviewed                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| obligation_type       | VARCHAR           | Nature of obligation created/activated                         | New duty, removal of exemption, new ICO power, penalty uplift                         |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| affects_ico           | BOOLEAN           | Does SI materially affect enforcement powers or budget of ICO? | TRUE/FALSE                                                                            |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| days_to_force         | INTEGER           | Computed: days between made_date and force_date                |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| source_url            | TEXT              | URL for this event on bills.parliament.uk                      |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| rss_guid              | VARCHAR           | Unique identifier from RSS feed entry for deduplication        |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| ingested_at           | TIMESTAMP         | When record is added to database                               |                                                                                       |
| ---                   | ---               | ---                                                            | ---                                                                                   |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields             | FALSE are included in scoring but weighted differently                                |
| ---                   | ---               | ---                                                            | ---                                                                                   |

# Political

- Six tables, one for each of the six sources that goes into the political score
  - Government speeches, party manifestos, budget documents, electoral signals, X/social listening, parliamentary Q&A
- These tables will require more NLP than the legislative set

## Table P1: Government Speeches

- This includes both government speeches and press releases, each row represents a single published speech or press release
- Primary departments: DSIT, Cabinet Office, Home Office
- Source: [gov.uk](http://gov.uk) site

| **Field Name**        | **Variable Type** | **Description**                                        | **Example/Notes**                                                                                                                          |
| --------------------- | ----------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| speech_id             | UUID              | Primary key, used for linking                          | Auto-generated                                                                                                                             |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| title                 | VARCHAR           | Title of speech or press release                       |                                                                                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| speaker_name          | VARCHAR           | Name of minister or official                           |                                                                                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| speaker_role          | VARCHAR           | Official role                                          | Secretary of State for Science, Innovation, and Technology                                                                                 |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| party                 | VARCHAR           | Political party of speaker                             |                                                                                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| department            | VARCHAR           | Originating government department                      | DSIT                                                                                                                                       |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| speech_date           | DATE              | Date of speech or publication                          |                                                                                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| speech_url            | TEXT              | [gov.uk](http://gov.uk) canonical URL                  |                                                                                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| rss_guid              | CARCHAR           | RSS feed GUID                                          |                                                                                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| topic_revelence_score | FLOAT             | 0-1 assigned relevance to topic                        | Need to figure out how to assign via NLP, probably need to get training data together                                                      |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| processing_activities | VARCHAR           | Processing activities/topic referenced                 | Used to route score contributions                                                                                                          |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| relevance_tag         | VARCHAR           | Array of topic tags                                    |                                                                                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| priority_level        | VARCHAR           | Is AI/data the primary, secondary, or periphery topic? | Primary, secondary, peripheral, none                                                                                                       |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| regulatory_stance     | VARCHAR           | Tone towards regulation in speech                      | Pro-enforcement, neutral, deregulatory, mixed<br><br>Need to figure out how to assign via NLP, probably need to get training data together |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| enforcement_signal    | FLOAT             | Composite signal for enforcement intent from this item | Need to figure out how to assign via NLP, probably need to get training data together                                                      |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in scored fields               | Low confidence contribute less to score until manually reviewed                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| ico_mentioned         | BOOLEAN           | Is the ICO mentioned?                                  | TRUE/FALSE                                                                                                                                 |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| ingested_at           | TIMESTAMP         | Pipeline ingestion timestamp                           |                                                                                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| raw_text              | TEXT              | Full text for NLP processing                           |                                                                                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields     | FALSE are included in scoring but weighted differently                                                                                     |
| ---                   | ---               | ---                                                    | ---                                                                                                                                        |

## Table P2: Party Manifestos

- Formal party manifesto commitments related to AI, data, digital regulation, one commitment per row
- Party manifestos only come out when there is an election coming up, the Manifesto Project has a good guide for analysing them
- Source: Manifesto Project, political party websites

| **Field Name**        | **Variable Type** | **Description**                                                 | **Example/Notes**                                               |
| --------------------- | ----------------- | --------------------------------------------------------------- | --------------------------------------------------------------- |
| manifesto_id          | UUID              | Primary key                                                     | Auto-generated                                                  |
| ---                   | ---               | ---                                                             | ---                                                             |
| party                 | VARCHAR           | Political party name                                            |                                                                 |
| ---                   | ---               | ---                                                             | ---                                                             |
| election_year         | INTEGER           | Year of election                                                |                                                                 |
| ---                   | ---               | ---                                                             | ---                                                             |
| commitment_text       | TEXT              | Relevant commitment                                             |                                                                 |
| ---                   | ---               | ---                                                             | ---                                                             |
| processing_activities | VARCHAR           | Processing activities/topic referenced                          | Used to route score contributions                               |
| ---                   | ---               | ---                                                             | ---                                                             |
| topic_tags            | VARCHAR           | NLP-detected topic tags                                         |                                                                 |
| ---                   | ---               | ---                                                             | ---                                                             |
| obligation_direction  | VARCHAR           | Does the commitment increase, decrease, or clarify obligations? | Increases, decreases, clarifies, mixed                          |
| ---                   | ---               | ---                                                             | ---                                                             |
| priority-level        | VARCHAR           | How prominently does this feature in the manifesto overall?     | Primary, secondary, peripheral                                  |
| ---                   | ---               | ---                                                             | ---                                                             |
| governing_party       | BOOLEAN           | Is this party currently in government?                          | TRUE/FALSE                                                      |
| ---                   | ---               | ---                                                             | ---                                                             |
| manifesto_project_id  | VARCHAR           | Manifesto Project record ID                                     | UK_2024_LAB_042                                                 |
| ---                   | ---               | ---                                                             | ---                                                             |
| source_url            | TEXT              | Link to full manifesto document                                 |                                                                 |
| ---                   | ---               | ---                                                             | ---                                                             |
| ingested_at           | TIMESTAMP         | Pipeline ingestion timestamp                                    |                                                                 |
| ---                   | ---               | ---                                                             | ---                                                             |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in scored fields                        | Low confidence contribute less to score until manually reviewed |
| ---                   | ---               | ---                                                             | ---                                                             |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields              | FALSE are included in scoring but weighted differently          |
| ---                   | ---               | ---                                                             | ---                                                             |

## Table P3: Budget Documents

- Captures data from annual UK budget, each row represents single budget line
- Source: [gov.uk](http://gov.uk) site

| **Field Name**     | **Variable Type** | **Description**                                        | **Example/Notes**                                                                     |
| ------------------ | ----------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| budget_id          | UUID              | Primary key                                            | Auto-generated                                                                        |
| ---                | ---               | ---                                                    | ---                                                                                   |
| budget_year        | INTEGER           | Financial year of the budget                           | 2025 (for FY 2025/26)                                                                 |
| ---                | ---               | ---                                                    | ---                                                                                   |
| budget_date        | DATE              | Date of the budget statement                           |                                                                                       |
| ---                | ---               | ---                                                    | ---                                                                                   |
| item_type          | VARCHAR           | Classification of budget line or commitment            | ICO allocation, tech regulation fund, AI safety spending, etc                         |
| ---                | ---               | ---                                                    | ---                                                                                   |
| item_description   | TEXT              | Description of specific line or commitment             |                                                                                       |
| ---                | ---               | ---                                                    | ---                                                                                   |
| amount_gbp         | NUMERIC           | GBP value of line item                                 |                                                                                       |
| ---                | ---               | ---                                                    | ---                                                                                   |
| yoy_change_pct     | FLOAT             | Year-on-year percentage change                         | Computed, can be null                                                                 |
| ---                | ---               | ---                                                    | ---                                                                                   |
| yoy_direction      | VARCHAR           | Direction of year-on-year change                       | Increase, decrease, flat, new item                                                    |
| ---                | ---               | ---                                                    | ---                                                                                   |
| ico_budget_flag    | BOOLEAN           | Is this the ICO'S core resource budget line?           | TRUE/FALSE                                                                            |
| ---                | ---               | ---                                                    | ---                                                                                   |
| enforcement_signal | FLOAT             | Composite signal for enforcement intent from this item | Need to figure out how to assign via NLP, probably need to get training data together |
| ---                | ---               | ---                                                    | ---                                                                                   |
| source_url         | TEXT              | Link to budget document or supplemental table          | URL                                                                                   |
| ---                | ---               | ---                                                    | ---                                                                                   |
| ingested_at        | TIMESTAMP         | Pipeline ingestion timestamp                           | Auto-generated                                                                        |
| ---                | ---               | ---                                                    | ---                                                                                   |
| nlp_confidence     | FLOAT             | NLP pipeline confidence in scored fields               | Low confidence contribute less to score until manually reviewed                       |
| ---                | ---               | ---                                                    | ---                                                                                   |
| manually_reviewed  | BOOLEAN           | FALSE until human has verified NLP-assigned fields     | FALSE are included in scoring but weighted differently                                |
| ---                | ---               | ---                                                    | ---                                                                                   |

## Table P4: Electoral Signals

- Used to estimate the probability of a change in government within 12 month window
  - If score is >.5, current government signals should be down-weighted to prevent over-indexing
- Need to set how often want to calculate this, should look at how often polls come out
- Source: Polling data (need to find best way to get them from polling companies)

| **Field Name**         | **Variable Type** | **Description**                                                                | **Example/Notes**                                                                               |
| ---------------------- | ----------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| electoral_id           | UUID              | Primary key                                                                    | Auto-generated                                                                                  |
| ---                    | ---               | ---                                                                            | ---                                                                                             |
| record_date            | DATE              | Date electoral snapshot is recorded                                            |                                                                                                 |
| ---                    | ---               | ---                                                                            | ---                                                                                             |
| last_election_date     | DATE              | Date of most recent general election                                           |                                                                                                 |
| ---                    | ---               | ---                                                                            | ---                                                                                             |
| next_election_due      | DATE              | Latest statutory date by which next election must be held                      | 2029-07-04                                                                                      |
| ---                    | ---               | ---                                                                            | ---                                                                                             |
| governing_party        | VARCHAR           | Currently governing party or coalition lead                                    |                                                                                                 |
| ---                    | ---               | ---                                                                            | ---                                                                                             |
| governing_poll_ptc     | FLOAT             | Average poll share for governing party                                         |                                                                                                 |
| ---                    | ---               | ---                                                                            | ---                                                                                             |
| opposition_poll_ptc    | FLOAT             | Average poll share for largest opposition party                                |                                                                                                 |
| ---                    | ---               | ---                                                                            | ---                                                                                             |
| poll_source            | VARCHAR           | Source of polling data                                                         |                                                                                                 |
| ---                    | ---               | ---                                                                            | ---                                                                                             |
| prediction_market_prob | FLOAT             | Prediction market probability of current governing party winning next election |                                                                                                 |
| ---                    | ---               | ---                                                                            | ---                                                                                             |
| gov_change_12m         | FLOAT             | Modelled probability of change in governing party in next 12 month             | Possible calculation: prediction_market_prob, gap in polling averages, time until next election |
| ---                    | ---               | ---                                                                            | ---                                                                                             |
| ingested_at            | TIMESTAMP         | Pipeline ingestion timestamp                                                   | Auto-generated                                                                                  |
| ---                    | ---               | ---                                                                            | ---                                                                                             |

## Table P5: X/Social Listening

- Captures posts from monitored X accounts, each row is single post
  - Should include prominent ministers, shadow spokespeople
- Source: Going to find a company for this

| **Field Name**        | **Variable Type** | **Description**                                          | **Example/Notes**                                                                                                                          |
| --------------------- | ----------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| social_id             | UUID              | Primary key                                              | Auto-generated                                                                                                                             |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| platform              | VARCHAR           | Source platform                                          | X/Twitter                                                                                                                                  |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| account_handle        | VARCHAR           | X handle of account                                      |                                                                                                                                            |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| account_name          | VARCHAR           | Display name of account                                  |                                                                                                                                            |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| account_category      | VARCHAR           | Category of monitored account                            | Minister, shadow minister, MP, aide, etc                                                                                                   |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| party                 | VARCHAR           | Political party of account holder                        |                                                                                                                                            |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| party_power           | BOOLEAN           | Is the account holder's party currently in government?   | TRUE/FALSE                                                                                                                                 |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| post_date             | TIMESTAMP         | Date and time of the post                                |                                                                                                                                            |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| post_id_platform      | VARCHAR           | Native post ID from X                                    |                                                                                                                                            |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| raw_text              | TEXT              | Full text as received                                    |                                                                                                                                            |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| processing_activities | VARCHAR           | Processing activities/topic referenced                   | Used to route score contributions                                                                                                          |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| topic_relevence_score | FLOAT             | Relevance to topic (0-1)                                 | Need to figure out how to assign via NLP, probably need to get training data                                                               |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| topic_tags            | VARCHAR           | NLP-detected topic tags                                  |                                                                                                                                            |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| priority-level        | VARCHAR           | How prominently does topic feature in post               | Primary, secondary, peripheral                                                                                                             |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| regulatory_stance     | VARCHAR           | Tone towards regulation in post                          | Pro-enforcement, neutral, deregulatory, mixed<br><br>Need to figure out how to assign via NLP, probably need to get training data together |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| engagement_score      | INTEGER           | Likes and reposts at time of ingestion (proxy for reach) |                                                                                                                                            |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| ingested_at           | TIMESTAMP         | Pipeline ingestion timestamp                             | Auto-generated                                                                                                                             |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in scored fields                 | Low confidence contribute less to score until manually reviewed                                                                            |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields       | FALSE are included in scoring but weighted differently                                                                                     |
| ---                   | ---               | ---                                                      | ---                                                                                                                                        |

## Table P6: Parliamentary Q&A

- Each row represents single question and answer pair
- Source: questions-statements.parliament.uk

| **Field Name**        | **Variable Type** | **Description**                                             | **Example/Notes**                                                                     |
| --------------------- | ----------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| pqa_id                | UUID              | Primary key                                                 | Auto-generated                                                                        |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| question_date         | DATE              | Date the question was tabled                                |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| answer_date           | DATE              | Date the answer is published                                |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| question_type         | VARCHAR           | Type of parliamentary question                              | Written, oral, urgent                                                                 |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| asking_MP             | VARCHAR           | Name of MP who asked the question                           |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| asking_party          | VARCHAR           | Party of asking MP                                          |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| asking_party_gov      | BOOLEAN           | Is the party of the asking MP the current governing party?  | TRUE/FALSE                                                                            |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| answering_minister    | VARCHAR           | Minister who provided the answer                            |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| answering_department  | VARCHAR           | Department of the answering minister                        |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| answering_party       | VARCHAR           | Party of the answering minister                             |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| question_text         | TEXT              | Full text of question                                       |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| answer_text           | TEXT              | Full text of answer                                         |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| processing_activities | VARCHAR           | Processing activities/topic referenced                      | Used to route score contributions                                                     |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| topic_tags            | VARCHAR           | NLP-detected topic tags                                     |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| topic_relevance_score | FLOAT             | Relevance to AI/topic (0-1)                                 | Need to figure out how to assign via NLP, probably need to get training data together |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| priority_level        | VARCHAR           | Topic prominence                                            | Primary, secondary, peripheral                                                        |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| government_position   | VARCHAR           | Government's stated position on enforcement based on answer | Supportive of enforcement, neutral, resident, unclear                                 |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| ico_mentioned         | BOOLEAN           | Is the ICO explicitly mentioned?                            | TRUE/FALSE                                                                            |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| enforcement_signal    | FLOAT             | Composite NLP signal for enforcement intent                 |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| source_url            | TEXT              | Source url from official government website                 |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| rss_guid              | VARCHAR           | RSS feed GUID for deduplication                             |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| ingested_at           | TIMESTAMP         | Pipeline ingestion timestamp                                |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in scored fields                    | Low confidence contribute less to score until manually reviewed                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields          | FALSE are included in scoring but weighted differently                                |
| ---                   | ---               | ---                                                         | ---                                                                                   |

# Regulatory

- Focus of these tables is the ICO as it is the main regulator for AI/digital technology in the UK government
  - There are two tables about other regulators that could be important

## Table R1: Enforcement register

- Each row is one enforcement action or regulatory outcome
- Source: ICO website

| **Field Name**           | **Variable Type** | **Description**                                             | **Example/Notes**                                                                                                                                                                      |
| ------------------------ | ----------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| enforcement_id           | UUID              | Primary key                                                 | Auto-generated                                                                                                                                                                         |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| ico_reference            | VARCHAR           | ICO's own reference number                                  |                                                                                                                                                                                        |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| org_name                 | VARCHAR           | Name of organization subject to action                      |                                                                                                                                                                                        |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| org_type                 | VARCHAR           | Sector/type classification of organization                  | Examples: AI start-up, large tech, financial services, etc                                                                                                                             |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| org_size                 | VARCHAR           | Size band of organization                                   | Micro (<10), Small (10-49), Medium (50-249), Large (250+)                                                                                                                              |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| action_date              | DATE              | Date the enforcement action was issued/published            |                                                                                                                                                                                        |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| action_type              | VARCHAR           | Type of enforcement action taken                            | Monetary penalty notice (fine); enforcement notice; information notice; assessment notice (audit); undertaking; reprimand; warning; prosecution; stop processing order; advisory visit |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| outcome                  | VARCHAR           | Result of action                                            | Upheld; overturned on appeal; settled; withdrawn                                                                                                                                       |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| penalty_gbp              | NUMERIC           | Fine amount in GBP if applicable                            |                                                                                                                                                                                        |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| penalty_as_max           | FLOAT             | Penalty as percentage of maximum possible fine              | Computed                                                                                                                                                                               |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| severity_tier            | VARCHAR           | Banded severity                                             | Critical, high, medium, low, advisory                                                                                                                                                  |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| aggravating_factors      | VARCHAR           | Factors that increased severity (if applicable)             | Repeated breach, deliberate, large-scale, etc                                                                                                                                          |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| mitigating_factors       | VARCHAR           | Factors that reduced severity (if applicable)               | Self-reported, remediation_taken, etc                                                                                                                                                  |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| appealed                 | BOOLEAN           | Was the action appealed to the Information Rights Tribunal? | TRUE/FALSE                                                                                                                                                                             |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| appeal_outcome           | VARCHAR           | Result of appeal (if applicable)                            | Upheld, reduced, overturned                                                                                                                                                            |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| processing_activities    | VARCHAR           | Processing activities/topic referenced                      | Used to route score contributions                                                                                                                                                      |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| legislation_breached     | VARCHAR           | Specific legislation or articles cited                      |                                                                                                                                                                                        |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| gdpr_principles          | VARCHAR           | GDPR data protection principles engaged                     |                                                                                                                                                                                        |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| special_category_data    | BOOLEAN           | Did the breach involve special category data?               | TRUE/FALSE                                                                                                                                                                             |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| cross_border             | BOOLEAN           | Did the action involve international data transfers?        | TRUE/FALSE                                                                                                                                                                             |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| ai_specific              | BOOLEAN           | Was AI or automated processing central to the breach?       | TRUE/FALSE                                                                                                                                                                             |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| prior_ico_contact        | BOOLEAN           | Has this organization had prior ICO contact of any type?    | TRUE/FALSE                                                                                                                                                                             |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| prior_contact_types      | VARCHAR           | Types of prior contact                                      |                                                                                                                                                                                        |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| prior_contact_count      | INTEGER           | Number of prior contacts                                    |                                                                                                                                                                                        |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| days_prior_contact       | INTEGER           | Days since most recent prior contact                        | Computed                                                                                                                                                                               |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| org_type_recidivism_rate | FLOAT             | Historical enforcement rate for this org_type               | Computed (need to determine formula)                                                                                                                                                   |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| source_url               | TEXT              | ICO enforcement register URL                                |                                                                                                                                                                                        |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| ingested_at              | TIMESTAMP         | Pipeline ingestion timestamp                                | Auto-generated                                                                                                                                                                         |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| raw_summary              | TEXT              | Full summary text from ICO register                         |                                                                                                                                                                                        |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| nlp_confidence           | FLOAT             | NLP pipeline confidence in scored fields                    | Low confidence contribute less to score until manually reviewed                                                                                                                        |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |
| manually_reviewed        | BOOLEAN           | FALSE until human has verified NLP-assigned fields          | FALSE are included in scoring but weighted differently                                                                                                                                 |
| ---                      | ---               | ---                                                         | ---                                                                                                                                                                                    |

## Table R2: ICO News and Blog

- Each row of the table is a news item or blog from the ICO
- Source: ICO website

| **Field Name**        | **Variable Type** | **Description**                                            | **Example/Notes**                                                                     |
| --------------------- | ----------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| news_id               | UUID              | Primary key                                                | Auto-generated                                                                        |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| title                 | VARCHAR           | Title of news item or blog post                            |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| publication_date      | DATE              | Date published                                             |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| content_type          | VARCHAR           | Type of publication                                        | News; blog; press release; statement; investigation announcement                      |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| processing_activities | VARCHAR           | Processing activities/topic referenced                     | Used to route score contributions                                                     |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| topic_tags            | VARCHAR           | NLP-detected topic tags                                    |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| topic_relevance_score | FLOAT             | Relevance to AI/topic (0-1)                                | Need to figure out how to assign via NLP, probably need to get training data together |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| signal_investigation  | BOOLEAN           | Does this item signal an active or imminent investigation? | TRUE/FALSE                                                                            |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| signal_consultation   | BOOLEAN           | Does this item signal an upcoming or active consultation?  | TRUE/FALSE                                                                            |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| enforcement_signal    | FLOAT             | Composite NLP enforcement intent score                     | 0.0-1.0                                                                               |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| source_url            | TEXT              | ICO canonical URL                                          |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| rss_guid              | VARCHAR           | RSS feed GUID                                              |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| raw_text              | TEXT              | Full article for NLP processing                            |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| ingested_at           | TIMESTAMP         | Pipeline ingestion timestamp                               | Auto-generated                                                                        |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in scored fields                   | Low confidence contribute less to score until manually reviewed                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields         | FALSE are included in scoring but weighted differently                                |
| ---                   | ---               | ---                                                        | ---                                                                                   |

## Table R3: ICO Consultation and Guidance

- Each row is one document/step in a consultation
- Source: ICO website

| **Field Name**        | **Variable Type** | **Description**                                            | **Example/Notes**                                                                     |
| --------------------- | ----------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| consultation_id       | UUID              | Primary key                                                | Auto-generated                                                                        |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| title                 | VARCHAR           | Full title of document                                     |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| publication_date      | DATE              | Date published or date consultation opened                 |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| document_type         | VARCHAR           | Classification of the document                             | Consultation; guidance; audit framework; call for evidence; opinion; code of practice |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| consultation_status   | VARCHAR           | Current status                                             | Open; open; closed; response published; finalized                                     |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| consultation_closes   | DATE              | Deadline for responses if open                             | Nullable                                                                              |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| processing_activities | VARCHAR           | Processing activities/topic referenced                     | Used to route score contributions                                                     |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| topic_tags            | VARCHAR           | NLP-detected topic tags                                    |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| topic_relevance_score | FLOAT             | Relevance to AI/topic (0-1)                                | Need to figure out how to assign via NLP, probably need to get training data together |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| obligation_direction  | VARCHAR           | Does this tighten, relax, or clarify obligations?          | Tightens, relaxes, clarifies, mixed                                                   |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| enforcement_signal    | FLOAT             | Composite NLP enforcement intent score                     | 0.0-1.0                                                                               |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| follows_enforcement   | BOOLEAN           | Does this consultation follow a recent enforcement action? | TRUE/FALSE                                                                            |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| source_url            | TEXT              | ICO canonical URL                                          |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| rss_guid              | VARCHAR           | RSS feed GUID                                              |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| raw_text              | TEXT              | Full article for NLP processing                            |                                                                                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| ingested_at           | TIMESTAMP         | Pipeline ingestion timestamp                               | Auto-generated                                                                        |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in scored fields                   | Low confidence contribute less to score until manually reviewed                       |
| ---                   | ---               | ---                                                        | ---                                                                                   |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields         | FALSE are included in scoring but weighted differently                                |
| ---                   | ---               | ---                                                        | ---                                                                                   |

## Table R4: Secondary regulators

- Each row is one action from the set of secondary regulatory
  - Competition and Markets Authority; Ofcom; Financial Conduct Authority; AI Safety Institute
- Source: Websites of secondary regulators

| **Field Name**        | **Variable Type** | **Description**                                        | **Example/Notes**                                                                     |
| --------------------- | ----------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| secondary-id          | UUID              | Primary key                                            | Auto-generated                                                                        |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| regulator             | VARCHAR           | Name of secondary regulator                            |                                                                                       |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| action_date           | DATE              | Date of action or publication                          |                                                                                       |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| action_type           | VARCHAR           | Type of action                                         | Enforcement; investigation; guidance; market study; statement                         |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| org_name              | VARCHAR           | Organization subject to action                         | If applicable                                                                         |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| org_type              | VARCHAR           | Sector classification                                  | AI start-up, large tech, etc                                                          |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| topic_tags            | VARCHAR           | NLP-detected topic tags                                |                                                                                       |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| processing_activities | VARCHAR           | Processing activities/topic referenced                 | Used to route score contributions                                                     |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| topic_relevance_score | FLOAT             | Relevance to AI/topic (0-1)                            | Need to figure out how to assign via NLP, probably need to get training data together |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| cross_regulator_flag  | BOOLEAN           | Does this action explicitly reference/involve the ICO? | TRUE/FALSE                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| ico_referral          | BOOLEN            | Has the regulator referred this matter to the ICO?     | TRUE/FALSE                                                                            |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| enforcement_signal    | FLOAT             | Composite NLP enforcement intent score                 | 0.0-1.0                                                                               |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| source_url            | TEXT              | ICO canonical URL                                      |                                                                                       |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| ingested_at           | TIMESTAMP         | Pipeline ingestion timestamp                           | Auto-generated                                                                        |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in scored fields               | Low confidence contribute less to score until manually reviewed                       |
| ---                   | ---               | ---                                                    | ---                                                                                   |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields     | FALSE are included in scoring but weighted differently                                |
| ---                   | ---               | ---                                                    | ---                                                                                   |

## Table R5: EU/International bodies

- Each row is one action from an international regulator
  - European Data Protection Board; Irish Data Protection Commission; French CNIL; German BfDI; Spanish AEPD
- Source: Websites of international regulators

| **Field Name**        | **Variable Type** | **Description**                                             | **Example/Notes**                                                                     |
| --------------------- | ----------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| international_id      | UUID              | Primary key                                                 | Auto-generated                                                                        |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| body                  | VARCHAR           | Issuing regulatory body                                     |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| jurisdiction          | VARCHAR           | Country or supranational body                               |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| action_date           | DATE              | Date of decision or action                                  |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| action_type           | VARCHAR           | Type of action                                              | Enforcement decision, binding opinion, guideline, joint investigation                 |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| org_name              | VARCHAR           | Organization subject to action                              | If applicable                                                                         |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| org_type              | VARCHAR           | Sector classification                                       | AI start-up, large tech, etc                                                          |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| penalty_eur           | NUMERIC           | Fine amount in EUR                                          | If applicable                                                                         |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| processing_activities | VARCHAR           | Processing activities/topic referenced                      | Used to route score contributions                                                     |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| topic_tags            | VARCHAR           | NLP-detected topic tags                                     |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| topic_relevance_score | FLOAT             | Relevance to AI/topic (0-1)                                 | Need to figure out how to assign via NLP, probably need to get training data together |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| uk_company_involved   | BOOLEAN           | Does the action involve a company also operating in the UK? | TRUE/FALSE                                                                            |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| gdpr_articles         | VARCHAR           | EU GDPR articles engaged (maps to equivalent UK GDPR)       |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| ico_signal_strength   | FLOAT             | Estimated probability this leads to ICO follow-up           | 0.0-1.0                                                                               |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| source_url            | TEXT              | ICO canonical URL                                           |                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| ingested_at           | TIMESTAMP         | Pipeline ingestion timestamp                                | Auto-generated                                                                        |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in scored fields                    | Low confidence contribute less to score until manually reviewed                       |
| ---                   | ---               | ---                                                         | ---                                                                                   |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields          | FALSE are included in scoring but weighted differently                                |
| ---                   | ---               | ---                                                         | ---                                                                                   |

## Table R6: DRCF

- Each row is one publication/statement from the Digital Regulation Cooperation Forum
- Source: DRCF website

| **Field Name**          | **Variable Type** | **Description**                                                    | **Example/Notes**                                                                     |
| ----------------------- | ----------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| drcf_id                 | UUID              | Primary key                                                        | Auto-generated                                                                        |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| publication_date        | DATE              | Date published                                                     |                                                                                       |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| document_type           | VARCHAR           | Type of DRCF publication                                           | Joint statement; work programme; report; consultation response                        |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| participating_bodies    | VARCHAR           | Regulators involved in this publication                            |                                                                                       |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| title                   | VARCHAR           | Title of the publication                                           |                                                                                       |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| processing_activities   | VARCHAR           | Processing activities/topic referenced                             | Used to route score contributions                                                     |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| topic_tags              | VARCHAR           | NLP-detected topic tags                                            |                                                                                       |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| topic_relevance_score   | FLOAT             | Relevance to AI/topic (0-1)                                        | Need to figure out how to assign via NLP, probably need to get training data together |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| ico_lead                | BOOLEAN           | Is the ICO the lead body for this publication?                     | TRUE/FALSE                                                                            |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| enforcement_signal      | FLOAT             | Composite NLP enforcement intent score                             | 0.0-1.0                                                                               |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| coordinated_action-flag | BOOLEAN           | Does this signal coordinated enforcement action across regulators? | TRUE.FALSE                                                                            |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| source_url              | TEXT              | ICO canonical URL                                                  |                                                                                       |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| ingested_at             | TIMESTAMP         | Pipeline ingestion timestamp                                       | Auto-generated                                                                        |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| nlp_confidence          | FLOAT             | NLP pipeline confidence in scored fields                           | Low confidence contribute less to score until manually reviewed                       |
| ---                     | ---               | ---                                                                | ---                                                                                   |
| manually_reviewed       | BOOLEAN           | FALSE until human has verified NLP-assigned fields                 | FALSE are included in scoring but weighted differently                                |
| ---                     | ---               | ---                                                                | ---                                                                                   |

# Judicial

- Four tables, each for one court/court-level within the UK

## Table J1: UK Supreme Court

- Each row is one case/decision of the UK Supreme Court
- Source: UK Supreme Court website

| **Field Name**              | **Variable Type** | **Description**                                      | **Example/Notes**                                               |
| --------------------------- | ----------------- | ---------------------------------------------------- | --------------------------------------------------------------- |
| supreme_id                  | UUID              | Primary key                                          | Auto-generated                                                  |
| ---                         | ---               | ---                                                  | ---                                                             |
| case_name                   | VARCHAR           | Standard case citation name                          |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| neautral_citation           | VARCHAR           | Neutral citation reference                           |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| decision_date               | DATE              | Date judgement handed down                           |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| subject_matter              | VARCHAR           | Primary legal subject of the case                    | Data protection; privacy, AI liability; freedom of information  |
| ---                         | ---               | ---                                                  | ---                                                             |
| case_url                    | TEXT              | Canonical URL                                        |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| ingested_at                 | TIMESTAMP         | Pipeline ingestion timestamp                         |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| appellant                   | VARCHAR           | Appellant party name                                 |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| respondent                  | VARCHAR           | Respondent party name                                |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| appellant_type              | VARHCAR           | Classification of appellant                          | Data subject; controller; processor; regulator; government      |
| ---                         | ---               | ---                                                  | ---                                                             |
| respondent_type             | VARCHAR           | Classification of respondent                         | Data subject; controller; processor; regulator; government      |
| ---                         | ---               | ---                                                  | ---                                                             |
| ico_role                    | VARCHAR           | ICO's involvement in the case                        | Party (appellant); party (respondent); intervener; amicus; none |
| ---                         | ---               | ---                                                  | ---                                                             |
| ico_position_upheld         | BOOLEAN           | Was the ICO's position upheld by the court?          | TRUE/FALSE (if applicable)                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| outcome_direction           | VARCHAR           | Who did the outcome favour?                          | Controller; data subject; ICO; mixed; procedural                |
| ---                         | ---               | ---                                                  | ---                                                             |
| outcome_summary             | TEXT              | Plain-English summary                                |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| precedent_weight            | VARCHAR           | Binding force of this decision                       |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| processing_activities       | VARCHAR           | Processing activities/topic referenced               | Used to route score contributions                               |
| ---                         | ---               | ---                                                  | ---                                                             |
| gdpr_articles               | VARCHAR           | UK GDPR articles directly engaged                    |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| gdpr_principles             | VARHCAR           | Data protection principles at issue                  |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| damages_awarded             | BOOLEAN           | Were damages awarded to a data subject?              | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| damages_amount              | NUMERIC           | Damages amount if awarded                            |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| ai_specific                 | BOOLEAN           | Is AI or automated processing central to the ruling? | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| widens_controller_liability | BOOLEAN           | Does this ruling expand controller liability?        | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| restrict_ico_powers         | BOOLEAN           | Does this ruling restrict ICO enforcement powers?    | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| enforcement_signal          | FLOAT             | Composite enforcement signal                         | 0.0-1.0                                                         |
| ---                         | ---               | ---                                                  | ---                                                             |
| nlp_confidence              | FLOAT             | NLP pipeline confidence in scored fields             | Low confidence contribute less to score until manually reviewed |
| ---                         | ---               | ---                                                  | ---                                                             |
| manually_reviewed           | BOOLEAN           | FALSE until human has verified NLP-assigned fields   | FALSE are included in scoring but weighted differently          |
| ---                         | ---               | ---                                                  | ---                                                             |

## Table J2: Court of Appeal

- Source: National Archives

| **Field Name**              | **Variable Type** | **Description**                                      | **Example/Notes**                                               |
| --------------------------- | ----------------- | ---------------------------------------------------- | --------------------------------------------------------------- |
| appeal_id                   | UUID              | Primary key                                          | Auto-generated                                                  |
| ---                         | ---               | ---                                                  | ---                                                             |
| case_name                   | VARCHAR           | Standard case citation name                          |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| neutral_citation            | VARCHAR           | Neutral citation                                     |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| decision_date               | DATE              | Date judgement handed down                           |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| division                    | VARCHAR           | Court of Appeal division                             | Civil or criminal                                               |
| ---                         | ---               | ---                                                  | ---                                                             |
| subject_matter              | VARCHAR           | Primary legal subject                                |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| appellant_type              | VARHCAR           | Classification of appellant                          | Data subject; controller; processor; regulator; government      |
| ---                         | ---               | ---                                                  | ---                                                             |
| respondent_type             | VARCHAR           | Classification of respondent                         | Data subject; controller; processor; regulator; government      |
| ---                         | ---               | ---                                                  | ---                                                             |
| ico_role                    | VARCHAR           | ICO's involvement in the case                        | Party (appellant); party (respondent); intervener; amicus; none |
| ---                         | ---               | ---                                                  | ---                                                             |
| ico_position_upheld         | BOOLEAN           | Was the ICO's position upheld by the court?          | TRUE/FALSE (if applicable)                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| outcome_direction           | VARCHAR           | Who did the outcome favour?                          | Controller; data subject; ICO; mixed; procedural                |
| ---                         | ---               | ---                                                  | ---                                                             |
| outcome_summary             | TEXT              | Plain-English summary                                |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| precedent_weight            | VARCHAR           | Binding force                                        |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| processing_activities       | VARCHAR           | Processing activities/topic referenced               | Used to route score contributions                               |
| ---                         | ---               | ---                                                  | ---                                                             |
| gdpr_articles               | VARCHAR           | UK GDPR articles directly engaged                    |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| gdpr_principles             | VARHCAR           | Data protection principles at issue                  |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| damages_awarded             | BOOLEAN           | Were damages awarded to a data subject?              | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| damages_amount              | NUMERIC           | Damages amount if awarded                            |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| ai_specific                 | BOOLEAN           | Is AI or automated processing central to the ruling? | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| widens_controller_liability | BOOLEAN           | Does this ruling expand controller liability?        | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| restrict_ico_powers         | BOOLEAN           | Does this ruling restrict ICO enforcement powers?    | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| enforcement_signal          | FLOAT             | Composite enforcement signal                         | 0.0-1.0                                                         |
| ---                         | ---               | ---                                                  | ---                                                             |
| case_url                    | TEXT              | URl from National Archives                           |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| ingested_at                 | TIMESTAMP         | Pipeline ingestion timestamp                         | Auto-generated                                                  |
| ---                         | ---               | ---                                                  | ---                                                             |
| nlp_confidence              | FLOAT             | NLP pipeline confidence in scored fields             | Low confidence contribute less to score until manually reviewed |
| ---                         | ---               | ---                                                  | ---                                                             |
| manually_reviewed           | BOOLEAN           | FALSE until human has verified NLP-assigned fields   | FALSE are included in scoring but weighted differently          |
| ---                         | ---               | ---                                                  | ---                                                             |

## Table J3: Information Rights Tribunal

- Most important court decisions and highest volume
- Source: National Archives

| **Field Name**        | **Variable Type** | **Description**                                      | **Example/Notes**                                                                                         |
| --------------------- | ----------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| tribunal_id           | UUID              | Primary key                                          | Auto-generated                                                                                            |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| case_reference        | VARCHAR           | Tribunal case reference                              |                                                                                                           |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| tier                  | VARCHAR           | Tribunal tier                                        | First-tier; upper tribunal                                                                                |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| decision_date         | DATE              | Date decision published                              |                                                                                                           |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| case_type             | VARCHAR           | Type of tribunal case                                | Enforcement notice appeal; monetary penalty appeal; information notice appeal; data subject rights appeal |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| appellant_type        | VARCHAR           | Classification of appellant                          | Controller; processor; data subject; ICO                                                                  |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| ico_role              | VARCHAR           | ICO involvement                                      | Respondent; appellant; none                                                                               |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| ico_position_upheld   | BOOLEAN           | Was the ICO's enforcement position upheld?           | TRUE/FALSE                                                                                                |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| outcome_direction     | VARCHAR           | Who did the outcome favor?                           | Controller; data subject; ICO; mixed; procedural                                                          |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| original_penalty_gdp  | NUMERIC           | Original ICO Penalty under appeal                    |                                                                                                           |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| revised_penalty_gdp   | NUMERIC           | Revised penalty under tribunal                       |                                                                                                           |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| penalty_reduction_pct | FLOAT             | Percentage reduction in penalty                      | Computed                                                                                                  |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| appeals_ground        | VARCHAR           | Legal grounds on which appeal was brought            |                                                                                                           |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| processing_activities | VARCHAR           | Processing activities/topic referenced               | Used to route score contributions                                                                         |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| gdpr_articles         | VARCHAR           | UK GDPR articles engaged                             |                                                                                                           |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| ai_specific           | BOOLEAN           | Is AI or automated processing central to the ruling? | TRUE/FALSE                                                                                                |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| precedent_weight      | VARCHAR           | Binding force                                        |                                                                                                           |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| enforcement_signal    | FLOAT             | Composite enforcement signal                         | 0.0-1.0                                                                                                   |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| case_url              | TEXT              | URl from National Archives                           |                                                                                                           |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| ingested_at           | TIMESTAMP         | Pipeline ingestion timestamp                         | Auto-generated                                                                                            |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in scored fields             | Low confidence contribute less to score until manually reviewed                                           |
| ---                   | ---               | ---                                                  | ---                                                                                                       |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields   | FALSE are included in scoring but weighted differently                                                    |
| ---                   | ---               | ---                                                  | ---                                                                                                       |

## Table J4: High Court

- Source: National Archives

| **Field Name**              | **Variable Type** | **Description**                                      | **Example/Notes**                                               |
| --------------------------- | ----------------- | ---------------------------------------------------- | --------------------------------------------------------------- |
| highcourt_id                | UUID              | Primary key                                          | Auto-generated                                                  |
| ---                         | ---               | ---                                                  | ---                                                             |
| case_name                   | VARCHAR           | Standard case citation                               |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| neutral_citation            | VARCHAR           | Neutral citation                                     |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| decision_date               | DATE              | Date judgement handed down                           |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| division                    | VARCHAR           | High Court division                                  | King's Bench; Chancery; Queen's Bench                           |
| ---                         | ---               | ---                                                  | ---                                                             |
| case_type                   | VARCHAR           | Nature of proceedings                                | Judicial review; civil damages claim; injunction; declaration   |
| ---                         | ---               | ---                                                  | ---                                                             |
| ico_role                    | VARCHAR           | ICO involvement                                      | Defendant; party; intervener; none                              |
| ---                         | ---               | ---                                                  | ---                                                             |
| ico_position_upheld         | BOOLEAN           | ICO position upheld?                                 | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| jr_permission_granted       | BOOLEAN           | Was JR permission granted?                           | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| outcome_direction           | VARCHAR           | Who did the outcome favour?                          | Controller; data subject; ICO; mixed; procedural                |
| ---                         | ---               | ---                                                  | ---                                                             |
| outcome_summary             | TEXT              | Plain-English summary                                |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| precedent_weight            | VARCHAR           | Binding force                                        |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| processing_activities       | VARCHAR           | Processing activities/topic referenced               | Used to route score contributions                               |
| ---                         | ---               | ---                                                  | ---                                                             |
| gdpr_articles               | VARCHAR           | UK GDPR articles directly engaged                    |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| gdpr_principles             | VARHCAR           | Data protection principles at issue                  |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| damages_awarded             | BOOLEAN           | Were damages awarded to a data subject?              | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| damages_amount              | NUMERIC           | Damages amount if awarded                            |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| ai_specific                 | BOOLEAN           | Is AI or automated processing central to the ruling? | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| widens_controller_liability | BOOLEAN           | Does this ruling expand controller liability?        | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| restrict_ico_powers         | BOOLEAN           | Does this ruling restrict ICO enforcement powers?    | TRUE/FALSE                                                      |
| ---                         | ---               | ---                                                  | ---                                                             |
| enforcement_signal          | FLOAT             | Composite enforcement signal                         | 0.0-1.0                                                         |
| ---                         | ---               | ---                                                  | ---                                                             |
| case_url                    | TEXT              | URl from National Archives                           |                                                                 |
| ---                         | ---               | ---                                                  | ---                                                             |
| ingested_at                 | TIMESTAMP         | Pipeline ingestion timestamp                         | Auto-generated                                                  |
| ---                         | ---               | ---                                                  | ---                                                             |
| nlp_confidence              | FLOAT             | NLP pipeline confidence in scored fields             | Low confidence contribute less to score until manually reviewed |
| ---                         | ---               | ---                                                  | ---                                                             |
| manually_reviewed           | BOOLEAN           | FALSE until human has verified NLP-assigned fields   | FALSE are included in scoring but weighted differently          |
| ---                         | ---               | ---                                                  | ---                                                             |

# Media and Civil Society

- 13 NGOs determined to be most important for AI
  - Big Brother Watch; Privacy International; Open Rights Group; Liberty; Foxglove; Connected by Data; MedConfidential; Ada Lovelace Institute; Alan Turing Institute; EDRi; the Future Society; AI Whistleblower Initiative; European AI and Society Fund

## Table M1: Media NGO Activity

- Tracks publication, press releases, etc from civil society organizations
- Source: Websites of NGOs

| **Field Name**        | **Variable Type** | **Description**                                            | **Example/Notes**                                                                                                                          |
| --------------------- | ----------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| ngo_activity_id       | UUID              | Primary key                                                | Auto-generated                                                                                                                             |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| ngo_name              | TEXT              | Organization name                                          |                                                                                                                                            |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| publication_date      | DATE              | Date of publication or complaint filing                    |                                                                                                                                            |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| activity_type         | VARCHAR           | Type of activity recorded                                  | Publication; press release; formal complaint; legal challenge; parliamentary submission                                                    |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| title                 | TEXT              | Title or headline of the publication/action                |                                                                                                                                            |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| source_url            | TEXT              | Source url                                                 |                                                                                                                                            |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| target_org            | VARCHAR           | Company or sector named as subject                         |                                                                                                                                            |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| ico_named             | BOOLEAN           | Is the ICO explicitly called on to act?                    | TRUE/FALSE                                                                                                                                 |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| formal_complaint      | BOOLEAN           | Is this/does this accompany a formal ICO complaint filing? | TRUE/FALSE                                                                                                                                 |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| complaint_ref         | VARCHAR           | ICO complaint reference number                             | If applicable                                                                                                                              |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| legal_action          | BOOLEAN           | Is legal action threatened or initiated?                   | TRUE/FALSE                                                                                                                                 |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| content_summary       | TEXT              | Content summary                                            |                                                                                                                                            |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| processing_activities | VARCHAR           | Processing activities/topic referenced                     | Used to route score contributions                                                                                                          |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| topic_relevance_score | FLOAT             | Relevance to AI/topic (0-1)                                | Need to figure out how to assign via NLP, probably need to get training data together                                                      |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| enforcement_stance    | VARCHAR           | Tone towards regulation in speech                          | Pro-enforcement, neutral, deregulatory, mixed<br><br>Need to figure out how to assign via NLP, probably need to get training data together |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| gdpr_articles         | VARCHAR           | UK GDPR articles directly engaged                          |                                                                                                                                            |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| ingested_at           | TIMESTAMP         | Pipeline ingestion timestamp                               | Auto-generated                                                                                                                             |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in scored fields                   | Low confidence contribute less to score until manually reviewed                                                                            |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields         | FALSE are included in scoring but weighted differently                                                                                     |
| ---                   | ---               | ---                                                        | ---                                                                                                                                        |

## Table M2: Media Press

- Tracks major press coverage of data privacy and AI regulation issues
  - Media that should be monitored: The Guardian; The Times; Financial Times; BBC; The Register; WIRED UK; Computer Weekly; City A.M.
- Source: News websites

| **Field Name**        | **Variable Type** | **Description**                                             | **Example/Notes**                                                                                                                            |
| --------------------- | ----------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| press_id              | UUID              | Primary key                                                 | Auto-generated                                                                                                                               |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| publication_date      | DATE              | Date of publication                                         |                                                                                                                                              |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| outlet                | VARCHAR           | Publication name                                            |                                                                                                                                              |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| outlet_tier           | INTEGER           | 1=National/BBC<br><br>2= Specialist trade<br><br>3=Regional |                                                                                                                                              |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| headline              | TEXT              | Article headline                                            |                                                                                                                                              |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| source_url            | TEXT              | Source url                                                  |                                                                                                                                              |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| author                | TEXT              | Journalist who wrote article                                |                                                                                                                                              |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| story_type            | VARCHAR           | Type of story                                               | Investigation; opinion; news; data breach; regulatory response; profile<br><br>NLP assigned                                                  |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| target_org            | VARCHAR           | Subject of the story                                        | If applicable                                                                                                                                |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| ico_mentioned         | BOOLEAN           | Is the ICO mentioned in article?                            | TRUE/FALSE                                                                                                                                   |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| ico_action            | BOOLEAN           | Does the article call for ICO action?                       | TRUE/FALSE                                                                                                                                   |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| content_summary       | TEXT              | Content summary                                             | NLP generated                                                                                                                                |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| processing_activities | VARCHAR           | Processing activities/topic referenced                      | Used to route score contributions                                                                                                            |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| topic_relevance_score | FLOAT             | Relevance to AI/topic (0-1)                                 | Need to figure out how to assign via NLP, probably need to get training data together                                                        |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| enforcement_stance    | VARCHAR           | Tone towards regulation in article                          | Pro-enforcement; neutral; pro-regulatory; mixed<br><br>Need to figure out how to assign via NLP, probably need to get training data together |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| ingested_at           | TIMESTAMP         | Pipeline ingestion timestamp                                | Auto-generated                                                                                                                               |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| nlp_confidence        | FLOAT             | NLP pipeline confidence in scored fields                    | Low confidence contribute less to score until manually reviewed                                                                              |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |
| manually_reviewed     | BOOLEAN           | FALSE until human has verified NLP-assigned fields          | FALSE are included in scoring but weighted differently                                                                                       |
| ---                   | ---               | ---                                                         | ---                                                                                                                                          |

# ICO Complaint Volume

- ICO publishes the complaints it received every quarter, also have yearly reports
  - Quarterly reports have 3-6 month lag, annual is longer

## Table I1: Volume statistics

- Each row is one sector per reporting period
- Source: ICO website

| **Field Name**     | **Variable Type** | **Description**                                                | **Example/Notes**                                      |
| ------------------ | ----------------- | -------------------------------------------------------------- | ------------------------------------------------------ |
| stat_id            | UUID              | Primary key                                                    | Auto-generated                                         |
| ---                | ---               | ---                                                            | ---                                                    |
| period_start       | DATE              | First day of reporting period                                  |                                                        |
| ---                | ---               | ---                                                            | ---                                                    |
| period_end         | DATE              | Last day of reporting period                                   |                                                        |
| ---                | ---               | ---                                                            | ---                                                    |
| period_type        | VARCHAR           | Type of reporting period                                       | Annual; quarterly; FOI response                        |
| ---                | ---               | ---                                                            | ---                                                    |
| ico_sector         | VARCHAR           | ICO sector label                                               | Verbatim from ICO publication                          |
| ---                | ---               | ---                                                            | ---                                                    |
| sector_relevance   | VARCHAR           | Relevance of this sector                                       | Full; partial; none<br><br>We just have to set this up |
| ---                | ---               | ---                                                            | ---                                                    |
| complaint_count    | INTEGER           | Total complaints received from data subjects in period         |                                                        |
| ---                | ---               | ---                                                            | ---                                                    |
| data_breach_count  | INTEGER           | Data breach notifications received in period                   |                                                        |
| ---                | ---               | ---                                                            | ---                                                    |
| complaint_resolved | BOOLEAN           | Has the complaint been resolved?                               | TRUE/FALSE                                             |
| ---                | ---               | ---                                                            | ---                                                    |
| complaint_resolved | FLOAT             | Percentage of complaints resolved in period                    | Computed                                               |
| ---                | ---               | ---                                                            | ---                                                    |
| yoy_change_pct     | FLOAT             | Year-on-year percentage change vs same period last year        | Computed                                               |
| ---                | ---               | ---                                                            | ---                                                    |
| qoq_change+pct     | FLOAT             | Quarterly-on-quarterly percentage change                       | Computed, only for quarterly period type               |
| ---                | ---               | ---                                                            | ---                                                    |
| avg_3period        | FLOAT             | Rolling 3-period average complaint count (for specific sector) | Sector                                                 |
| ---                | ---               | ---                                                            | ---                                                    |
| pct_above_avg      | FLOAT             | ((complaint_count / avg_3period)-1) as percentage              | Computed                                               |
| ---                | ---               | ---                                                            | ---                                                    |
| spike_flag         | BOOLEAN           | Is the complaint_count> 1.5\*avg_3period?                      | TRUE/FALSE (computed)                                  |
| ---                | ---               | ---                                                            | ---                                                    |
| source_doc         | TEXT              | Source document title                                          |                                                        |
| ---                | ---               | ---                                                            | ---                                                    |
| source_url         | TEXT              | Source URL                                                     |                                                        |
| ---                | ---               | ---                                                            | ---                                                    |
| ingested_at        | TIMESTAMP         | Pipeline ingestion timestamp                                   | Auto-generated                                         |
| ---                | ---               | ---                                                            | ---                                                    |
| manually_reviewed  | BOOLEAN           | FALSE until human has verified ICO data                        | FALSE are included in scoring but weighted differently |
| ---                | ---               | ---                                                            | ---                                                    |

## Table I2: Volume scores

- Source: Table 1

| **Field Name**       | **Variable Type** | **Description**                                                                  | **Example/Notes**       |
| -------------------- | ----------------- | -------------------------------------------------------------------------------- | ----------------------- |
| score_id             | UUID              | Primary key                                                                      | Auto-generated          |
| ---                  | ---               | ---                                                                              | ---                     |
| ico_sector           | VARCHAR           | ICO sector tag from Table 1                                                      |                         |
| ---                  | ---               | ---                                                                              | ---                     |
| ref_period_start     | DATE              | Start of most recent period used                                                 |                         |
| ---                  | ---               | ---                                                                              | ---                     |
| ref_period_end       | DATE              | End of most recent period used                                                   |                         |
| ---                  | ---               | ---                                                                              | ---                     |
| complaint_count_used | INTERGER          | Complaint_count value from reference period                                      |                         |
| ---                  | ---               | ---                                                                              | ---                     |
| avg_3period_used     | FLOAT             | Avg_3period value used in computation                                            |                         |
| ---                  | ---               | ---                                                                              | ---                     |
| volume_factor        | FLOAT             | Ratio of complaint_count to avg_3period                                          |                         |
| ---                  | ---               | ---                                                                              | ---                     |
| trend_direction      | VARCHAR           | Direction of year-on-year trend                                                  | Rising; stable; falling |
| ---                  | ---               | ---                                                                              | ---                     |
| spike_active         | BOOLEAN           | TRUE is spike_flag in reference period                                           | TRUE/FALSE              |
| ---                  | ---               | ---                                                                              | ---                     |
| sector_risk_modifier | FLOAT             | Model; sector_risk_modifier = volume_factor \* trend_multiplier \* spike_monitor |                         |
| ---                  | ---               | ---                                                                              | ---                     |
| data_lag             | INTERGER          | Months between reference_period and computed_at                                  |                         |
| ---                  | ---               | ---                                                                              | ---                     |
| stale_flag           | BOOLEAN           | True is more than 9 months in data_lab                                           |                         |
| ---                  | ---               | ---                                                                              | ---                     |
| computed_at          | TIMESTAMP         | Timestamp of score computation run                                               |                         |
| ---                  | ---               | ---                                                                              | ---                     |
