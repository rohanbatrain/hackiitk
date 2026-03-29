# 🚀 START HERE - macOS Setup

## Step 1: Run This Command

Open Terminal in this directory and run:

```bash
./setup_mac.sh
```

**That's it!** The script does everything automatically.

## Step 2: Activate and Test

After setup completes:

```bash
source activate.sh
./test_installation.sh
```

## Step 3: Analyze Your First Policy

```bash
policy-analyzer analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms
```

## Done! 🎉

Check the `outputs/` folder for results.

---

## Daily Usage

Every time you want to use the tool:

```bash
# Option 1: Activate first
source activate.sh
policy-analyzer analyze your-policy.pdf --domain isms
deactivate

# Option 2: Use launcher (easier!)
./policy-analyzer.sh analyze your-policy.pdf --domain isms
```

---

## Need Help?

- **Quick Start**: Read `MACOS_QUICK_START.md`
- **Commands**: Read `CLI_QUICK_REFERENCE.md`
- **Full Guide**: Read `docs/CLI_GUIDE.md`
- **Examples**: Run `./examples.sh`
- **Help**: Run `policy-analyzer --help`

---

## Troubleshooting

### "Permission denied"
```bash
chmod +x setup_mac.sh
./setup_mac.sh
```

### "Command not found"
```bash
source activate.sh
```

### "Python not found"
```bash
brew install python@3.11
```

---

**That's all you need to know to get started!**

Run `./setup_mac.sh` now! ⚡
