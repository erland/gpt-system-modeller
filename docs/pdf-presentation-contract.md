# PDF presentation contract

B9 defines the PDF presentation rules as part of the canonical internal `standard` architecture report profile in `metamodel/report-profiles/standard.yaml`.

The contract is presentation-only. It does not modify the canonical architecture model and must not change model semantics. Markdown remains the report source; PDF exporters must derive layout from the same report profile.

## Page and headings

The standard PDF target is A4 portrait with explicit millimetre margins. Major architecture sections start on a new page. Heading levels are fixed as title 1, report section 2, diagram group 3 and detail diagram 4. A heading should stay with the following content when the exporter supports that behavior.

## Diagrams

Diagram composition continues to follow the B6-B8 rules before PDF layout is applied. The PDF contract then constrains the rendered result to 92 percent of available content width and 155 mm maximum diagram height. Diagrams are centered and kept with their captions where possible. Captions are placed below and use the prefix `Diagram`.

B7 overview/detail parts remain separate diagrams; detail parts do not automatically force a new page. B8 sequence diagrams remain one Interaction per diagram.

## Tables and text

Tables repeat their header across pages, wrap cell content and should avoid splitting a single row between pages. Standard table text is 8.5 pt. Body text is 10 pt with 1.15 line spacing.

Code and generated diagram source must wrap when necessary and retain a visible code frame when included in a PDF-oriented rendering path.

## Pagination

Widow and orphan targets are two lines. Page numbering is enabled. These are layout requirements for the exporter, not additions to the Markdown report semantics.

## Machine-readable contract

Run:

```bash
python3 scripts/pdf_contract.py
python3 scripts/pdf_contract.py --format json
```

The tool validates the standard report profile and emits `system-modeller-pdf-presentation-v1`, including section order, PDF presentation rules and the B6-B8 diagram policy that the PDF renderer must respect.

B9 establishes the contract only. B10 adds end-to-end small/medium/large report regression and is responsible for verifying rendered report behavior against representative systems.
