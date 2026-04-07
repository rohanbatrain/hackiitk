# Diagram Index and Interpretation Guide

All diagram sources are in `PPT/diagrams/source/` as Mermaid (`.mmd`).

## Included diagrams

1. `architecture_overall.mmd`
   - High-level layered architecture and major component groups.

2. `end_to_end_sequence.mmd`
   - Primary runtime sequence from CLI invocation to output generation.

3. `setup_run_workflow.mmd`
   - Environment/setup/run workflow for operators.

4. `analysis_pipeline_flow.mmd`
   - Ingestion-to-analysis-to-output pipeline flow.

5. `module_component_interaction.mmd`
   - Module/component interaction map across major packages.

6. `offline_boundary.mmd`
   - Offline execution boundary and setup-time external dependency boundary.

7. `system_context.mmd`
   - System context view (actors and surrounding systems).

8. `container_view.mmd`
   - Container/process and data-store view for local runtime deployment.

9. `deployment_view.mmd`
   - Deployment-oriented view for local workstation/server node.

10. `trust_boundary_security.mmd`
    - Trust boundary/security boundary sketch.

11. `error_failure_flow.mmd`
    - Failure flow and decision points across execution stages.

12. `config_interaction.mmd`
    - Configuration surface interaction and schema mismatch risk.

13. `storage_artifact_flow.mmd`
    - Storage/artifact lifecycle flow.

14. `testing_execution_flow.mmd`
    - Test execution/CI flow map.

## Consistency notes

- Diagrams are grounded in code paths centered on `cli/main.py` and `orchestration/analysis_pipeline.py`.
- Where behavior is implementation-incomplete (placeholder code), diagrams reflect current behavior and do not assume future functionality.

## Rendered outputs

- `PPT/diagrams/rendered/` is reserved for exported images (PNG/SVG/PDF) if rendered later.
