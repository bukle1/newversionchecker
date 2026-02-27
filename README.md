# newversionchecker

A lightweight Python tool to check for new versions of packages and automate the update process.

## Usage

### Check a single package

```bash
python version_checker.py --package requests
```

### Check all packages in a requirements file

```bash
python version_checker.py --requirements requirements.txt
```

### Check and automatically apply updates

```bash
python version_checker.py --package requests --update
python version_checker.py --requirements requirements.txt --update
```

## Automated Checks

A GitHub Actions workflow (`.github/workflows/check-updates.yml`) runs every Monday at 09:00 UTC and reports any available dependency updates. It can also be triggered manually from the **Actions** tab.