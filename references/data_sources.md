# Data Sources

The current scaffold uses deterministic mock data from `src/ai_infra_review/data_sources/mock.py`.

Suggested production data sources:

- Company filings: SEC EDGAR, annual reports, quarterly reports, and earnings transcripts.
- Investor relations: company presentations, capex guidance, backlog commentary, and segment disclosures.
- Market data: prices, valuation multiples, short interest, ownership, and factor exposures.
- Supply chain data: foundry capacity, HBM supply, power equipment lead times, optical transceiver demand, and advanced packaging availability.
- Macro inputs: rates, electricity prices, grid interconnection queues, and data center construction activity.

Any production connector should preserve:

- Retrieval timestamp
- Source URL or document identifier
- Metric definition
- Unit and currency
- Restatement or revision handling
