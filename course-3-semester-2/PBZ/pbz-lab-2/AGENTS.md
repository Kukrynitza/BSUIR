# AGENTS.md - PBZ Lab 2 (Ontology Project)

## Project Overview

This is a **PBZ (Knowledge Bases / Artificial Intelligence) lab** for BSUIR, semester 3-2.
The project contains OWL ontologies built using **WebProtege** and related ontology editing tools.

## Project Structure

| File | Description |
|------|-------------|
| `pbz-lab-2.owx` | Main ontology file (WebProtege format) |
| `cob.xml` | Imported COB (Core Ontology for Biology and Biomedicine) ontology |
| `ogms.owl` | Imported OGMS (Ontology for General Medical Science) ontology |
| `catalog-v001.xml` | XML catalog for ontology import resolution |
| `*.docx` | Lab report / documentation files |

## File Format Conventions

- **Ontologies**: OWL 2 DL in RDF/XML serialization (`.xml`, `.owl`, `.owx`)
- **Encoding**: UTF-8 for all XML files
- **XML declaration**: Always include `<?xml version="1.0"?>` at the top
- **Namespaces**: Use standard OBO Foundry namespace prefixes:
  - `rdf:`, `rdfs:`, `owl:`, `xsd:` (W3C standards)
  - `obo:` for `http://purl.obolibrary.org/obo/`
  - `oboInOwl:` for OBO-in-OWL metadata
  - `dc:`, `terms:` for Dublin Core metadata

## Working with Ontologies

- **Primary tool**: WebProtege (cloud-based) or Protege Desktop
- **Reasoning**: Use a DL reasoner (HermiT, ELK) to verify consistency
- **Validation**: Ensure the ontology passes reasoner consistency checks before submitting

## Catalog Management

- `catalog-v001.xml` maps ontology IRIs to local file paths
- When adding new imports, add corresponding `<uri>` entries to the catalog
- Local files take precedence; use `file:/` URIs for local resources

## Lab Report Guidelines

- Reports are `.docx` format (Word)
- Include ontology diagrams, class hierarchies, and SPARQL queries if applicable
- Screenshot ontology views from Protege/WebProtege for the report

## No Traditional Build/Lint/Test

This project has **no build system, no linter, and no automated tests**.
Ontology quality is validated through:
1. Reasoner consistency checks (no unsatisfiable classes)
2. Manual review of class hierarchy and axioms
3. SPARQL query verification against expected results

## Common Tasks

- **Add a new class**: Define in `.owx` with `rdfs:label`, `rdfs:subClassOf`, and `IAO_0000115` (definition)
- **Add an import**: Update `catalog-v001.xml` and add import declaration in the ontology header
- **Verify consistency**: Run Protege reasoner (HermiT or ELK)
