# HashBash - v 1.153

A lightweight, cross‑platform Tkinter frontend for **hashcat** with drag‑and‑drop, session restore, and a terminal‑style splash screen. Built for fast workflows and repeatable cracking runs.

> **Important:** Use this tool only on hashes you are authorized to test. Educational and legitimate security testing purposes only.

---

## Features

* 🎛️ Simple GUI over hashcat (select hashes, wordlists, rules)
* 📦 Persistent settings via `settings.json`
* 🧷 Session management (`--session hashcat_gui`) with **Restore** support
* ⏯️ Pause/Resume via hashcat’s interactive stdin (`p`/`r`)
* 🧹 New Session command cleanly stops and resets state
* 🧲 Drag‑and‑drop for hashes/wordlists/rules (via `tkinterdnd2`)
* 📝 Results automatically exported to `results/results.txt` and opened

---

## Requirements

### Runtime

* **Python** 3.8+ (with Tkinter)
* **hashcat** installed and available on your system `PATH`
* Python package: `tkinterdnd2` (see `requirements.txt`)

> **Linux:** you may need your distro’s Tk packages (e.g. Ubuntu/Debian: `sudo apt install python3-tk`).

### Tested Platforms

* Windows 10/11
* macOS (Apple Silicon/Intel)
* Linux (X11/Wayland)

> Drag‑and‑drop relies on `tkinterdnd2`. Ensure your Python’s Tk is 8.6+.

---

## Installation

```bash
# 1) Install hashcat (system-level)
# Windows: use the official binary and add to PATH
# macOS (Homebrew): brew install hashcat
# Debian/Ubuntu: sudo apt install hashcat

# 2) For Nvidia GPU Acceleration be sure to install the proper version of 
# Nvidia CUDA Developers Toolkit along for your Video Card!
# Also Be sure to have up-to-date Video Card Drivers INSTALLED!
. .\Downloads\Nvidia\cuda_12.9.1_576.57_windows.exe
# Older Video Cards will need deprecated or older versions of both Drivers
# and CUDA Dev Toolkits ALONG WITH VERSIONS OF HASHCAT!

# 3) Install Python deps
pip install -r requirements.txt

# 4) Clone
git clone https://github.com/TheMetalBit/HashBash.git
cd \HashBash
copy entire contents of \HashBash into your currently running C:\..\Hashcat-x.x.x directory. 
--------------------------------
# 5) (Optional) - Not nessesary, but Paranoia is sometimes good! To Create a Virtual Python Environment...
python -m venv .venv
# Windows
. .venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

---

## Running

# (Note) - HashBash.py Should always be run from the current working Hashcat-x.x.x directory! 
```bash
python3 hashbash.py
```
# -Example running HashBash Windows Installation In Currently Running Hashcat Directory-
# cd C:\Program Files\hashcat7.1.2
# C:\Program Files\hashcat7.1.2>python3 hashbash.py

* A splash window appears; press **Continue** (or hit **Enter/Space**).
* Use **Select Hash Files**, **Select Wordlists**, and **Select Rules** to load inputs.
* Choose **Hash Mode**, **Workload Level**, **Attack Type**, **Device Type**.
* Optionally toggle **Use Slow Candidates (-S)**.
* Click **Run Hashcat**.
* Results are appended to `results/results.txt` and opened when the queue finishes.
* \*\*\*While running, configuration widgets are hidden; use **Pause**, **Resume**, or **Cancel**.

  \*\*\* - This feature will be release in future versions of HashBash. For now you MUST CANCEL A RUNNING SESSION BEFORE ADJUSTING RUNNING OPTIONS!!! If you do so and click on the Run Hashcah Button the GUI will spit out a results.txt specifying that there already an instance running. In This case just exit out of the GUI and re-run HashBash.

### Session Restore

If a `hashcat_gui.restore` file exists, you’ll be \*\*\*prompted to restore the prior session on launch.

\*\*\* - This feature will be release in future versions of HashBash. For now if you exit GUI while session is running, all configurations will be restored upon restart of the HashBash GUI unless you select New Session from top Drop Down Menu.

### New Session

`Session → New Session` cleanly stops any running session, clears queues/UI, deletes `results.txt` (in the configured output dir), and removes session restore/log files.

---

## File Layout (suggested)

```
repo/
├─ hashbash.py          # the main script
├─ requirements.txt     # Python dependencies
├─ settings.json        # created/updated at runtime
└─ results/
   └─ results.txt       # auto-generated output
```

> You may rename `hashbash.py`; update this README accordingly.

---

## Configuration Details

* `settings.json` is created in the working directory and persists:

  * `hash_files`, `wordlists`, `rules`
  * `hash_mode`, `workload`, `attack_mode`, `devices`
  * `slow_candidates` (boolean)
  * `output_dir` (defaults to `results/` if unset)

* The hashcat **session name** is fixed as `hashcat_gui`.

---

## Troubleshooting

**“hashcat not found”** → Ensure `hashcat` is installed and available on `PATH`.

**Tkinter missing on Linux** → Install system Tk: `sudo apt install python3-tk` (Debian/Ubuntu) or your distro equivalent.

**Drag & Drop not working** → Confirm `tkinterdnd2` is installed in the same Python environment you’re using to run the app.

**Splash art misaligned** → The app forces a monospaced system font (`TkFixedFont`). If it still looks off, ensure your OS has a default monospace font installed.

**No output** → Hashcat writes progress to stdout/stderr, which the GUI streams to the output pane; if nothing appears, recheck mode/attack/inputs and run hashcat manually in a terminal for the same command.

---

## Security & Ethics

Only operate on hashes you own or have explicit permission to test. Follow all applicable laws and policies.

---

## License

Choose a license and add a `LICENSE` file (MIT, Apache-2.0, GPL-3.0, etc.).

---

## Acknowledgements

* [hashcat](https://hashcat.net/hashcat/)
* `tkinterdnd2`

---

## Contributing

PRs and issues are welcome. Please avoid adding heavy dependencies; the goal is a small, portable GUI.
