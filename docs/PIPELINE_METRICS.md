# Veriqo Pipeline Metrics

## Owner

Kendra Lynne Abellana — DevOps Engineer

## Current Status

The pipeline is not yet implemented or verified.
Measurements will be recorded from actual runs.

## Weekly Summary

All durations are in minutes.

| Sprint | Avg PR duration | Avg main duration | CI success % | Production deploys | Avg merge-to-live | Failed deploys | Avg recovery time | Improvement |
|---|---|---|---|---|---|---|---|---|
| 1 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Establish baseline |
| 2 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | To be recorded |
| 3 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | To be recorded |
| 4 | Pending | Pending | Pending | Pending | Pending | Pending | Pending | To be recorded |

## Measurement Rules

- PR duration: workflow start until completion.
- Main duration: main workflow start until completion.
- Record queue time separately if relevant.
- CI success rate:
  successful runs / (successful runs + failed runs) × 100.
- Exclude running and cancelled runs from that calculation;
  report cancelled runs separately.
- Production deployments: count verified successful deployments.
- Merge-to-live: merge time until the correct deployed version
  passes live verification.
- Failed deployments: failed rollout or failed post-deploy verification.
- Recovery time: detected deployment/service failure until
  a healthy version is verified again.
- Record sample counts alongside averages.
- Use Pending before measurement.
- Use N/A when a metric does not apply.
- Use 0 only when a measured count is actually zero.
- Never invent measurements.

## Run Evidence

Add one entry for each measured CI run.

| Date/time and timezone | Sprint | Branch or PR | Commit | Run URL | Duration | Result |
|---|---|---|---|---|---|---|

## Deployment Evidence

| Merge time | Commit | Deployment URL or ID | Verified-live time | Result | Recovery time |
|---|---|---|---|---|---|

Use consistent timestamps and state the timezone.

## Weekly Sample Counts

| Sprint | Successful CI runs | Failed CI runs | Cancelled CI runs | PR duration samples | Main duration samples |
|---|---|---|---|---|---|
| 1 | Pending | Pending | Pending | Pending | Pending |
| 2 | Pending | Pending | Pending | Pending | Pending |
| 3 | Pending | Pending | Pending | Pending | Pending |
| 4 | Pending | Pending | Pending | Pending | Pending |

## Optimization Evidence

For each improvement, record:

- Problem.
- Change made.
- Comparable before/after runs and their links.
- Sample counts.
- Measured improvement.
- Confirmation that required checks remain.

Keep detailed comparisons in docs/OPTIMIZATIONS.md.
Update this log before every consultation.
