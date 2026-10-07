"""Modern Tkinter desktop interface for Pokemon team optimization."""

from __future__ import annotations

import queue
import threading
from pathlib import Path
from typing import Any

from .instances import load_instance, predefined_instance_paths
from .solver import SolveSummary, solve_problem


def launch_gui() -> None:
    """Open the Pokemon-inspired visual solver using the standard library."""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError as error:
        raise RuntimeError("The visual interface requires Tkinter.") from error

    c = {
        "navy": "#D90B32", "dark": "#520817", "blue": "#22A7E8",
        "yellow": "#FFD429", "red": "#0C6657", "red2": "#084A40",
        "shell": "#D90B32", "shell_dark": "#8E071F", "black": "#17191B",
        "bg": "#720518", "card": "#E9ECEF", "surface": "#F8FAF9",
        "border": "#25282B", "text": "#172033", "muted": "#59636D",
        "green": "#16835A", "green_bg": "#E7F7F0",
        "amber": "#9A6700", "amber_bg": "#FFF6D8",
        "error": "#B42318", "error_bg": "#FDECEA",
    }
    type_colors = {
        "Normal": "#92999F", "Fire": "#E76F51", "Water": "#3F83D1",
        "Electric": "#D9A918", "Grass": "#58A65C", "Ice": "#55B8C1",
        "Fighting": "#B4534B", "Poison": "#9656A1", "Ground": "#B98A52",
        "Flying": "#7189C7", "Psychic": "#D95F83", "Bug": "#7E9C3A",
        "Rock": "#9B8652", "Ghost": "#665A91", "Dragon": "#5866B2",
        "Dark": "#5B5361", "Steel": "#71879A", "Fairy": "#D878A5",
    }

    class App:
        def __init__(self, root: Any) -> None:
            self.root = root
            root.title("Pokémon Team Optimizer")
            # Kept below common 1366x768 / 125%-scaled desktop bounds.
            root.geometry("1040x680")
            root.minsize(860, 540)
            root.configure(bg=c["bg"])
            self.results: queue.Queue[tuple[str, object]] = queue.Queue()
            self._style()
            self._variables()
            self._header()
            self._layout()
            self._toggle_fields()
            self._welcome()
            root.after(100, self._poll)

        def _style(self) -> None:
            style = ttk.Style(self.root)
            style.theme_use("clam")
            for name in ("Modern.TCombobox", "Modern.TEntry"):
                style.configure(
                    name, fieldbackground=c["surface"], foreground=c["text"],
                    bordercolor=c["border"], lightcolor=c["border"],
                    darkcolor=c["border"], arrowcolor=c["navy"], padding=8,
                )
            style.map(
                "Modern.TCombobox",
                fieldbackground=[("readonly", c["surface"])],
                selectbackground=[("readonly", c["surface"])],
                selectforeground=[("readonly", c["text"])],
            )

        def _variables(self) -> None:
            labels = {
                "small_12": "Small  ·  12 candidates",
                "medium_20": "Medium  ·  20 candidates",
                "medium_30": "Medium  ·  30 candidates",
                "large_50": "Large  ·  50 candidates",
                "xlarge_100": "Extra large  ·  100 candidates",
            }
            self.paths = {labels[p.stem]: p for p in predefined_instance_paths()}
            self.instance = tk.StringVar(value=next(iter(self.paths)))
            self.algorithm = tk.StringVar(value="Simulated Annealing")
            self.seed = tk.StringVar(value="1")
            self.temp = tk.StringVar(value="10.0")
            self.alpha = tk.StringVar(value="0.995")
            self.minimum = tk.StringVar(value="0.0001")
            self.iterations = tk.StringVar(value="20000")
            self.brute_limit = tk.StringVar(value="30")
            self.status = tk.StringVar(value="Ready to optimize")

        def _header(self) -> None:
            canvas = tk.Canvas(
                self.root, height=108, bg=c["navy"], highlightthickness=0
            )
            canvas.pack(fill="x")

            def draw(event: Any) -> None:
                w = event.width
                canvas.delete("all")
                canvas.create_rectangle(0, 0, w, 108, fill=c["shell"], outline="")
                canvas.create_polygon(
                    0, 86, w * .30, 86, w * .39, 32, w, 32, w, 108, 0, 108,
                    fill=c["shell_dark"], outline=c["dark"], width=3,
                )
                canvas.create_text(
                    128, 56, anchor="w", text="PKO-DEX",
                    fill="white", font=("Consolas", 22, "bold"),
                )
                canvas.create_text(
                    130, 78, anchor="w", text="DEFENSIVE TEAM ANALYSIS SYSTEM",
                    fill="#FFD9DF", font=("Consolas", 9, "bold"),
                )
                canvas.create_oval(22, 12, 98, 88, fill="#D9EFF7", outline=c["dark"], width=4)
                canvas.create_oval(29, 19, 91, 81, fill="#087CB8", outline="#073A59", width=3)
                canvas.create_oval(39, 26, 62, 49, fill="#66D2FF", outline="")
                canvas.create_oval(45, 30, 55, 40, fill="#D8F6FF", outline="")
                for x, fill in ((108, "#ED2939"), (130, c["yellow"]), (152, "#3EBB62")):
                    canvas.create_oval(x, 13, x + 14, 27, fill=fill, outline=c["dark"], width=2)

            canvas.bind("<Configure>", draw)

        def _card(self, parent: Any) -> Any:
            return tk.Frame(
                parent, bg=c["card"], highlightbackground=c["black"],
                highlightthickness=5, padx=16, pady=14,
            )

        def _scrollable_card(self, parent: Any) -> tuple[Any, Any]:
            """Return a device panel whose contents remain usable when short."""
            shell = tk.Frame(
                parent, bg=c["card"], highlightbackground=c["black"],
                highlightthickness=5,
            )
            scrollbar = ttk.Scrollbar(shell, orient="vertical")
            canvas = tk.Canvas(
                shell, bg=c["card"], highlightthickness=0,
                yscrollcommand=scrollbar.set,
            )
            scrollbar.configure(command=canvas.yview)
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)

            inner = tk.Frame(canvas, bg=c["card"], padx=16, pady=14)
            window = canvas.create_window((0, 0), window=inner, anchor="nw")

            def update_region(_event: Any = None) -> None:
                canvas.configure(scrollregion=canvas.bbox("all"))

            def fit_width(event: Any) -> None:
                canvas.itemconfigure(window, width=event.width)
                update_region()

            def scroll(event: Any) -> None:
                canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

            inner.bind("<Configure>", update_region)
            canvas.bind("<Configure>", fit_width)
            canvas.bind(
                "<Enter>", lambda _event: self.root.bind_all("<MouseWheel>", scroll)
            )
            canvas.bind(
                "<Leave>", lambda _event: self.root.unbind_all("<MouseWheel>")
            )
            return shell, inner

        def _layout(self) -> None:
            content = tk.Frame(self.root, bg=c["shell"], padx=16, pady=14)
            content.pack(fill="both", expand=True)
            content.grid_columnconfigure(0, minsize=350, weight=4)
            content.grid_columnconfigure(1, minsize=30)
            content.grid_columnconfigure(2, weight=7)
            content.grid_rowconfigure(0, weight=1)
            settings_shell, self.settings = self._scrollable_card(content)
            settings_shell.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
            hinge = tk.Frame(
                content, bg=c["shell_dark"], highlightbackground=c["dark"],
                highlightthickness=3,
            )
            hinge.grid(row=0, column=1, sticky="ns", padx=2)
            for y in (.08, .47, .86):
                tk.Frame(hinge, bg=c["black"], height=5, width=22).place(
                    relx=.5, rely=y, anchor="center"
                )
            self.results_card = self._card(content)
            self.results_card.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
            self._settings_panel()
            self._results_panel()

        def _title(self, parent: Any, number: str, text: str, row: int) -> None:
            tk.Label(
                parent, text=number, bg=c["yellow"], fg=c["dark"],
                font=("Segoe UI", 9, "bold"), width=2, pady=2,
            ).grid(row=row, column=0, sticky="w", pady=(5, 7))
            tk.Label(
                parent, text=text, bg=c["card"], fg=c["text"],
                font=("Segoe UI", 11, "bold"),
            ).grid(
                row=row, column=0, columnspan=3, sticky="w",
                padx=(38, 0), pady=(5, 7),
            )

        def _settings_panel(self) -> None:
            p = self.settings
            for column in range(3):
                p.grid_columnconfigure(column, weight=1)
            tk.Label(
                p, text="TRAINER INPUT", bg=c["card"], fg=c["text"],
                font=("Consolas", 16, "bold"),
            ).grid(row=0, column=0, columnspan=3, sticky="w")
            tk.Label(
                p, text="Configure candidate scan parameters.",
                bg=c["card"], fg=c["muted"], font=("Segoe UI", 9),
            ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 10))

            self._title(p, "1", "Problem instance", 2)
            self.instance_box = ttk.Combobox(
                p, textvariable=self.instance, values=tuple(self.paths),
                state="readonly", style="Modern.TCombobox", font=("Segoe UI", 10),
            )
            self.instance_box.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(0, 5))
            tk.Button(
                p, text="Browse", command=self._browse, bg=c["blue"], fg="white",
                activebackground=c["border"], relief="flat", bd=0, padx=10, pady=8,
                font=("Segoe UI", 9, "bold"), cursor="hand2",
            ).grid(row=3, column=2, sticky="ew", padx=(5, 0))

            self._title(p, "2", "Search algorithm", 4)
            self.algorithm_box = ttk.Combobox(
                p, textvariable=self.algorithm,
                values=("Simulated Annealing", "Exact Brute Force"),
                state="readonly", style="Modern.TCombobox", font=("Segoe UI", 10),
            )
            self.algorithm_box.grid(row=5, column=0, columnspan=3, sticky="ew")
            self.algorithm_box.bind("<<ComboboxSelected>>", lambda _e: self._toggle_fields())

            self._title(p, "3", "Algorithm parameters", 6)
            params = tk.Frame(p, bg=c["card"])
            params.grid(row=7, column=0, columnspan=3, sticky="ew")
            params.grid_columnconfigure(0, weight=1)
            params.grid_columnconfigure(1, weight=1)
            fields = (
                ("SEED", self.seed, 0, 0), ("INITIAL TEMPERATURE", self.temp, 0, 1),
                ("COOLING RATE", self.alpha, 2, 0),
                ("MINIMUM TEMPERATURE", self.minimum, 2, 1),
                ("MAXIMUM ITERATIONS", self.iterations, 4, 0),
                ("BRUTE-FORCE LIMIT", self.brute_limit, 4, 1),
            )
            self.sa_entries, self.brute_entries = [], []
            for label, variable, row, column in fields:
                tk.Label(
                    params, text=label, bg=c["card"], fg=c["muted"],
                    font=("Segoe UI", 8, "bold"),
                ).grid(row=row, column=column, sticky="w", pady=(4, 2))
                entry = ttk.Entry(
                    params, textvariable=variable, style="Modern.TEntry",
                    font=("Segoe UI", 10),
                )
                entry.grid(
                    row=row + 1, column=column, sticky="ew",
                    padx=(0, 5) if column == 0 else (5, 0),
                )
                (self.brute_entries if label == "BRUTE-FORCE LIMIT" else self.sa_entries).append(entry)

            tk.Frame(p, bg=c["border"], height=1).grid(
                row=8, column=0, columnspan=3, sticky="ew", pady=(12, 10)
            )
            self.solve_button = tk.Button(
                p, text="▶  START TEAM SCAN", command=self._start, bg=c["red"], fg="white",
                activebackground=c["red2"], activeforeground="white", relief="flat",
                bd=0, padx=16, pady=10, font=("Segoe UI", 10, "bold"), cursor="hand2",
            )
            self.solve_button.grid(row=9, column=0, columnspan=3, sticky="ew")
            self.status_label = tk.Label(
                p, textvariable=self.status, bg=c["green_bg"], fg=c["green"],
                font=("Segoe UI", 9, "bold"), pady=6,
            )
            self.status_label.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        def _results_panel(self) -> None:
            header = tk.Frame(self.results_card, bg=c["card"])
            header.pack(fill="x")
            tk.Label(
                header, text="TEAM DATABASE", bg=c["card"], fg=c["text"],
                font=("Consolas", 16, "bold"),
            ).pack(side="left")
            self.badge = tk.Label(
                header, text="WAITING", bg=c["surface"], fg=c["muted"],
                font=("Segoe UI", 8, "bold"), padx=10, pady=4,
            )
            self.badge.pack(side="right")
            self.body = tk.Frame(self.results_card, bg=c["card"])
            self.body.pack(fill="both", expand=True, pady=(14, 0))

        def _clear(self) -> None:
            for child in self.body.winfo_children():
                child.destroy()

        def _pokeball(self, parent: Any) -> None:
            icon = tk.Canvas(parent, width=86, height=86, bg=c["card"], highlightthickness=0)
            icon.pack(pady=(0, 12))
            icon.create_arc(8, 8, 78, 78, start=0, extent=180, fill=c["red"], outline=c["dark"], width=3)
            icon.create_arc(8, 8, 78, 78, start=180, extent=180, fill="white", outline=c["dark"], width=3)
            icon.create_line(9, 43, 77, 43, fill=c["dark"], width=6)
            icon.create_oval(33, 33, 53, 53, fill="white", outline=c["dark"], width=4)

        def _welcome(self) -> None:
            self._clear()
            frame = tk.Frame(self.body, bg=c["card"])
            frame.place(relx=.5, rely=.45, anchor="center")
            self._pokeball(frame)
            tk.Label(
                frame, text="Your optimized team will appear here", bg=c["card"],
                fg=c["text"], font=("Segoe UI", 13, "bold"),
            ).pack()
            tk.Label(
                frame, text="Configure a run, then select Optimize Team.",
                bg=c["card"], fg=c["muted"], font=("Segoe UI", 9),
            ).pack(pady=(5, 0))

        def _loading(self) -> None:
            self._clear()
            frame = tk.Frame(self.body, bg=c["card"])
            frame.place(relx=.5, rely=.45, anchor="center")
            tk.Label(
                frame, text="Searching the solution space…", bg=c["card"],
                fg=c["navy"], font=("Segoe UI", 14, "bold"),
            ).pack()
            tk.Label(
                frame, text="Exploring valid six-Pokémon combinations",
                bg=c["card"], fg=c["muted"], font=("Segoe UI", 9),
            ).pack(pady=(6, 0))

        def _metric(self, parent: Any, label: str, value: str, column: int) -> None:
            tile = tk.Frame(
                parent, bg=c["black"], highlightbackground="#59636D",
                highlightthickness=2, padx=12, pady=9,
            )
            tile.grid(row=0, column=column, sticky="nsew", padx=4)
            tk.Label(tile, text=label, bg=c["black"], fg="#7FDBFF", font=("Consolas", 8, "bold")).pack(anchor="w")
            tk.Label(tile, text=value, bg=c["black"], fg="#B9F18C", font=("Consolas", 14, "bold")).pack(anchor="w", pady=(3, 0))

        def _render(self, result: SolveSummary) -> None:
            self._clear()
            name = "Simulated Annealing" if result.algorithm == "sa" else "Exact Brute Force"
            tk.Label(
                self.body, text=result.instance_name.replace("_", " ").title(),
                bg=c["card"], fg=c["text"], font=("Segoe UI", 13, "bold"),
            ).pack(anchor="w")
            tk.Label(
                self.body, text=f"{name}  ·  {result.n} candidates",
                bg=c["card"], fg=c["muted"], font=("Segoe UI", 9),
            ).pack(anchor="w", pady=(2, 12))
            metrics = tk.Frame(self.body, bg=c["card"])
            metrics.pack(fill="x")
            for column in range(3):
                metrics.grid_columnconfigure(column, weight=1)
            self._metric(metrics, "BEST COST", f"{result.cost:g}", 0)
            self._metric(metrics, "AVG. MULTIPLIER", f"{result.average_multiplier:.4f}", 1)
            self._metric(metrics, "RUNTIME", f"{result.runtime_ms:.2f} ms", 2)
            tk.Label(
                self.body, text="RECOMMENDED TEAM", bg=c["card"], fg=c["muted"],
                font=("Segoe UI", 9, "bold"),
            ).pack(anchor="w", pady=(18, 8))
            grid = tk.Frame(self.body, bg=c["card"])
            grid.pack(fill="both", expand=True)
            grid.grid_columnconfigure(0, weight=1)
            grid.grid_columnconfigure(1, weight=1)
            for index, pokemon in enumerate(result.team):
                row, column = divmod(index, 2)
                tile = tk.Frame(grid, bg=c["blue"], highlightbackground=c["dark"], highlightthickness=2)
                tile.grid(row=row, column=column, sticky="nsew", padx=(0, 5) if column == 0 else (5, 0), pady=(0, 8))
                tk.Frame(tile, bg=type_colors[pokemon.type1], width=6).pack(side="left", fill="y")
                details = tk.Frame(tile, bg=c["blue"], padx=11, pady=9)
                details.pack(side="left", fill="both", expand=True)
                tk.Label(details, text=f"#{index + 1}  {pokemon.name}", bg=c["blue"], fg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w")
                types = pokemon.type1 + (f"  /  {pokemon.type2}" if pokemon.type2 else "")
                tk.Label(details, text=types.upper(), bg=c["blue"], fg="#08253A", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(3, 0))
            metadata = []
            if result.seed is not None:
                metadata.append(f"Seed {result.seed}")
            if result.iterations is not None:
                metadata.append(f"{result.iterations:,} iterations")
            if result.combinations_evaluated is not None:
                metadata.append(f"{result.combinations_evaluated:,} combinations evaluated")
            tk.Label(self.body, text="  •  ".join(metadata), bg=c["card"], fg=c["muted"], font=("Segoe UI", 8)).pack(anchor="w", pady=(5, 0))

        def _browse(self) -> None:
            chosen = filedialog.askopenfilename(
                title="Select problem instance",
                filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
            )
            if chosen:
                label = f"Custom  ·  {Path(chosen).name}"
                self.paths[label] = Path(chosen)
                self.instance_box.configure(values=tuple(self.paths))
                self.instance.set(label)

        def _toggle_fields(self) -> None:
            sa = self.algorithm.get() == "Simulated Annealing"
            for entry in self.sa_entries:
                entry.configure(state="normal" if sa else "disabled")
            for entry in self.brute_entries:
                entry.configure(state="disabled" if sa else "normal")

        def _settings(self) -> tuple[Path, str, dict[str, object]]:
            selected = self.instance.get()
            if selected not in self.paths:
                raise ValueError("Select a valid instance")
            if self.algorithm.get() == "Simulated Annealing":
                options: dict[str, object] = {
                    "seed": int(self.seed.get()), "initial_temperature": float(self.temp.get()),
                    "alpha": float(self.alpha.get()), "min_temperature": float(self.minimum.get()),
                    "max_iterations": int(self.iterations.get()),
                }
                return self.paths[selected], "sa", options
            return self.paths[selected], "brute-force", {
                "brute_force_max_candidates": int(self.brute_limit.get())
            }

        def _set_status(self, text: str, kind: str) -> None:
            styles = {
                "ok": (c["green_bg"], c["green"]),
                "work": (c["amber_bg"], c["amber"]),
                "error": (c["error_bg"], c["error"]),
            }
            bg, fg = styles[kind]
            self.status.set(text)
            self.status_label.configure(bg=bg, fg=fg)

        def _start(self) -> None:
            try:
                path, algorithm, options = self._settings()
            except ValueError as error:
                messagebox.showerror("Invalid settings", str(error))
                return
            self.solve_button.configure(state="disabled", bg="#B84A47")
            self._set_status("Searching for the best team…", "work")
            self.badge.configure(text="RUNNING", bg=c["amber_bg"], fg=c["amber"])
            self._loading()

            def worker() -> None:
                try:
                    result = solve_problem(load_instance(path), algorithm, **options)
                    self.results.put(("success", result))
                except Exception as error:
                    self.results.put(("error", error))

            threading.Thread(target=worker, daemon=True).start()

        def _poll(self) -> None:
            try:
                kind, payload = self.results.get_nowait()
            except queue.Empty:
                self.root.after(100, self._poll)
                return
            self.solve_button.configure(state="normal", bg=c["red"])
            if kind == "success" and isinstance(payload, SolveSummary):
                self._set_status("Optimization complete", "ok")
                self.badge.configure(text="COMPLETE", bg=c["green_bg"], fg=c["green"])
                self._render(payload)
            else:
                self._set_status("Unable to complete this run", "error")
                self.badge.configure(text="ERROR", bg=c["error_bg"], fg=c["error"])
                self._welcome()
                messagebox.showerror("Solve failed", str(payload))
            self.root.after(100, self._poll)

    root = tk.Tk()
    App(root)
    root.mainloop()
