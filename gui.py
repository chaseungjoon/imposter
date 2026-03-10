from __future__ import annotations

import customtkinter as ctk
import random
from wordgen import initiate


# ── Theme & Colors ──────────────────────────────────────────────────────────
BG            = "#111111"
SURFACE       = "#1e1e1e"
CARD          = "#262626"
CARD_HOVER    = "#2f2f2f"
CARD_SELECTED = "#1a3a5c"
PRIMARY       = "#4a9eff"
PRIMARY_HOVER = "#6bb3ff"
TEXT          = "#f0f0f0"
TEXT_DIM      = "#888888"
WORD_COLOR    = "#00e5ff"
DANGER        = "#ff4d6a"
IMPOSTER_RED  = "#ff3b3b"
CIVILIAN_BLUE = "#4a9eff"
SUCCESS       = "#2dd4a8"
GOLD          = "#ffd700"
SILVER        = "#c0c0c0"
BRONZE        = "#cd7f32"
BORDER        = "#333333"
ENTRY_BG      = "#1a1a1a"
FONT_FAMILY   = "Helvetica"


# ── Helper ──────────────────────────────────────────────────────────────────

def _bind_recursive(widget, event, callback):
    """Bind an event to a widget and all its descendants."""
    widget.bind(event, callback)
    for child in widget.winfo_children():
        _bind_recursive(child, event, callback)


