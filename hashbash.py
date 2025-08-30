import sys
import os
import json
import subprocess
import threading
import signal
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
from tkinterdnd2 import DND_FILES, TkinterDnD

SETTINGS_FILE = "settings.json"
SESSION_NAME = "hashcat_gui"

# --- Splash Screen ---
def launch_hashbash_gui():
    """Start the main HashBash GUI (TkinterDnD root)."""
    root = TkinterDnD.Tk()
    app = HashcatGUI(root)
    root.mainloop()


def show_splash():
    """Blocking splash window with ASCII art and a Continue button."""
    splash = Tk()
    splash.title("#HashBash - Bash the HASH!!!")
    splash.configure(bg="black")

    # Center the window
    splash.update_idletasks()
    ww, wh = 900, 900
    sw = splash.winfo_screenwidth()
    sh = splash.winfo_screenheight()
    x = (sw - ww) // 2
    y = (sh - wh) // 3
    splash.geometry(f"{ww}x{wh}+{x}+{y}")
    splash.resizable(False, False)

    # Use grid for predictable layout (art expands, button fixed at bottom)
    splash.grid_rowconfigure(0, weight=1)
    splash.grid_rowconfigure(1, weight=0)
    splash.grid_columnconfigure(0, weight=1)

    # ASCII art (hammer smashing the #)
    ascii_art = r"""
  ::.  .::   .:::.    .:::::   ::.  .::  :::::::    .::::    .:::::   ::.  .::  
  ++=  =++.  -+++=   :=+++++-. =+=  =++ .+++++++:   =+++=   :=+++++: .++-  =++  
  ++=  =++.  -++++.  =++-:+++: =+=  =++..++=:-+++. .+++++. .+++::=++ .++-  =+=  
  ++=  =++. .+++++:  =++  .::. ++=  =++..++-  +++. -+++++: .++=  .:: .++-  =+=  
  ++=::=++. :++--+=  =++=-:.   ++=::=++..++=--++-  =++:=+= .+++--    .++=--=++  
  ++++++++. -++.:++: .:=+++=.  ++++++++..++++++=. .++= -++. ..=+++-  .++++++++  
 .++=::=++. =++.:++-    :-=++- ++=::=++..++=:-+++  ++=.-++:    :==+=: ++=::=+=  
 .++=  =++..+++++++= .::  -++- ++=  =++..++-  +++ :+++++++- ...  -++- ++-  -++  
 .++=  =++..++=:-++=.=+=..-++- ++=  =++..++-..+++ -++-:-++= ++=..-++: ++-  -++  
 .++=  =++..++:  =+= .-+++++-. ++=  =++..+++++++. =++. .++=.:=+++++=. =+-  -++  
  ::.  ::: .::.  .::  .:::::   ::.  .::  :::::::  :::   :::  .::::::  :::  .::  
                                        .                                       
                                   .:---:.           BASH da' HASH              
                                :-==-.                                          
                            .:==+=:.                               .::          
                          :-====:                            ..::-===-:         
                       .:======.                        ..:--==--:..  ..        
                     ..-=======.                  ..:--==--::..       .         
                    , :=========            .::-====--:..       .....'          
                   .   :========:     ..:---==-::...      ....''                
                   .   .=========:'.:---::...       ....''                      
                    .   -=========-          ....'''                            
         `  .       ...:==========... ....''                                    
            .. .     ..  .=========-'''                                         
                *`    .   :========-.                                           
            ` $  ''    .   :----:. .                                            
               .--. .   .....  .--.:.                                           
              .-=-          ..  :=::-.          HashBash GUI ver. 1.153         
          ....:==-....--     .. .-====-                 made by                 
         :+=============--  ...:--=====-           #The Metal->Bit              
         .:::-===:::::==-:  ...--====---.                                       
             -==-    :--.    .:::::::::::         --Special Thanks--            
            .===.    -==      ::........'          [CBKB] DeadlyData            
        ::::-===:::::===-::     * .  .  *                                       
        =+=================- * .   $ . .                                        
        ...:===:....===...     ..* . $ *.                                       
           :==-    .==-    ..:  . ..$ .  .  THIS SOFTWARE IS FOR EDUCATIONAL    
           :--:    .--:   .. ..* ' . #=$  $          PURPOSES ONLY.             
                          ` ` ``   `  `  `                                      
"""
        # Auto-scale font and render ANSI art into a Text widget
    mono = tkfont.nametofont("TkFixedFont")
    try:
        mono.configure(size=14)
    except Exception:
        pass

    lbl = Label(
        splash,
        text=ascii_art,
        bg="black",
        fg="#00ff00",
        font=mono,
        justify=CENTER,
        anchor="n"
    )
    lbl.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 0))

    btn = Button(
        splash,
        text="Continue",
        command=splash.destroy,
        bg="#0f0",
        fg="#000",
        activebackground="#7fff7f",
        padx=12,
        pady=6
    )
    btn.grid(row=1, column=0, sticky="ew", padx=20, pady=20)

    # Auto-adjust height so the art fits the screen and the Continue button stays visible
    splash.update_idletasks()
    try:
        line_h = mono.metrics("linespace")
    except Exception:
        line_h = 16
    lines = len(ascii_art.splitlines())
    btn_h = btn.winfo_reqheight()
    # Estimate content height: art lines + top padding + button + bottom padding + small fudge
    content_h = (lines * max(1, line_h)) + 20 + btn_h + 20 + 40
    max_h = sh - 80  # keep some margin from screen bottom
    new_h = min(max(300, int(content_h)), int(max_h))
    if new_h != wh:
        y = (sh - new_h) // 3
        splash.geometry(f"{ww}x{new_h}+{x}+{y}")

    # Keyboard shortcuts
    splash.bind("<Return>", lambda e: splash.destroy())
    splash.bind("<space>", lambda e: splash.destroy())

    splash.mainloop()

class HashcatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("#HashBash v1.153 - made by #The Metal->Bit")
        self.root.configure(bg="black")
        self.jobs = []
        self.current_job = None
        self.process = None
        self.cancelled_current = False

        self.allowed_extensions = {
            "hash_files": None,
            "wordlists": ['.txt', '.lst', '.dic'],
            "rules": ['.rule', '.txt']
        }

        self.load_settings()
        self.setup_widgets()
        self.check_resume_session()

    def setup_widgets(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        menubar = Menu(self.root)
        session_menu = Menu(menubar, tearoff=0)
        session_menu.add_command(label="New Session", command=self.new_session)
        menubar.add_cascade(label="Session", menu=session_menu)
        self.root.config(menu=menubar)

        content = Frame(self.root, bg="black")
        content.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Hash files selection
        hash_frame = Frame(content, bg="black")
        hash_frame.pack(fill=X)
        Button(hash_frame, text="Select Hash Files", command=self.select_hash_files).pack(side=LEFT, fill=X, expand=True)
        Button(hash_frame, text="Remove Selected", command=lambda: self.remove_selected(self.hash_listbox, "hash_files")).pack(side=LEFT)
        Button(hash_frame, text="Remove All", command=lambda: self.remove_all(self.hash_listbox, "hash_files")).pack(side=LEFT)
        self.hash_listbox = Listbox(content, selectmode=MULTIPLE, height=4, bg="black", fg="green")
        self.hash_listbox.pack(fill=X)
        self.register_drag_and_drop(self.hash_listbox, "hash_files")

        # Wordlists selection
        wl_frame = Frame(content, bg="black")
        wl_frame.pack(fill=X)
        Button(wl_frame, text="Select Wordlists", command=self.select_wordlists).pack(side=LEFT, fill=X, expand=True)
        Button(wl_frame, text="Remove Selected", command=lambda: self.remove_selected(self.wordlist_listbox, "wordlists")).pack(side=LEFT)
        Button(wl_frame, text="Remove All", command=lambda: self.remove_all(self.wordlist_listbox, "wordlists")).pack(side=LEFT)
        self.wordlist_listbox = Listbox(content, selectmode=MULTIPLE, height=4, bg="black", fg="yellow")
        self.wordlist_listbox.pack(fill=X)
        self.register_drag_and_drop(self.wordlist_listbox, "wordlists")

        # Rules selection
        rule_frame = Frame(content, bg="black")
        rule_frame.pack(fill=X)
        Button(rule_frame, text="Select Rules", command=self.select_rules).pack(side=LEFT, fill=X, expand=True)
        Button(rule_frame, text="Remove Selected", command=lambda: self.remove_selected(self.rule_listbox, "rules")).pack(side=LEFT)
        Button(rule_frame, text="Remove All", command=lambda: self.remove_all(self.rule_listbox, "rules")).pack(side=LEFT)
        self.rule_listbox = Listbox(content, selectmode=MULTIPLE, height=4, bg="black", fg="red")
        self.rule_listbox.pack(fill=X)
        self.register_drag_and_drop(self.rule_listbox, "rules")

        # Controls
        opts = Frame(content, bg="black")
        opts.pack(fill=X, pady=5)
        for i in range(4): opts.grid_columnconfigure(i, weight=1)

        self.output_btn = Button(opts, text="Select Output Directory", command=self.set_output_directory)
        self.output_btn.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=2)

        labels = ["Hash Mode:", "Workload Level:", "Attack Type:", "Device Type:"]
        for idx, txt in enumerate(labels):
            Label(opts, text=txt, bg="black", fg="white").grid(row=1, column=idx, sticky="w", padx=5)

        # Comboboxes
        self.hashmode_var = StringVar(value=self.settings.get("hash_mode", "22000"))
        self.hashmode_cb = ttk.Combobox(opts, textvariable=self.hashmode_var, state="readonly")
        self.hashmode_cb['values'] = ["0","100","1400","1700","1000","22000","3200","400","9600","10500","11600","13000"]
        self.hashmode_cb.grid(row=2, column=0, sticky="ew", padx=5)

        self.workload_var = StringVar(value=self.settings.get("workload", "2"))
        self.workload_cb = ttk.Combobox(opts, textvariable=self.workload_var, state="readonly", width=10)
        self.workload_cb['values'] = ["1","2","3","4"]
        self.workload_cb.grid(row=2, column=1, sticky="ew", padx=5)

        self.attack_var = StringVar(value=self.settings.get("attack_mode", "0"))
        self.attack_cb = ttk.Combobox(opts, textvariable=self.attack_var, state="readonly", width=10)
        self.attack_cb['values'] = ["0","1","3","6","7"]
        self.attack_cb.grid(row=2, column=2, sticky="ew", padx=5)

        self.device_var = StringVar(value=self.settings.get("devices", "1,2"))
        self.device_cb = ttk.Combobox(opts, textvariable=self.device_var, state="readonly", width=10)
        self.device_cb['values'] = ["1","2","1,2"]
        self.device_cb.grid(row=2, column=3, sticky="ew", padx=5)

        # Slow candidates checkbox (clickable / Windows-safe)
        slow_default = 1 if self._to_bool(self.settings.get("slow_candidates", False)) else 0
        self.slow_var = IntVar(value=slow_default)
        self.slow_cb = Checkbutton(
            content,
            text="Use Slow Candidates (-S)",
            variable=self.slow_var,
            onvalue=1,
            offvalue=0,
            bg="black",
            fg="white",
            activebackground="black",
            activeforeground="white",
            selectcolor="red",
            state=NORMAL,
            takefocus=1,
            cursor="hand2",
            command=self.on_slow_toggle
        )
        self.slow_cb.pack(anchor=W)

        Button(content, text="Run Hashcat", command=self.load_jobs_from_hashes).pack(fill=X, pady=5)

        # Pause/Resume
        ctrl = Frame(content, bg="black")
        ctrl.pack(fill=X)
        self.pause_btn = Button(ctrl, text="Pause", command=self.pause_job, state=DISABLED)
        self.pause_btn.pack(side=LEFT, padx=5, fill=X, expand=True)
        self.resume_btn = Button(ctrl, text="Resume", command=self.resume_job, state=DISABLED)
        self.resume_btn.pack(side=LEFT, padx=5, fill=X, expand=True)

        # Output display
        self.output_text = Text(content, height=15, bg="black", fg="green")
        self.output_text.pack(fill=BOTH, expand=True)

        # Bottom buttons
        bf = Frame(self.root, bg="black")
        bf.grid(row=1, column=0, sticky="ew")
        self.exit_btn = Button(bf, text="Exit", command=self.confirm_exit).pack(side=RIGHT, padx=5, pady=5)
        self.cancel_btn = Button(bf, text="Cancel", command=self.cancel_job)
        self.cancel_btn.pack_forget()

        self.refresh_all_listboxes()

    # File selectors
    def set_output_directory(self):
        d = filedialog.askdirectory()
        if d:
            self.settings["output_dir"] = d
            self.save_settings()
            self.output_btn.config(text=f"Output Directory: {d}")

    def select_hash_files(self):
        paths = filedialog.askopenfilenames(title="Select Hash Files", filetypes=[("All Files","*.*")])
        if paths:
            self.settings.setdefault("hash_files", [])
            for p in paths:
                if self._check_extension(p, "hash_files") and p not in self.settings["hash_files"]:
                    self.settings["hash_files"].append(p)
            self.refresh_listbox(self.hash_listbox, self.settings["hash_files"])
            self.save_settings()

    def select_wordlists(self):
        paths = filedialog.askopenfilenames(title="Select Wordlists", filetypes=[("Wordlists","*.txt *.lst *.dic"),("All","*.*")])
        if paths:
            self.settings.setdefault("wordlists", [])
            for p in paths:
                if self._check_extension(p, "wordlists") and p not in self.settings["wordlists"]:
                    self.settings["wordlists"].append(p)
            self.refresh_listbox(self.wordlist_listbox, self.settings["wordlists"])
            self.save_settings()

    def select_rules(self):
        paths = filedialog.askopenfilenames(title="Select Rules", filetypes=[("Rules","*.rule *.txt"),("All","*.*")])
        if paths:
            self.settings.setdefault("rules", [])
            for p in paths:
                if self._check_extension(p, "rules") and p not in self.settings["rules"]:
                    self.settings["rules"].append(p)
            self.refresh_listbox(self.rule_listbox, self.settings["rules"])
            self.save_settings()

    # Listbox refreshers
    def refresh_listbox(self, listbox, items):
        listbox.delete(0, END)
        for item in items:
            listbox.insert(END, item)

    def refresh_all_listboxes(self):
        self.refresh_listbox(self.hash_listbox, self.settings.get("hash_files", []))
        self.refresh_listbox(self.wordlist_listbox, self.settings.get("wordlists", []))
        self.refresh_listbox(self.rule_listbox, self.settings.get("rules", []))

    # Remove entries
    def remove_selected(self, listbox, key):
        for i in reversed(listbox.curselection()):
            listbox.delete(i)
            del self.settings[key][i]
        self.save_settings()

    def remove_all(self, listbox, key):
        listbox.delete(0, END)
        self.settings[key] = []
        self.save_settings()

    # Settings I/O
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE) as f:
                self.settings = json.load(f)
        else:
            self.settings = {}

    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(self.settings, f)

    # Session Restore
    def check_resume_session(self):
        restore_file = f"{SESSION_NAME}.restore"
        if os.path.exists(restore_file) and messagebox.askyesno("Resume?", "Resume previous session?"):
            self.run_restore()

    def run_restore(self):
        args = ["hashcat", "--session", SESSION_NAME, "--restore"]
        if sys.platform.startswith('win'):
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            self.process = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE, universal_newlines=True,
                creationflags=creationflags
            )
        else:
            self.process = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid
            )
        threading.Thread(target=self._reader_thread, daemon=True).start()

        # New Session
    def new_session(self):
        if messagebox.askyesno("New Session", "Clear existing session?"):
            # Stop running hashcat session via hashcat restore mechanism
            try:
                subprocess.call(["hashcat", "--session", SESSION_NAME, "--stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            # Kill any remaining hashcat processes in this session group
            if self.process and self.process.poll() is None:
                try:
                    if sys.platform.startswith('win'):
                        try:
                            self.process.send_signal(signal.CTRL_BREAK_EVENT)
                        except Exception:
                            self.process.terminate()
                    else:
                        os.killpg(self.process.pid, signal.SIGINT)
                except Exception:
                    self.process.terminate()
            # Also pkill by session name as fallback (Unix only)
            if not sys.platform.startswith('win'):
                try:
                    subprocess.call(["pkill", "-f", f"hashcat.*--session {SESSION_NAME}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass

            # Clear job queue and UI
            self.jobs.clear()
            self.current_job = None
            self.output_text.delete('1.0', END)

            # Remove previous results file
            od = self.settings.get("output_dir", "results")
            rf = os.path.join(od, "results.txt")
            if os.path.exists(rf): os.remove(rf)

            # Reset selections
            for key in ("hash_files", "wordlists", "rules"): 
                self.settings[key] = []
            self.refresh_all_listboxes()

            # Reset control buttons
            self.pause_btn.config(state=DISABLED)
            self.resume_btn.config(state=DISABLED)
            self.cancel_btn.pack_forget()

            # Remove session restore/log files
            for f in (f"{SESSION_NAME}.restore", f"{SESSION_NAME}.log"): 
                if os.path.exists(f): os.remove(f)
            self.save_settings()

    # Job loading & execution
    def load_jobs_from_hashes(self):
        self.jobs.clear()
        hashes = self.settings.get("hash_files", [])
        if not hashes:
            messagebox.showwarning("No Hash Files", "Select at least one hash file.")
            return
        self.output_text.delete('1.0', END)
        self.settings.update({
            "hash_mode": self.hashmode_var.get(),
            "workload": self.workload_var.get(),
            "attack_mode": self.attack_var.get(),
            "devices": self.device_var.get(),
            "slow_candidates": self._to_bool(self.slow_var.get())
        })
        self.save_settings()
        for hf in hashes:
            self.jobs.append({
                "hashes": [hf],
                "wordlists": self.settings.get("wordlists", []),
                "rules": self.settings.get("rules", []),
                "workload": self.settings.get("workload"),
                "attack_mode": self.settings.get("attack_mode", "0"),
                "devices": self.settings.get("devices"),
                "output_dir": self.settings.get("output_dir", "results"),
                "hash_mode": self.settings.get("hash_mode"),
                "slow_candidates": self._to_bool(self.settings.get("slow_candidates"))
            })
        self.pause_btn.config(state=DISABLED)
        self.resume_btn.config(state=DISABLED)
        self.run_next_job()

    def run_next_job(self):
        if not self.jobs and not (self.process and self.process.poll() is None):
            self.export_results({"output_dir": self.settings.get("output_dir", "results")})
        if not self.jobs and not (self.process and self.process.poll() is None):
            self.cancel_btn.pack_forget()
        if self.jobs:
            self.current_job = self.jobs.pop(0)
            self.run_hashcat(self.current_job)
            self.pause_btn.config(state=NORMAL)
            self.resume_btn.config(state=DISABLED)
        else:
            self.pause_btn.config(state=DISABLED)
            self.resume_btn.config(state=DISABLED)

    def run_hashcat(self, job):
        self.cancelled_current = False
        args = ["hashcat", "-m", job["hash_mode"], "-a", job.get("attack_mode", "0")]
        if job["slow_candidates"]:
            args.append("-S")
        args += job["hashes"] + job["wordlists"]
        for r in job["rules"]: args += ["-r", r]
        args += ["--workload-profile", job["workload"]]
        for d in job["devices"].split(','): args += ["-D", d]
        args += ["--session", SESSION_NAME]
        if sys.platform.startswith('win'):
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            self.process = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE, universal_newlines=True,
                creationflags=creationflags
            )
        else:
            self.process = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE, universal_newlines=True, preexec_fn=os.setsid
            )
        threading.Thread(target=self._reader_thread, daemon=True).start()
        self.cancel_btn.pack(side=RIGHT, padx=5, pady=5)

    def _reader_thread(self):
        while True:
            try:
                line = self.process.stdout.readline()
            except ValueError:
                break
            if not line:
                break
            self.output_text.insert(END, line)
            self.output_text.see(END)
        self.process.wait()
        if self.cancelled_current:
            self.cancelled_current = False
            return
        self.cancel_btn.pack_forget()
        if not self.jobs and not (self.process and self.process.poll() is None):
            self.export_results({"output_dir": self.settings.get("output_dir", "results")})
        else:
            self.run_next_job()

    def export_results(self, job):
        od = job.get("output_dir", "results")
        os.makedirs(od, exist_ok=True)
        path = os.path.join(od, "results.txt")
        with open(path, 'a') as f:
            f.write(self.output_text.get('1.0', END))
        self.open_results_file(path)

    def open_results_file(self, path):
        try:
            if sys.platform.startswith('win'): os.startfile(path)
            elif sys.platform.startswith('darwin'): subprocess.Popen(['open', path])
            else: subprocess.Popen(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def pause_job(self):
        if self.process and self.process.poll() is None:
            try:
                # Hashcat interactive: 'p' = pause
                self.process.stdin.write("p")
                self.process.stdin.flush()
                self.pause_btn.config(state=DISABLED)
                self.resume_btn.config(state=NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to pause: {e}")

    def resume_job(self):
        if self.process and self.process.poll() is None:
            try:
                # Hashcat interactive: 'r' = resume
                self.process.stdin.write("r")
                self.process.stdin.flush()
                self.pause_btn.config(state=NORMAL)
                self.resume_btn.config(state=DISABLED)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to resume: {e}")

    def cancel_job(self):
        if self.process and self.process.poll() is None:
            try:
                if sys.platform.startswith('win'):
                    try:
                        # Graceful interrupt for console apps started with CREATE_NEW_PROCESS_GROUP
                        self.process.send_signal(signal.CTRL_BREAK_EVENT)
                    except Exception:
                        self.process.terminate()
                else:
                    os.killpg(self.process.pid, signal.SIGINT)
            except Exception:
                self.process.terminate()
        self.cancelled_current = True
        self.cancel_btn.pack_forget()
        self.pause_btn.config(state=DISABLED)
        self.resume_btn.config(state=DISABLED)

    def confirm_exit(self):
        if messagebox.askyesno("Exit?", "Really exit and stop all sessions?"):
            # Stop any running hashcat session gracefully
            try:
                subprocess.call(["hashcat", "--session", SESSION_NAME, "--stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

            # Interrupt any active process owned by this GUI
            if self.process and self.process.poll() is None:
                try:
                    if sys.platform.startswith('win'):
                        try:
                            self.process.send_signal(signal.CTRL_BREAK_EVENT)
                        except Exception:
                            self.process.terminate()
                    else:
                        os.killpg(self.process.pid, signal.SIGINT)
                except Exception:
                    self.process.terminate()

            # As a final safety on Unix, also kill any lingering processes of this named session
            if not sys.platform.startswith('win'):
                try:
                    subprocess.call(["pkill", "-f", f"hashcat.*--session {SESSION_NAME}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass

            # Clear queues and state
            self.jobs.clear()
            self.current_job = None
            self.cancelled_current = True

            # Remove session restore/log files
            for f in (f"{SESSION_NAME}.restore", f"{SESSION_NAME}.log"):
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception:
                        pass

            # Disable controls to reflect shutdown
            self.pause_btn.config(state=DISABLED)
            self.resume_btn.config(state=DISABLED)
            self.cancel_btn.pack_forget()

            # Persist settings and exit
            self.save_settings()
            self.root.quit()
            sys.exit(0)

    def _check_extension(self, path, key):
        lst = self.allowed_extensions.get(key)
        return True if lst is None else os.path.splitext(path)[1].lower() in lst

    def register_drag_and_drop(self, listbox, key):
        listbox.drop_target_register(DND_FILES)
        def drop(event):
            for f in self.root.tk.splitlist(event.data):
                if os.path.isfile(f) and self._check_extension(f, key) and f not in self.settings.setdefault(key, []):
                    self.settings[key].append(f)
            self.refresh_listbox(listbox, self.settings[key])
            self.save_settings()
        listbox.dnd_bind('<<Drop>>', drop)
    def on_slow_toggle(self):
        """Persist checkbox state immediately and ensure it toggles reliably."""
        try:
            val = bool(int(self.slow_var.get()))
        except Exception:
            val = self._to_bool(self.slow_var.get())
        self.settings["slow_candidates"] = val
        self.save_settings()

    # Utility: strict boolean coercion for settings/UI values
    def _to_bool(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, (int,)):
            return bool(value)
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        return False

if __name__ == "__main__":
    show_splash()
    launch_hashbash_gui()
