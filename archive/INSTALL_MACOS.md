# Install on macOS - Super Simple

## One-Line Install

```bash
chmod +x setup_mac.sh && ./setup_mac.sh
```

## What Happens

The script will:
1. Check Python (needs 3.8+)
2. Create virtual environment
3. Install all dependencies
4. Install policy-analyzer
5. Check/setup Ollama
6. Download LLM model
7. Create helper scripts
8. Test everything

Takes about 5-10 minutes depending on your internet speed.

## After Install

```bash
# Activate
source activate.sh

# Test
./test_installation.sh

# Use
policy-analyzer analyze policy.pdf --domain isms
```

## That's It!

See `SETUP_MAC_README.md` for more details.

---

**Quick Start:**
1. Run: `chmod +x setup_mac.sh && ./setup_mac.sh`
2. Wait for setup to complete
3. Run: `source activate.sh`
4. Run: `policy-analyzer info`
5. Start analyzing!