# ═══════════════════════════════════════════════════════════════════════════
class ImposterApp(ctk.CTk):
    """Full imposter game with voting, scoring and leaderboard."""

    def __init__(self):
        super().__init__()

        # ── Window ──────────────────────────────────────────────────────
        self.title("IMPOSTER")
        self.geometry("520x720")
        self.minsize(480, 660)
        self.configure(fg_color=BG)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── Game state ──────────────────────────────────────────────────
        self.player_names: list[str] = []
        self.player_words: list[str] = []
        self.imp_player_idx: int = -1
        self.imp_word: str = ""
        self.civ_word: str = ""
        self.current_reveal_idx: int = 0
        self.speaking_order: list[int] = []

        # ── Voting state ────────────────────────────────────────────────
        self.votes: dict[str, str] = {}      # voter_name → voted_for_name
        self.current_voter_idx: int = 0
        self.selected_vote: str | None = None

        # ── Scoring (persists across rounds) ────────────────────────────
        self.scores: dict[str, int] = {}

        # ── Container ──────────────────────────────────────────────────
        self.container = ctk.CTkFrame(self, fg_color=BG)
        self.container.pack(fill="both", expand=True)

        self._show_main_menu()

    # ── Generic helpers ─────────────────────────────────────────────────
    def _clear(self):
        for child in self.container.winfo_children():
            child.destroy()

    # =====================================================================
    #  SCREEN 1 — Main Menu
    # =====================================================================
    def _show_main_menu(self):
        self._clear()

        wrapper = ctk.CTkFrame(self.container, fg_color=BG)
        wrapper.pack(fill="both", expand=True, padx=40, pady=(40, 30))

        ctk.CTkLabel(
            wrapper, text="IMPOSTER", font=(FONT_FAMILY, 42, "bold"),
            text_color=TEXT
        ).pack(pady=(20, 4))
        ctk.CTkLabel(
            wrapper, text="pass & play word game",
            font=(FONT_FAMILY, 13), text_color=TEXT_DIM
        ).pack(pady=(0, 30))

        # ── Player entry ────────────────────────────────────────────────
        input_frame = ctk.CTkFrame(wrapper, fg_color=SURFACE, corner_radius=14)
        input_frame.pack(fill="x", pady=(0, 14))
        input_inner = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_inner.pack(fill="x", padx=18, pady=16)

        ctk.CTkLabel(
            input_inner, text="Add Player",
            font=(FONT_FAMILY, 13, "bold"), text_color=TEXT_DIM, anchor="w"
        ).pack(fill="x")

        entry_row = ctk.CTkFrame(input_inner, fg_color="transparent")
        entry_row.pack(fill="x", pady=(8, 0))

        self.name_entry = ctk.CTkEntry(
            entry_row, placeholder_text="Enter name…", height=40,
            corner_radius=10, fg_color=ENTRY_BG, border_color=BORDER,
            border_width=1, text_color=TEXT, font=(FONT_FAMILY, 14)
        )
        self.name_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.name_entry.bind("<Return>", lambda e: self._add_player())

        ctk.CTkButton(
            entry_row, text="+", width=40, height=40, corner_radius=10,
            font=(FONT_FAMILY, 20, "bold"), fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER, command=self._add_player
        ).pack(side="right")

        # ── Player list ─────────────────────────────────────────────────
        list_frame = ctk.CTkFrame(wrapper, fg_color=SURFACE, corner_radius=14)
        list_frame.pack(fill="both", expand=True, pady=(0, 14))

        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.pack(fill="x", padx=18, pady=(14, 6))
        ctk.CTkLabel(
            list_header, text="Players",
            font=(FONT_FAMILY, 13, "bold"), text_color=TEXT_DIM, anchor="w"
        ).pack(side="left")
        self.player_count_label = ctk.CTkLabel(
            list_header, text="0", font=(FONT_FAMILY, 13, "bold"),
            text_color=PRIMARY, anchor="e"
        )
        self.player_count_label.pack(side="right")

        self.player_list_frame = ctk.CTkScrollableFrame(
            list_frame, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=TEXT_DIM
        )
        self.player_list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.empty_label = ctk.CTkLabel(
            self.player_list_frame, text="No players added yet",
            font=(FONT_FAMILY, 13), text_color=TEXT_DIM
        )
        self.empty_label.pack(pady=20)

        self.error_label = ctk.CTkLabel(
            wrapper, text="", font=(FONT_FAMILY, 12),
            text_color=DANGER, anchor="w"
        )
        self.error_label.pack(fill="x", pady=(0, 4))

        self.start_btn = ctk.CTkButton(
            wrapper, text="Start Game", height=48, corner_radius=12,
            font=(FONT_FAMILY, 16, "bold"), fg_color=CARD,
            hover_color=CARD_HOVER, text_color=TEXT_DIM, state="disabled",
            command=self._start_game
        )
        self.start_btn.pack(fill="x")

    # ── Menu helpers ────────────────────────────────────────────────────
    def _add_player(self):
        name = self.name_entry.get().strip()
        self.error_label.configure(text="")
        if not name:
            self.error_label.configure(text="Name cannot be empty.")
            return
        if name in self.player_names:
            self.error_label.configure(text=f"'{name}' is already in the game.")
            return
        if len(self.player_names) >= 12:
            self.error_label.configure(text="Maximum 12 players.")
            return
        self.player_names.append(name)
        self.name_entry.delete(0, "end")
        self._refresh_player_list()

    def _remove_player(self, name: str):
        if name in self.player_names:
            self.player_names.remove(name)
        self._refresh_player_list()

    def _refresh_player_list(self):
        for child in self.player_list_frame.winfo_children():
            child.destroy()

        count = len(self.player_names)
        self.player_count_label.configure(text=str(count))

        if count == 0:
            ctk.CTkLabel(
                self.player_list_frame, text="No players added yet",
                font=(FONT_FAMILY, 13), text_color=TEXT_DIM
            ).pack(pady=20)

        for idx, name in enumerate(self.player_names):
            row = ctk.CTkFrame(
                self.player_list_frame, fg_color=CARD,
                corner_radius=10, height=42
            )
            row.pack(fill="x", pady=3)
            row.pack_propagate(False)
            ctk.CTkLabel(
                row, text=str(idx + 1), width=28,
                font=(FONT_FAMILY, 12, "bold"), text_color=PRIMARY,
                fg_color=ENTRY_BG, corner_radius=6
            ).pack(side="left", padx=(10, 8), pady=6)
            ctk.CTkLabel(
                row, text=name, font=(FONT_FAMILY, 14),
                text_color=TEXT, anchor="w"
            ).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(
                row, text="✕", width=30, height=28, corner_radius=6,
                font=(FONT_FAMILY, 13), fg_color="transparent",
                hover_color=SURFACE, text_color=TEXT_DIM,
                command=lambda n=name: self._remove_player(n)
            ).pack(side="right", padx=8)

        if count >= 3:
            self.start_btn.configure(
                state="normal", fg_color=PRIMARY,
                hover_color=PRIMARY_HOVER, text_color="#ffffff"
            )
        else:
            self.start_btn.configure(
                state="disabled", fg_color=CARD,
                hover_color=CARD_HOVER, text_color=TEXT_DIM
            )

    def _start_game(self):
        if len(self.player_names) < 3:
            return
        for name in self.player_names:
            if name not in self.scores:
                self.scores[name] = 0
        self._new_round()

    def _new_round(self):
        """Generate fresh words and begin the word-reveal phase."""
        count = len(self.player_names)
        try:
            result = initiate(count)
        except Exception as e:
            self._show_error_screen(str(e))
            return
        self.player_words = result[0]
        self.imp_player_idx = result[1]
        self.imp_word = result[2]
        self.civ_word = result[3]
        self.current_reveal_idx = 0
        self.votes = {}
        self.current_voter_idx = 0
        self.selected_vote = None
        self._show_word_reveal()

    def _show_error_screen(self, error_msg: str):
        """Show an API error with a retry button."""
        self._clear()
        wrapper = ctk.CTkFrame(self.container, fg_color=BG)
        wrapper.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkFrame(wrapper, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkLabel(
            wrapper, text="⚠", font=(FONT_FAMILY, 52)
        ).pack(pady=(0, 8))
        ctk.CTkLabel(
            wrapper, text="API Error",
            font=(FONT_FAMILY, 28, "bold"), text_color=DANGER
        ).pack(pady=(0, 12))

        err_frame = ctk.CTkFrame(wrapper, fg_color=SURFACE, corner_radius=12)
        err_frame.pack(fill="x", pady=(0, 24))
        ctk.CTkLabel(
            err_frame, text=error_msg, font=(FONT_FAMILY, 12),
            text_color=TEXT_DIM, wraplength=380, justify="left"
        ).pack(padx=16, pady=14)

        ctk.CTkFrame(wrapper, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkButton(
            wrapper, text="Retry", height=48, corner_radius=12,
            font=(FONT_FAMILY, 15, "bold"),
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#ffffff",
            command=self._new_round
        ).pack(fill="x")

    # =====================================================================
    #  SCREEN 2 — Word Reveal (pass-and-play)
    # =====================================================================
    def _show_word_reveal(self):
        self._clear()
        idx = self.current_reveal_idx
        name = self.player_names[idx]

        wrapper = ctk.CTkFrame(self.container, fg_color=BG)
        wrapper.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(
            wrapper, text=f"{idx + 1} / {len(self.player_names)}",
            font=(FONT_FAMILY, 13), text_color=TEXT_DIM
        ).pack(pady=(20, 0))

        pbar_bg = ctk.CTkFrame(wrapper, fg_color=BORDER, height=4, corner_radius=2)
        pbar_bg.pack(fill="x", pady=(10, 40))
        pbar_bg.pack_propagate(False)
        pct = (idx + 1) / len(self.player_names)
        ctk.CTkFrame(pbar_bg, fg_color=PRIMARY, corner_radius=2).place(
            relx=0, rely=0, relwidth=pct, relheight=1.0
        )

        ctk.CTkFrame(wrapper, fg_color="transparent").pack(fill="both", expand=True)

        center = ctk.CTkFrame(wrapper, fg_color="transparent")
        center.pack()

        ctk.CTkLabel(
            center, text=name,
            font=(FONT_FAMILY, 38, "bold"), text_color=TEXT
        ).pack(pady=(0, 12))

        self.word_label = ctk.CTkLabel(
            center, text="tap to reveal your word",
            font=(FONT_FAMILY, 15), text_color=TEXT_DIM
        )
        self.word_label.pack(pady=(0, 28))

        self.action_frame = ctk.CTkFrame(center, fg_color="transparent")
        self.action_frame.pack()

        self.reveal_btn = ctk.CTkButton(
            self.action_frame, text="Reveal", width=180, height=52,
            corner_radius=14, font=(FONT_FAMILY, 17, "bold"),
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
            command=lambda: self._reveal_word(idx)
        )
        self.reveal_btn.pack()

        ctk.CTkFrame(wrapper, fg_color="transparent").pack(fill="both", expand=True)

    def _reveal_word(self, idx: int):
        word = self.player_words[idx]
        self.word_label.configure(
            text=word, font=(FONT_FAMILY, 48, "bold"),
            text_color=WORD_COLOR
        )
        self.reveal_btn.destroy()
        ctk.CTkButton(
            self.action_frame, text="OK", width=180, height=52,
            corner_radius=14, font=(FONT_FAMILY, 17, "bold"),
            fg_color=CARD, hover_color=CARD_HOVER, text_color=TEXT,
            command=self._next_player
        ).pack()

    def _next_player(self):
        self.current_reveal_idx += 1
        if self.current_reveal_idx < len(self.player_names):
            self._show_word_reveal()
        else:
            self._show_turn_order()

    # =====================================================================
    #  SCREEN 3 — Speaking Order
    # =====================================================================
    def _show_turn_order(self):
        self._clear()

        indices = list(range(len(self.player_names)))
        random.shuffle(indices)
        self.speaking_order = indices

        wrapper = ctk.CTkFrame(self.container, fg_color=BG)
        wrapper.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(
            wrapper, text="Speaking Order",
            font=(FONT_FAMILY, 32, "bold"), text_color=TEXT
        ).pack(pady=(24, 4))
        ctk.CTkLabel(
            wrapper, text="each player says one word per round",
            font=(FONT_FAMILY, 13), text_color=TEXT_DIM
        ).pack(pady=(0, 30))

        card_container = ctk.CTkScrollableFrame(
            wrapper, fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=TEXT_DIM
        )
        card_container.pack(fill="both", expand=True, pady=(0, 20))

        cols = 3
        for c in range(cols):
            card_container.columnconfigure(c, weight=1, uniform="col")

        for order_num, player_idx in enumerate(self.speaking_order):
            r = order_num // cols
            c = order_num % cols
            card = ctk.CTkFrame(
                card_container, fg_color=CARD, corner_radius=14,
                border_width=1, border_color=BORDER
            )
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=16, pady=18)
            badge = ctk.CTkFrame(
                inner, fg_color=PRIMARY, width=36, height=36, corner_radius=18
            )
            badge.pack()
            badge.pack_propagate(False)
            ctk.CTkLabel(
                badge, text=str(order_num + 1),
                font=(FONT_FAMILY, 15, "bold"), text_color="#ffffff"
            ).place(relx=0.5, rely=0.5, anchor="center")
            ctk.CTkLabel(
                inner, text=self.player_names[player_idx],
                font=(FONT_FAMILY, 14, "bold"), text_color=TEXT
            ).pack(pady=(10, 0))

        btn_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        btn_row.pack(fill="x")

        ctk.CTkButton(
            btn_row, text="Play Again", height=48, corner_radius=12,
            font=(FONT_FAMILY, 15, "bold"),
            fg_color=CARD, hover_color=CARD_HOVER, text_color=TEXT,
            command=self._new_round
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            btn_row, text="Vote", height=48, corner_radius=12,
            font=(FONT_FAMILY, 15, "bold"),
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#ffffff",
            command=self._start_voting
        ).pack(side="right", fill="x", expand=True, padx=(6, 0))

    # =====================================================================
    #  SCREEN 4 — Voting (pass-and-play, speaking order)
    # =====================================================================
    def _start_voting(self):
        self.votes = {}
        self.current_voter_idx = 0
        self._show_vote_screen()

    def _show_vote_screen(self):
        self._clear()
        self.selected_vote = None

        voter_player_idx = self.speaking_order[self.current_voter_idx]
        voter_name = self.player_names[voter_player_idx]

        wrapper = ctk.CTkFrame(self.container, fg_color=BG)
        wrapper.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(
            wrapper,
            text=f"Vote {self.current_voter_idx + 1} / {len(self.player_names)}",
            font=(FONT_FAMILY, 13), text_color=TEXT_DIM
        ).pack(pady=(10, 0))

        pbar_bg = ctk.CTkFrame(wrapper, fg_color=BORDER, height=4, corner_radius=2)
        pbar_bg.pack(fill="x", pady=(10, 20))
        pbar_bg.pack_propagate(False)
        pct = (self.current_voter_idx + 1) / len(self.player_names)
        ctk.CTkFrame(pbar_bg, fg_color=PRIMARY, corner_radius=2).place(
            relx=0, rely=0, relwidth=pct, relheight=1.0
        )

        ctk.CTkLabel(
            wrapper, text=f"{voter_name}'s Vote",
            font=(FONT_FAMILY, 28, "bold"), text_color=TEXT
        ).pack(pady=(0, 4))
        ctk.CTkLabel(
            wrapper, text="select who you think is the imposter",
            font=(FONT_FAMILY, 13), text_color=TEXT_DIM
        ).pack(pady=(0, 20))

        card_container = ctk.CTkScrollableFrame(
            wrapper, fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=TEXT_DIM
        )
        card_container.pack(fill="both", expand=True, pady=(0, 14))

        cols = 3
        for c in range(cols):
            card_container.columnconfigure(c, weight=1, uniform="col")

        self.vote_cards: dict[str, ctk.CTkFrame] = {}
        grid_idx = 0
        for pidx, name in enumerate(self.player_names):
            if pidx == voter_player_idx:
                continue
            r = grid_idx // cols
            c = grid_idx % cols
            grid_idx += 1

            card = ctk.CTkFrame(
                card_container, fg_color=CARD, corner_radius=14,
                border_width=2, border_color=BORDER
            )
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=16, pady=18)

            avatar = ctk.CTkFrame(
                inner, fg_color=SURFACE, width=40, height=40, corner_radius=20
            )
            avatar.pack()
            avatar.pack_propagate(False)
            ctk.CTkLabel(
                avatar, text=name[0].upper(),
                font=(FONT_FAMILY, 16, "bold"), text_color=TEXT_DIM
            ).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(
                inner, text=name,
                font=(FONT_FAMILY, 13, "bold"), text_color=TEXT
            ).pack(pady=(8, 0))

            self.vote_cards[name] = card
            _bind_recursive(card, "<Button-1>", lambda e, n=name: self._select_vote(n))

        self.vote_submit_btn = ctk.CTkButton(
            wrapper, text="Submit Vote", height=48, corner_radius=12,
            font=(FONT_FAMILY, 15, "bold"),
            fg_color=CARD, hover_color=CARD_HOVER, text_color=TEXT_DIM,
            state="disabled",
            command=lambda: self._submit_vote(voter_name)
        )
        self.vote_submit_btn.pack(fill="x")

    def _select_vote(self, name: str):
        self.selected_vote = name
        for card_name, card in self.vote_cards.items():
            if card_name == name:
                card.configure(border_color=PRIMARY, fg_color=CARD_SELECTED)
            else:
                card.configure(border_color=BORDER, fg_color=CARD)
        self.vote_submit_btn.configure(
            state="normal", fg_color=PRIMARY,
            hover_color=PRIMARY_HOVER, text_color="#ffffff"
        )

    def _submit_vote(self, voter_name: str):
        if self.selected_vote is None:
            return
        self.votes[voter_name] = self.selected_vote
        self.current_voter_idx += 1
        if self.current_voter_idx < len(self.player_names):
            self._show_vote_screen()
        else:
            self._show_vote_result()

    # =====================================================================
    #  SCREEN 5 — Vote Result (revealed immediately)
    # =====================================================================
    def _show_vote_result(self):
        self._clear()

        # Tally
        vote_counts: dict[str, int] = {}
        for voted_for in self.votes.values():
            vote_counts[voted_for] = vote_counts.get(voted_for, 0) + 1

        max_votes = max(vote_counts.values())
        tied = [n for n, c in vote_counts.items() if c == max_votes]

        # ── DRAW ────────────────────────────────────────────────────────
        if len(tied) > 1:
            self._show_draw_screen(tied, max_votes)
            return

        most_voted_name = tied[0]
        most_voted_idx = self.player_names.index(most_voted_name)
        is_imposter = (most_voted_idx == self.imp_player_idx)

        # Store for later scoring
        self._most_voted_name = most_voted_name
        self._most_voted_is_imposter = is_imposter

        wrapper = ctk.CTkFrame(self.container, fg_color=BG)
        wrapper.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(
            wrapper, text="Most Voted",
            font=(FONT_FAMILY, 32, "bold"), text_color=TEXT
        ).pack(pady=(20, 4))
        ctk.CTkLabel(
            wrapper, text=f"{max_votes} vote{'s' if max_votes != 1 else ''}",
            font=(FONT_FAMILY, 14), text_color=TEXT_DIM
        ).pack(pady=(0, 10))

        # Top spacer
        ctk.CTkFrame(wrapper, fg_color="transparent").pack(fill="both", expand=True)

        # Card — already revealed, centered vertically
        role_color = IMPOSTER_RED if is_imposter else CIVILIAN_BLUE
        role_text = "IMPOSTER" if is_imposter else "CIVILIAN"

        card_frame = ctk.CTkFrame(
            wrapper, fg_color=CARD, corner_radius=20,
            border_width=2, border_color=role_color
        )
        card_frame.pack()

        card_inner = ctk.CTkFrame(card_frame, fg_color="transparent")
        card_inner.pack(padx=36, pady=30)

        avatar = ctk.CTkFrame(
            card_inner, fg_color=SURFACE, width=56, height=56, corner_radius=28
        )
        avatar.pack()
        avatar.pack_propagate(False)
        ctk.CTkLabel(
            avatar, text=most_voted_name[0].upper(),
            font=(FONT_FAMILY, 22, "bold"), text_color=TEXT_DIM
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card_inner, text=most_voted_name,
            font=(FONT_FAMILY, 20, "bold"), text_color=TEXT
        ).pack(pady=(14, 10))

        ctk.CTkLabel(
            card_inner, text=role_text,
            font=(FONT_FAMILY, 24, "bold"), text_color=role_color
        ).pack()

        # Bottom spacer
        ctk.CTkFrame(wrapper, fg_color="transparent").pack(fill="both", expand=True)

        # Continue button pinned at bottom
        if is_imposter:
            ctk.CTkButton(
                wrapper, text="Continue", height=48, corner_radius=12,
                font=(FONT_FAMILY, 15, "bold"),
                fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#ffffff",
                command=self._show_imposter_guess
            ).pack(fill="x")
        else:
            self._apply_scores_imposter_wins()
            ctk.CTkButton(
                wrapper, text="Continue", height=48, corner_radius=12,
                font=(FONT_FAMILY, 15, "bold"),
                fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#ffffff",
                command=self._show_leaderboard
            ).pack(fill="x")

    # ── DRAW screen ─────────────────────────────────────────────────────
    def _show_draw_screen(self, tied: list[str], votes: int):
        self._clear()

        wrapper = ctk.CTkFrame(self.container, fg_color=BG)
        wrapper.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkFrame(wrapper, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkLabel(
            wrapper, text="⚔️", font=(FONT_FAMILY, 60)
        ).pack(pady=(0, 8))
        ctk.CTkLabel(
            wrapper, text="DRAW!",
            font=(FONT_FAMILY, 40, "bold"), text_color="#d4a5ff"
        ).pack(pady=(0, 10))
        ctk.CTkLabel(
            wrapper, text=f"{', '.join(tied)} tied with {votes} vote{'s' if votes != 1 else ''} each",
            font=(FONT_FAMILY, 14), text_color=TEXT_DIM,
            wraplength=360, justify="center"
        ).pack(pady=(0, 10))

        ctk.CTkFrame(wrapper, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkButton(
            wrapper, text="Re-Vote", height=52, corner_radius=12,
            font=(FONT_FAMILY, 16, "bold"),
            fg_color="#6c2bd9", hover_color="#8344e8", text_color="#ffffff",
            command=self._start_revote
        ).pack(fill="x")

    def _start_revote(self):
        """Reset votes and go back to voting."""
        self.votes.clear()
        self.current_voter_idx = 0
        self.selected_vote = None
        self._show_vote_screen()

    # =====================================================================
    #  SCREEN 5.5 — Imposter Guess (only when imposter is caught)
    # =====================================================================
    def _show_imposter_guess(self):
        self._clear()
        imp_name = self.player_names[self.imp_player_idx]

        wrapper = ctk.CTkFrame(self.container, fg_color=BG)
        wrapper.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkFrame(wrapper, fg_color="transparent").pack(fill="both", expand=True)

        ctk.CTkLabel(
            wrapper, text="🎯", font=(FONT_FAMILY, 52)
        ).pack(pady=(0, 8))
        ctk.CTkLabel(
            wrapper, text="Guess the\nCivilian's Word!",
            font=(FONT_FAMILY, 30, "bold"), text_color=TEXT,
            justify="center"
        ).pack(pady=(0, 10))
        ctk.CTkLabel(
            wrapper, text=f"{imp_name}, say your guess out loud",
            font=(FONT_FAMILY, 14), text_color=TEXT_DIM
        ).pack(pady=(0, 40))

        btn_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        btn_row.pack(fill="x")

        ctk.CTkButton(
            btn_row, text="Wrong", height=52, corner_radius=12,
            font=(FONT_FAMILY, 16, "bold"),
            fg_color="#3a1c1c", hover_color="#5a2c2c", text_color=DANGER,
            command=self._imposter_guess_wrong
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            btn_row, text="Correct", height=52, corner_radius=12,
            font=(FONT_FAMILY, 16, "bold"),
            fg_color="#1c3a1c", hover_color="#2c5a2c", text_color=SUCCESS,
            command=self._imposter_guess_correct
        ).pack(side="right", fill="x", expand=True, padx=(6, 0))

        ctk.CTkFrame(wrapper, fg_color="transparent").pack(fill="both", expand=True)

    def _imposter_guess_correct(self):
        imp_name = self.player_names[self.imp_player_idx]
        self.scores[imp_name] = self.scores.get(imp_name, 0) + 5
        self._show_leaderboard()

    def _imposter_guess_wrong(self):
        for i, name in enumerate(self.player_names):
            if i != self.imp_player_idx:
                self.scores[name] = self.scores.get(name, 0) + 7
        self._show_leaderboard()

    # ── Scoring helpers ─────────────────────────────────────────────────
    def _apply_scores_imposter_wins(self):
        """Civilian voted most → imposter wins."""
        imp_name = self.player_names[self.imp_player_idx]
        self.scores[imp_name] = self.scores.get(imp_name, 0) + 10
        for voter_name, voted_for_name in self.votes.items():
            if voted_for_name == imp_name:
                self.scores[voter_name] = self.scores.get(voter_name, 0) + 7

    # =====================================================================
    #  SCREEN 6 — Leaderboard
    # =====================================================================
    def _show_leaderboard(self):
        self._clear()

        wrapper = ctk.CTkFrame(self.container, fg_color=BG)
        wrapper.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(
            wrapper, text="Leaderboard",
            font=(FONT_FAMILY, 32, "bold"), text_color=TEXT
        ).pack(pady=(24, 24))

        sorted_players = sorted(
            self.player_names,
            key=lambda n: self.scores.get(n, 0),
            reverse=True
        )

        medal_map = {0: ("🥇", GOLD), 1: ("🥈", SILVER), 2: ("🥉", BRONZE)}

        list_frame = ctk.CTkScrollableFrame(
            wrapper, fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=TEXT_DIM
        )
        list_frame.pack(fill="both", expand=True, pady=(0, 20))

        for rank, name in enumerate(sorted_players):
            score = self.scores.get(name, 0)

            border_clr = BORDER
            if rank == 0:
                border_clr = GOLD
            elif rank == 1:
                border_clr = SILVER
            elif rank == 2:
                border_clr = BRONZE

            row = ctk.CTkFrame(
                list_frame, fg_color=CARD, corner_radius=12,
                height=56, border_width=1, border_color=border_clr
            )
            row.pack(fill="x", pady=4)
            row.pack_propagate(False)

            if rank in medal_map:
                medal_text, _ = medal_map[rank]
                ctk.CTkLabel(
                    row, text=medal_text, font=(FONT_FAMILY, 22), width=44
                ).pack(side="left", padx=(14, 2))
            else:
                ctk.CTkLabel(
                    row, text=f"#{rank + 1}",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=TEXT_DIM, width=44
                ).pack(side="left", padx=(14, 2))

            ctk.CTkLabel(
                row, text=name, font=(FONT_FAMILY, 16, "bold"),
                text_color=TEXT, anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=(6, 0))

            ctk.CTkLabel(
                row, text=str(score), font=(FONT_FAMILY, 18, "bold"),
                text_color=PRIMARY
            ).pack(side="right", padx=18)

        btn_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        btn_row.pack(fill="x")

        ctk.CTkButton(
            btn_row, text="Quit", height=48, corner_radius=12,
            font=(FONT_FAMILY, 15, "bold"),
            fg_color=CARD, hover_color=CARD_HOVER, text_color=TEXT,
            command=self.destroy
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            btn_row, text="Keep Playing", height=48, corner_radius=12,
            font=(FONT_FAMILY, 15, "bold"),
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#ffffff",
            command=self._new_round
        ).pack(side="right", fill="x", expand=True, padx=(6, 0))


# ═══════════════════════════════════════════════════════════════════════════

def launch():
    app = ImposterApp()
    app.mainloop()


if __name__ == "__main__":
    launch()
