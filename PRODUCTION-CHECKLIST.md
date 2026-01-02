# Production Deployment Checklist

## Pre-Deployment Phase (T-7 days)

### Code Readiness
- [ ] All feature branches merged to staging
- [ ] Code review completed (100% coverage)
- [ ] No blocking comments from reviewers
- [ ] All unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance tests baseline established
- [ ] Security scanning passed (SAST/DAST)
- [ ] Dependency vulnerabilities resolved
- [ ] Code documentation updated
- [ ] API documentation current
- [ ] Architecture decisions documented

### Infrastructure Readiness
- [ ] Production environment verified
- [ ] Database backups tested (restore time <2 hours)
- [ ] Load balancers configured
- [ ] CDN caching rules validated
- [ ] Firewall rules updated
- [ ] SSL/TLS certificates valid
- [ ] DNS records verified
- [ ] Monitoring dashboards created
- [ ] Alerting thresholds configured
- [ ] Log aggregation verified
- [ ] Rollback procedure documented
- [ ] Infrastructure as Code reviewed

### Data & Database
- [ ] Database migration scripts tested (dry-run)
- [ ] Data validation scripts prepared
- [ ] Backup size assessed
- [ ] Migration time estimated (<1 hour)
- [ ] Rollback data procedures documented
- [ ] Data retention policies reviewed
- [ ] Compliance checks passed (GDPR, etc.)

## Release Candidate Phase (T-3 days)

### Testing & QA
- [ ] Staging environment reflects production
- [ ] Full regression testing completed
- [ ] Performance testing passed (P99 <100ms)
- [ ] Load testing: 5x expected peak load
- [ ] Security penetration testing completed
- [ ] Accessibility testing passed (WCAG 2.1)
- [ ] Browser compatibility verified
- [ ] Mobile responsiveness checked
- [ ] API contract testing passed
- [ ] Data migration validation complete

### Documentation & Communication
- [ ] Release notes drafted
- [ ] Changelog updated
- [ ] Customer communication prepared
- [ ] Known issues documented
- [ ] Breaking changes highlighted
- [ ] Deployment instructions finalized
- [ ] Rollback procedures documented
- [ ] Team communication plan sent
- [ ] Customer support briefed
- [ ] SLAs acknowledged

### Business Readiness
- [ ] Product owner sign-off obtained
- [ ] Business requirements verified
- [ ] Analytics events instrumented
- [ ] Feature flags configured
- [ ] A/B testing setup complete (if applicable)
- [ ] Revenue impact assessed
- [ ] Customer success notified
- [ ] Sales team briefed
- [ ] Legal/compliance approval obtained

## Pre-Production Deployment (T-1 day)

### Operational Readiness
- [ ] On-call rotation confirmed
- [ ] Escalation procedures shared
- [ ] Team contact list updated
- [ ] War room setup (Slack/Discord/Zoom)
- [ ] Communication channels prepared
- [ ] Status page configured
- [ ] Monitoring queries tested
- [ ] Alerting tested end-to-end
- [ ] Run book reviewed by team
- [ ] Disaster recovery plan reviewed

### Infrastructure Final Checks
- [ ] Capacity planning validated
- [ ] Auto-scaling rules tested
- [ ] Database replicas synced
- [ ] Cache warming procedures ready
- [ ] DNS propagation time confirmed
- [ ] Backup systems tested
- [ ] Disaster recovery plan walkthrough

### Deployment Preparation
- [ ] Deployment scripts tested in staging
- [ ] Rollback scripts tested
- [ ] Database migration scripts validated
- [ ] Environment variables verified
- [ ] Configuration files audited
- [ ] Secrets management reviewed
- [ ] Deployment timing confirmed
- [ ] Maintenance window scheduled

## Deployment Execution Phase (T-0)

### Pre-Deployment Verification
- [ ] All team members present in war room
- [ ] Communications channels active
- [ ] Monitoring dashboards open
- [ ] Rollback procedures reviewed
- [ ] Deployment plan walkthrough complete
- [ ] Go/No-go decision made
- [ ] Stakeholders informed
- [ ] Canary deployment prepared

