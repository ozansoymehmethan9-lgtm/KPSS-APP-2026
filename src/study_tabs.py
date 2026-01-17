import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, date
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import DB_FILE

class StudyTabsMixin:
    # ---- 2. PROGRESS ----
    def build_progress_tab(self):
        self.tab_progress.grid_columnconfigure(0, weight=1)
        self.tab_progress.grid_columnconfigure(1, weight=1)
        self.tab_progress.grid_rowconfigure(1, weight=1)
        
        frm_add = ctk.CTkFrame(self.tab_progress)
        frm_add.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.combo_ders = ctk.CTkComboBox(frm_add, values=["Türkçe", "Matematik", "Geometri", "Tarih", "Coğrafya", "Vatandaşlık", "Eğitim Bilimleri", "Alan Bilgisi"])
        self.combo_ders.pack(side="left", padx=5)
        self.ent_konu = ctk.CTkEntry(frm_add, placeholder_text="Konu Adı", width=200)
        self.ent_konu.pack(side="left", padx=5)
        ctk.CTkButton(frm_add, text="Konu Ekle", command=self.add_subject).pack(side="left", padx=5)
        
        # Split Trees
        ctk.CTkLabel(self.tab_progress, text="Genel Yetenek (GY)", font=("Roboto", 16, "bold")).grid(row=1, column=0, sticky="w", padx=10)
        self.tree_gy = ttk.Treeview(self.tab_progress, columns=("ders", "konu", "durum"), show="headings")
        self.tree_gy.heading("ders", text="Ders"); self.tree_gy.heading("konu", text="Konu"); self.tree_gy.heading("durum", text="Durum")
        self.tree_gy.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        ctk.CTkLabel(self.tab_progress, text="Genel Kültür (GK)", font=("Roboto", 16, "bold")).grid(row=1, column=1, sticky="w", padx=10)
        self.tree_gk = ttk.Treeview(self.tab_progress, columns=("ders", "konu", "durum"), show="headings")
        self.tree_gk.heading("ders", text="Ders"); self.tree_gk.heading("konu", text="Konu"); self.tree_gk.heading("durum", text="Durum")
        self.tree_gk.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")
        
        act_frame = ctk.CTkFrame(self.tab_progress)
        act_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ctk.CTkButton(act_frame, text="✅ Tamamlandı", fg_color="green", command=lambda: self.update_prog_status("Tamamlandı")).pack(side="left", padx=5)
        ctk.CTkButton(act_frame, text="⏳ Devam Ediyor", fg_color="orange", command=lambda: self.update_prog_status("Devam Ediyor")).pack(side="left", padx=5)
        ctk.CTkButton(act_frame, text="❌ Başlanmadı", fg_color="gray", command=lambda: self.update_prog_status("Başlanmadı")).pack(side="left", padx=5)
        ctk.CTkButton(act_frame, text="🗑 Sil", fg_color="red", command=self.delete_prog_subject).pack(side="left", padx=5)
        
        self.load_progress_trees()

    def add_subject(self):
        d = self.combo_ders.get(); k = self.ent_konu.get()
        if not k: return
        GY = ["Türkçe", "Matematik", "Geometri", "Mantık"]
        kat = "GY" if d in GY else "GK"
        conn = sqlite3.connect(DB_FILE); conn.execute("INSERT INTO subjects (ders, konu, durum, kategori) VALUES (?,?,?,?)", (d, k, "Başlanmadı", kat)); conn.commit(); conn.close()
        self.ent_konu.delete(0, "end"); self.load_progress_trees()

    def update_prog_status(self, new_status):
        sel = self.tree_gy.selection() or self.tree_gk.selection()
        if not sel: return
        sid = int(sel[0])
        conn = sqlite3.connect(DB_FILE); conn.execute("UPDATE subjects SET durum = ? WHERE id = ?", (new_status, sid)); conn.commit(); conn.close()
        self.load_progress_trees()

    def delete_prog_subject(self):
        sel = self.tree_gy.selection() or self.tree_gk.selection()
        if not sel: return
        sid = int(sel[0])
        conn = sqlite3.connect(DB_FILE); conn.execute("DELETE FROM subjects WHERE id = ?", (sid,)); conn.commit(); conn.close()
        self.load_progress_trees()

    def load_progress_trees(self):
        from database import load_all_from_db
        self.data = load_all_from_db()
        for i in self.tree_gy.get_children(): self.tree_gy.delete(i)
        for i in self.tree_gk.get_children(): self.tree_gk.delete(i)
        for s in self.data["subjects"]:
            target = self.tree_gy if s["kategori"] == "GY" else self.tree_gk
            target.insert("", "end", iid=str(s["id"]), values=(s["ders"], s["konu"], s["durum"]))

    def log_event(self, msg):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO logs (tarih, olay) VALUES (?,?)",
            (datetime.now().isoformat(), msg))
        conn.commit(); conn.close()

    # ---- 4. HEDEFLER ----
    def build_goals_tab(self):
        self.tab_goals.grid_columnconfigure(0, weight=1); self.tab_goals.grid_rowconfigure(1, weight=1)
        frm = ctk.CTkFrame(self.tab_goals); frm.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.combo_goal_type = ctk.CTkComboBox(frm, values=["Günlük", "Haftalık"]); self.combo_goal_type.pack(side="left", padx=5)
        self.ent_goal_ders = ctk.CTkEntry(frm, placeholder_text="Ders"); self.ent_goal_ders.pack(side="left", padx=5)
        self.ent_goal_target = ctk.CTkEntry(frm, placeholder_text="Hedef", width=80); self.ent_goal_target.pack(side="left", padx=5)
        self.ent_goal_done = ctk.CTkEntry(frm, placeholder_text="Çözülen", width=80); self.ent_goal_done.pack(side="left", padx=5)
        ctk.CTkButton(frm, text="Hedef Ekle", command=self.add_goal).pack(side="left", padx=5)
        self.tree_goals = ttk.Treeview(self.tab_goals, columns=("tip", "ders", "hedef", "cozulen", "durum"), show="headings")
        self.tree_goals.heading("tip", text="Tip"); self.tree_goals.heading("ders", text="Ders"); self.tree_goals.heading("hedef", text="Hedef"); self.tree_goals.heading("cozulen", text="Çözülen"); self.tree_goals.heading("durum", text="Durum")
        self.tree_goals.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        act = ctk.CTkFrame(self.tab_goals); act.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.ent_goal_upd = ctk.CTkEntry(act, placeholder_text="Yeni Çözülen", width=120); self.ent_goal_upd.pack(side="left", padx=5)
        ctk.CTkButton(act, text="Güncelle", command=self.update_goal_progress).pack(side="left", padx=5)
        ctk.CTkButton(act, text="Sil", fg_color="red", command=self.delete_goal).pack(side="right", padx=5)
        self.load_goals()

    def add_goal(self):
        t = self.combo_goal_type.get(); d = self.ent_goal_ders.get()
        try: h = int(self.ent_goal_target.get()); c = int(self.ent_goal_done.get() or 0)
        except: return
        conn = sqlite3.connect(DB_FILE); conn.execute("INSERT INTO goals (tip, tarih, ders, hedef_soru, cozulen) VALUES (?,?,?,?,?)", (t, date.today().isoformat(), d, h, c)); conn.commit(); conn.close(); self.load_goals(); self.update_summary()

    def load_goals(self):
        from database import load_all_from_db
        self.data = load_all_from_db()
        for i in self.tree_goals.get_children(): self.tree_goals.delete(i)
        for g in self.data["goals"]:
            percent = (g["cozulen"] / g["hedef_soru"] * 100) if g["hedef_soru"] > 0 else 0
            self.tree_goals.insert("", "end", iid=str(g["id"]), values=(g["tip"], g["ders"], g["hedef_soru"], g["cozulen"], f"%{int(percent)}"))

    def update_goal_progress(self):
        sel = self.tree_goals.selection()
        if not sel: return
        gid = int(sel[0])
        try: val = int(self.ent_goal_upd.get())
        except: return
        conn = sqlite3.connect(DB_FILE); conn.execute("UPDATE goals SET cozulen = ? WHERE id = ?", (val, gid)); conn.commit(); conn.close(); self.ent_goal_upd.delete(0, "end"); self.load_goals(); self.update_summary()

    def delete_goal(self):
        sel = self.tree_goals.selection()
        if not sel: return
        gid = int(sel[0]); conn = sqlite3.connect(DB_FILE); conn.execute("DELETE FROM goals WHERE id=?", (gid,)); conn.commit(); conn.close(); self.load_goals(); self.update_summary()

    # ---- 5. TESTS ----
    def build_tests_tab(self):
        self.tab_tv_tests = ctk.CTkTabview(self.tab_tests)
        self.tab_tv_tests.pack(fill="both", expand=True)
        t_sub_konu = self.tab_tv_tests.add("Konu Testleri")
        t_sub_deneme = self.tab_tv_tests.add("Genel Denemeler")
        self.build_konu_tests_ui(t_sub_konu)
        self.build_denemeler_ui(t_sub_deneme)

    def build_konu_tests_ui(self, parent):
        parent.grid_columnconfigure(0, weight=1); parent.grid_rowconfigure(1, weight=1)
        frm = ctk.CTkFrame(parent); frm.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.ent_test_ders = ctk.CTkEntry(frm, placeholder_text="Ders/Konu"); self.ent_test_ders.pack(side="left", padx=5)
        self.ent_test_d = ctk.CTkEntry(frm, placeholder_text="D", width=50); self.ent_test_d.pack(side="left", padx=5)
        self.ent_test_y = ctk.CTkEntry(frm, placeholder_text="Y", width=50); self.ent_test_y.pack(side="left", padx=5)
        ctk.CTkButton(frm, text="Ekle", command=self.add_test).pack(side="left", padx=5)
        self.tree_tests = ttk.Treeview(parent, columns=("tarih", "ders", "dy", "net"), show="headings")
        self.tree_tests.heading("tarih", text="Tarih"); self.tree_tests.heading("ders", text="Ders"); self.tree_tests.heading("dy", text="D/Y"); self.tree_tests.heading("net", text="Net")
        self.tree_tests.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        ctk.CTkButton(parent, text="Sil", fg_color="red", command=self.delete_test).grid(row=2, column=0, pady=5, sticky="e", padx=10)
        self.load_tests()

    def build_denemeler_ui(self, parent):
        parent.grid_columnconfigure(0, weight=1); parent.grid_columnconfigure(1, weight=1); parent.grid_rowconfigure(0, weight=1)
        lp = ctk.CTkFrame(parent); lp.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        f = ctk.CTkFrame(lp); f.pack(fill="x", pady=5)
        self.ent_tr_d_date = ctk.CTkEntry(f, placeholder_text=str(date.today()), width=90); self.ent_tr_d_date.grid(row=0, column=0, padx=2, pady=2)
        labs = ["Türkçe", "Matematik", "Tarih", "Coğrafya", "Vatandaşlık"]; self.trial_entries = {}
        for i, l in enumerate(labs, 1):
            ctk.CTkLabel(f, text=l, font=("Arial", 10)).grid(row=i, column=0, sticky="e")
            d = ctk.CTkEntry(f, width=40, placeholder_text="D"); d.grid(row=i, column=1, padx=2)
            y = ctk.CTkEntry(f, width=40, placeholder_text="Y"); y.grid(row=i, column=2, padx=2)
            self.trial_entries[l] = (d, y)
        ctk.CTkButton(f, text="Deneme Kaydet", command=self.save_trial).grid(row=6, column=0, columnspan=3, pady=5)
        self.tree_trials = ttk.Treeview(lp, columns=("id", "tarih", "net"), show="headings", height=12)
        self.tree_trials.heading("tarih", text="Tarih"); self.tree_trials.heading("net", text="Net"); self.tree_trials.column("id", width=0, stretch=False)
        self.tree_trials.pack(fill="both", expand=True, pady=5); self.tree_trials.bind("<<TreeviewSelect>>", self.on_trial_select)
        ctk.CTkButton(lp, text="Sil", fg_color="red", command=self.delete_trial).pack(pady=5)
        rp = ctk.CTkFrame(parent); rp.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.fig_trial, self.ax_trial = plt.subplots(figsize=(4, 3), dpi=90); self.canvas_trial = FigureCanvasTkAgg(self.fig_trial, master=rp); self.canvas_trial.get_tk_widget().pack(fill="both", expand=True)
        self.load_trials()

    def add_test(self):
        dn = self.ent_test_ders.get()
        try: d, y = int(self.ent_test_d.get()), int(self.ent_test_y.get())
        except: return
        n = d - (y/4); conn = sqlite3.connect(DB_FILE); conn.execute("INSERT INTO tests (tarih, ders, dogru, yanlis, net, yuzde, is_deneme) VALUES (?,?,?,?,?,?,?)", (date.today().isoformat(), dn, d, y, n, 0, 0)); conn.commit(); conn.close(); self.load_tests(); self.update_summary()

    def load_tests(self):
        from database import load_all_from_db
        self.data = load_all_from_db()
        for i in self.tree_tests.get_children(): self.tree_tests.delete(i)
        for t in self.data["tests"]:
            if not t["is_deneme"]: self.tree_tests.insert("", "end", iid=str(t["id"]), values=(t["tarih"], t["ders"], f"{t['dogru']}/{t['yanlis']}", f"{t['net']:.2f}"))

    def delete_test(self):
        sel = self.tree_tests.selection()
        if not sel: return
        tid = int(sel[0]); conn = sqlite3.connect(DB_FILE); conn.execute("DELETE FROM tests WHERE id=?", (tid,)); conn.commit(); conn.close(); self.load_tests(); self.update_summary()

    def save_trial(self):
        dt = self.ent_tr_d_date.get() or date.today().isoformat()
        res = {}; tn = 0
        try:
            for l, (ed, ey) in self.trial_entries.items(): d, y = int(ed.get() or 0), int(ey.get() or 0); res[l] = (d, y); tn += d - (y/4)
        except: return
        conn = sqlite3.connect(DB_FILE)
        if hasattr(self, 'editing_trial_id') and self.editing_trial_id: conn.execute("DELETE FROM trials WHERE id=?", (self.editing_trial_id,))
        conn.execute("INSERT INTO trials (tarih, turkce_d, turkce_y, mat_d, mat_y, tarih_d, tarih_y, cog_d, cog_y, vat_d, vat_y, toplam_net) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (dt, res["Türkçe"][0], res["Türkçe"][1], res["Matematik"][0], res["Matematik"][1], res["Tarih"][0], res["Tarih"][1], res["Coğrafya"][0], res["Coğrafya"][1], res["Vatandaşlık"][0], res["Vatandaşlık"][1], tn))
        conn.commit(); conn.close(); self.editing_trial_id = None; self.load_trials(); self.update_summary()

    def load_trials(self):
        from database import load_all_from_db
        self.data = load_all_from_db()
        for i in self.tree_trials.get_children(): self.tree_trials.delete(i)
        dates, nets = [], []
        for t in self.data["trials"]:
            self.tree_trials.insert("", "end", iid=str(t["id"]), values=(t["id"], t["tarih"], f"{t['toplam_net']:.2f}")); dates.append(t["tarih"]); nets.append(t["toplam_net"])
        self.ax_trial.clear()
        if dates: self.ax_trial.plot(dates, nets, marker='o', color='green'); self.ax_trial.tick_params(axis='x', rotation=45, labelsize=8)
        self.canvas_trial.draw()

    def on_trial_select(self, e):
        sel = self.tree_trials.selection()
        if not sel: return
        tid = int(sel[0]); self.editing_trial_id = tid; res = next((x for x in self.data["trials"] if x["id"]==tid), None)
        if res:
            self.ent_tr_d_date.delete(0, "end"); self.ent_tr_d_date.insert(0, res["tarih"])
            m = {"Türkçe": ("turkce_d", "turkce_y"), "Matematik": ("mat_d", "mat_y"), "Tarih": ("tarih_d", "tarih_y"), "Coğrafya": ("cog_d", "cog_y"), "Vatandaşlık": ("vat_d", "vat_y")}
            for l, (dk, yk) in m.items(): ed, ey = self.trial_entries[l]; ed.delete(0, "end"); ed.insert(0, res[dk]); ey.delete(0, "end"); ey.insert(0, res[yk])

    def delete_trial(self):
        sel = self.tree_trials.selection()
        if not sel: return
        tid = int(sel[0]); conn = sqlite3.connect(DB_FILE); conn.execute("DELETE FROM trials WHERE id=?", (tid,)); conn.commit(); conn.close(); self.load_trials(); self.update_summary()

    # ---- 6. NET CALC ----
    def build_net_calculator_tab(self):
        card = ctk.CTkFrame(self.tab_net, corner_radius=15); card.pack(fill="both", expand=True, padx=40, pady=40)
        ctk.CTkLabel(card, text="KPSS Lisans Puan Hesapla", font=("Roboto", 24, "bold"), text_color="#1976d2").pack(pady=20)
        f = ctk.CTkFrame(card, fg_color="transparent"); f.pack(pady=10)
        headers = ["Bölüm", "D", "Y", "Net"]
        for i, h in enumerate(headers): ctk.CTkLabel(f, text=h, font=("Roboto", 14, "bold")).grid(row=0, column=i, padx=20)
        rows = [("GY (60)", "gy"), ("GK (60)", "gk"), ("Eğitim (80)", "eb")]
        self.net_entries, self.net_labels = {}, {}
        for idx, (t, k) in enumerate(rows, 1):
            ctk.CTkLabel(f, text=t, font=("Roboto", 12)).grid(row=idx, column=0, sticky="w", padx=20, pady=10)
            d = ctk.CTkEntry(f, width=70, placeholder_text="0"); d.grid(row=idx, column=1, padx=10)
            y = ctk.CTkEntry(f, width=70, placeholder_text="0"); y.grid(row=idx, column=2, padx=10)
            l = ctk.CTkLabel(f, text="0.00", font=("Roboto", 14, "bold")); l.grid(row=idx, column=3, padx=10)
            self.net_entries[k] = (d, y); self.net_labels[k] = l
        ctk.CTkButton(card, text="HESAPLA", width=200, height=40, command=self.calc_net).pack(pady=20)
        self.lbl_p3 = ctk.CTkLabel(card, text="P3: -", font=("Roboto", 22, "bold")); self.lbl_p3.pack()
        self.lbl_p10 = ctk.CTkLabel(card, text="P10: -", font=("Roboto", 18, "bold")); self.lbl_p10.pack()

    def calc_net(self):
        r = {}
        for k in ["gy", "gk", "eb"]:
            d, y = int(self.net_entries[k][0].get() or 0), int(self.net_entries[k][1].get() or 0); n = d - y/4; r[k] = n; self.net_labels[k].configure(text=f"{n:.2f}")
        p3 = min(100, 55 + (r["gy"]*0.41) + (r["gk"]*0.38)); p10 = min(100, 42 + (r["gy"]*0.3) + (r["gk"]*0.3) + (r["eb"]*0.4))
        self.lbl_p3.configure(text=f"P3: {p3:.3f}"); self.lbl_p10.configure(text=f"P10: {p10:.3f}")
