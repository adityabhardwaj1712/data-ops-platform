# Delivery Checklist (Mandatory)

Every paid job MUST pass these checks before "Delivery" to the client.

## 1. Data Integrity ✅
- [ ] **Schema Match**: All fields in the delivered CSV match the client's request.
- [ ] **Row Count**: Minimum 95% of expected rows extracted successfully.
- [ ] **No Nulls**: Crucial fields (e.g., "Email", "Price") have < 5% null values.
- [ ] **Deduplication**: Run `Deduplicator` to ensure no verbatim duplicates.

## 2. Quality & Trust 🛡️
- [ ] **Confidence Threshold**: Average confidence score per task is > 90%.
- [ ] **HITL Review**: If any flag for `NEEDS_HITL` was raised, it has been resolved by a human.
- [ ] **Sample Audit**: Manually check 10 random rows against the source URL for accuracy.

## 3. Package Standards 📂
- [ ] **File Format**: Clean CSV or Excel (no technical metadata like `_task_id`).
- [ ] **README Included**: Explains field meanings and scrape date.
- [ ] **Metadata JSON**: Includes `scrape_date`, `confidence_summary`, and `reviewed: true`.

---
> [!IMPORTANT]
> **Audit Trail**: Save this checklist (completed) in the job's artifact folder as `audit_log.md` before finalizing delivery.
