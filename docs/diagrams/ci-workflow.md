# CI Workflow Diagram

## 🔄 Test Development Setup Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Push/PR                          │
│              (main/dev branch, scripts/**)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions Triggered                       │
│          Workflow: test-setup-dev.yml                       │
└─────┬───────────────┬───────────────┬───────────────────────┘
      │               │               │
      ▼               ▼               ▼
┏━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━━━━━━━━┓
┃   Linux    ┃  ┃   macOS    ┃  ┃  Multiple Python    ┃
┃  (Ubuntu)  ┃  ┃  (Latest)  ┃  ┃   (3.8 - 3.12)      ┃
┗━━━━┬━━━━━━━┛  ┗━━━━┬━━━━━━━┛  ┗━━━━━┬━━━━━━━━━━━━━━━┛
      │               │               │
      ├─ Checkout     ├─ Checkout     ├─ Checkout
      ├─ Setup Python ├─ Setup Python ├─ Setup Python 3.8
      ├─ Run setup    ├─ Run setup    ├─ Setup Python 3.9
      ├─ Verify venv  ├─ Verify venv  ├─ Setup Python 3.10
      ├─ Check deps   ├─ Check deps   ├─ Setup Python 3.11
      ├─ Test CLI     ├─ Test CLI     ├─ Setup Python 3.12
      ├─ Idempotent   ├─ Idempotent   └─ Test all versions
      └─ Display info ├─ No --user
                      └─ Clean system
      │               │               │
      ▼               ▼               ▼
┏━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━━━━━━━━┓
┃  ✅ PASS   ┃  ┃  ✅ PASS   ┃  ┃     ✅ PASS         ┃
┗━━━━┬━━━━━━━┛  ┗━━━━┬━━━━━━━┛  ┗━━━━━┬━━━━━━━━━━━━━━━┛
      │               │               │
      └───────────────┴───────────────┘
                     │
                     ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃     Summary Job          ┃
        ┃  Collect all results     ┃
        ┃  Display final status    ┃
        ┗━━━━━━━━━━┬━━━━━━━━━━━━━━┛
                   │
                   ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃  ✅ All Tests Passed     ┃
        ┃  Badge: Green            ┃
        ┃  PR: Ready to merge      ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## 📋 Detailed Check Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  ./docklite setup-dev                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │ Check Python   │
            │   version      │  ─────►  ✅ 3.8+ required
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │ Create .venv/  │
            │  directory     │  ─────►  ✅ Virtual env isolated
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │ Install deps   │
            │  in .venv/     │  ─────►  ✅ typer, rich, dotenv, yaml
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │ Create .env    │
            │  from example  │  ─────►  ✅ Configuration ready
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │ Check Docker   │
            │   running      │  ─────►  ✅ Docker available
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │ Make CLI       │
            │  executable    │  ─────►  ✅ ./docklite ready
            └────────┬───────┘
                     │
                     ▼
        ┏━━━━━━━━━━━━━━━━━━━━┓
        ┃  ✅ Setup Complete  ┃
        ┗━━━━━━━━━━━━━━━━━━━━┛
```

## 🧪 Test Verification Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Execution                           │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │ .venv/ │  │  .env  │  │  CLI   │
   │ exists │  │ exists │  │ works  │
   └───┬────┘  └───┬────┘  └───┬────┘
       │           │           │
       ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │ Python │  │ Config │  │Version │
   │ exists │  │ valid  │  │command │
   └───┬────┘  └───┬────┘  └───┬────┘
       │           │           │
       ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │  Deps  │  │ Docker │  │  Help  │
   │install │  │ check  │  │command │
   └───┬────┘  └───┬────┘  └───┬────┘
       │           │           │
       └───────────┴───────────┘
                   │
                   ▼
        ┏━━━━━━━━━━━━━━━━━━━━┓
        ┃  ✅ All Verified    ┃
        ┗━━━━━━━━━━━━━━━━━━━━┛
```

## 🍎 macOS Special Checks

```
┌─────────────────────────────────────────────────────────────┐
│                  macOS-Specific Tests                       │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ No --user    │ │ No --break-  │ │ User site    │
│   flag       │ │ system-pkgs  │ │   clean      │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
   ✅ PASS          ✅ PASS          ✅ PASS
       │                │                │
       └────────────────┴────────────────┘
                        │
                        ▼
             ┏━━━━━━━━━━━━━━━━━━━━┓
             ┃  System Python      ┃
             ┃  Not Polluted       ┃
             ┗━━━━━━━━━━━━━━━━━━━━┛
```

## 🔁 Idempotency Check

```
┌─────────────────────────────────────────────────────────────┐
│              First Run: ./docklite setup-dev                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
             ✅ Creates .venv/
             ✅ Installs dependencies
             ✅ Creates .env
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Second Run: ./docklite setup-dev                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
             ✅ .venv/ exists (skip)
             ✅ Dependencies installed (skip)
             ✅ .env exists (keep)
                     │
                     ▼
        ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        ┃  ✅ Idempotent             ┃
        ┃  No errors on rerun        ┃
        ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## ⚡ Parallel Execution

```
      Time: 0m                     5m                    10m
        │                          │                     │
Linux   ├──────────────────────────┤
        │  2-3 minutes             │
        │                          │
macOS   ├─────────────────────────────┤
        │  3-4 minutes                │
        │                          │
Python  ├────────────────────────────────────────────────┤
3.8     │  ■■■■■■■■■              │                     │
3.9     │    ■■■■■■■■■            │                     │
3.10    │      ■■■■■■■■■          │                     │
3.11    │        ■■■■■■■■■        │                     │
3.12    │          ■■■■■■■■■      │                     │
        │                          │                     │
        └──────────────────────────┴─────────────────────┘
                   Total: ~4-5 minutes (parallel)
```

## 🎯 Success Criteria

```
┌────────────────────────────────────────────────────────────┐
│                    All Checks Must Pass                    │
└────────────────────────────────────────────────────────────┘

✅ test-setup-linux
   └─ 8 verification steps

✅ test-setup-macos
   └─ 10 verification steps (including macOS-specific)

✅ test-setup-multiple-python
   └─ 5 Python versions tested

✅ summary
   └─ All jobs successful
   
        │
        ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                           ┃
┃              ✅ Badge: Passing                           ┃
┃              ✅ PR: Ready to merge                       ┃
┃              ✅ Production: Safe to deploy               ┃
┃                                                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

**Legend:**
- `─` Sequential flow
- `│` Parallel execution  
- `✅` Success check
- `┏━━┓` Important result
- `┌──┐` Process step