### Deployment Steps
- [ ] **Phase 1 - Canary (5% traffic)**: Monitor for 15-30 min
  - [ ] Error rates normal
  - [ ] Latency acceptable
  - [ ] Resource usage expected
  - [ ] No alerts triggered
  - [ ] Customer-facing features working
  
- [ ] **Phase 2 - Progressive Rollout (25% traffic)**: Monitor for 15-30 min
  - [ ] Error rates normal
  - [ ] Latency acceptable
  - [ ] Database load acceptable
  - [ ] Cache hit rates normal
  - [ ] No new issues observed
  
- [ ] **Phase 3 - Full Rollout (100% traffic)**: Monitor for 1+ hour
  - [ ] Error rates <0.1%
  - [ ] P99 latency <100ms
  - [ ] CPU utilization <70%
  - [ ] Memory utilization <75%
  - [ ] Database connections healthy
  - [ ] Queue depths normal

### Post-Deployment Validation
- [ ] All endpoints responding
- [ ] Database integrity checks passed
- [ ] Cache hit rates normal
- [ ] API response times acceptable
- [ ] WebSocket connections stable
- [ ] Background jobs processing
- [ ] Third-party integrations working
- [ ] Logging flowing normally
- [ ] Metrics being collected
- [ ] Smoke tests passed
- [ ] Critical user journeys tested

## Post-Deployment Phase (T+24 hours)

### Immediate Post-Deployment (T+1 hour)
- [ ] No critical alerts
- [ ] Error rate trending normal
- [ ] Customer reports: none critical
- [ ] Team confidence: high
- [ ] Decision: deployment stable

### Short-term Monitoring (T+24 hours)
- [ ] Error rates stable and expected
- [ ] Performance metrics stable
- [ ] Database performance normal
- [ ] Customer satisfaction surveys: no issues
- [ ] User adoption metrics tracked
- [ ] Feature usage metrics analyzed
- [ ] Performance baselines updated
- [ ] Deployment retrospective scheduled

### Post-Deployment Analysis
- [ ] Deployment time recorded
- [ ] Issues encountered documented
- [ ] Rollback events (if any) analyzed
- [ ] Customer feedback collected
- [ ] Metrics compared to baseline
- [ ] Cost impact assessed
- [ ] Lessons learned documented
- [ ] Process improvements identified

## Rollback Triggers

Immediate rollback if:
- [ ] Error rate >1%
- [ ] API latency P99 >500ms
- [ ] Database unavailable
- [ ] Data corruption detected
- [ ] Security vulnerability discovered
- [ ] Revenue-impacting feature broken
- [ ] Critical customer impacted
- [ ] Cascading failures occur

## Rollback Procedure

1. [ ] Declare rollback decision
2. [ ] Notify all stakeholders
3. [ ] Execute rollback script
4. [ ] Verify database rollback
5. [ ] Clear caches
6. [ ] Verify routing to previous version
7. [ ] Run smoke tests
8. [ ] Confirm rollback complete
9. [ ] Document reasons
10. [ ] Schedule incident review

## Post-Rollback
- [ ] Incident severity assessed
- [ ] Root cause analysis started
- [ ] Timeline of events documented
- [ ] Stakeholder communication sent
- [ ] Development team briefed
- [ ] Investigation plan created
- [ ] Prevention measures identified

## Sign-Offs

### Deployment Approval
- [ ] Engineering Lead: _________________ Date: _____
- [ ] Product Owner: _________________ Date: _____
- [ ] DevOps Lead: _________________ Date: _____
- [ ] Security Lead: _________________ Date: _____

### Deployment Execution
- [ ] Deployed by: _________________ Date: _____ Time: _____
- [ ] Approved by: _________________ Date: _____ Time: _____

### Post-Deployment Sign-Off
- [ ] Operations Lead: _________________ Date: _____
- [ ] Product Owner: _________________ Date: _____
- [ ] Verified Stable: _________________ Date: _____

## Notes & Issues

```
[Document any issues encountered during deployment]




```

---

**Deployment Version**: v[X.Y.Z]  
**Deployment Date**: [Date]  
**Deployment Time**: [Start Time - End Time]  
**Environment**: Production  
**Status**: [Success/Rollback/Partial]
