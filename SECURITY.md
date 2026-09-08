# Security policy

These are offline demonstrations maintained by VirtualAgentics. Report vulnerabilities privately using GitHub's **Report a vulnerability** option on the Security tab, or email **bdc@virtualagentics.ai**. Do not include real customer data, credentials or payment information in public issues. This mailbox is owner-managed; no response-time commitment is offered.

## Supported scope

The current default branch is supported. These examples are not deployed services. Python source, input validation, output integrity, dependencies and GitHub workflows are in scope. Input files and payloads are untrusted; the local filesystem and database are controlled by the caller. Running untrusted Python code requires a separate sandbox.

## Required properties

Invalid input must not silently become accepted business data. Duplicate orders must not be counted twice. CSV rows must reconcile to accepted or withheld records, Excel output must preserve supported literal text, and existing output directories must not be overwritten. Credentials and customer data must stay out of this repository and CI. Pull-request code runs without deployment credentials or repository write permissions.

## Limitations

See the README for exact supported inputs and failure behavior. Tests and scanning reduce risk; they do not prove absence of defects. No security findings are excluded solely because this is a demonstration. Report practical impact and a synthetic reproducer when possible. There is no paid bounty or service-level agreement.
