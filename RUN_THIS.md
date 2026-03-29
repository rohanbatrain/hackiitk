# Run These Commands

Copy and paste these commands one by one:

## 1. Run Setup
```bash
./setup.sh
```

Wait for it to complete (5-10 minutes).

## 2. Activate Environment
```bash
source venv311/bin/activate
```

## 3. Test with Sample Policy
```bash
./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms
```

## 4. Test with Another Sample
```bash
./pa --policy-path data/policies/Access\ Control\ Policy.md --domain isms
```

## 5. Check Output
```bash
ls -la outputs/
```

You should see a timestamped directory with:
- gap_analysis.json
- revised_policy.md
- implementation_roadmap.md
- audit_log.json

## That's It!

If all tests pass, your Policy Analyzer is working correctly.

## Next Steps

Analyze your own policies:
```bash
./pa --policy-path /path/to/your/policy.pdf --domain isms
```
