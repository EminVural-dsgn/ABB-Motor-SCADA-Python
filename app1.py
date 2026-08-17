import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os
import minimalmodbus
import serial
from collections import deque
import time
import json
from tkinter import filedialog

class UltimateACS880App:
    def __init__(self, root):
        self.root = root
        self.dil = "EN"
        self.tema = "dark"
        self.root.title("ABB ACS880 Akıllı SCADA & Kontrol Sistemi")
        self.root.state('zoomed') 
        
        self.instrument = None 
        self.baglanti_aktif = False
        self.canli_okuma_aktif = False
        self.motor_calisiyor = False

        # --- LIVE GRAPH HISTORY ---
        self.max_len = 100
        self.t_start = time.time()
        self.hist_t = deque(maxlen=self.max_len)
        self.hist_u = deque(maxlen=self.max_len)
        self.hist_v = deque(maxlen=self.max_len)
        self.hist_w = deque(maxlen=self.max_len)
        self.hist_hiz = deque(maxlen=self.max_len)
        self.hist_tork = deque(maxlen=self.max_len)
        self.hist_guc = deque(maxlen=self.max_len)
        self.hist_volt = deque(maxlen=self.max_len)

        self.yukle_ayarlar()

        self.dp_kutulari = {}
        self.sw_kutulari = {}
        self.ui_widgets = []
        self.ui_tabs = []
        
        # --- TRANSLATIONS ---
        self.texts = {
            "EN": {
                "main_title": "⚡ ABB ACS880 SMART MANAGEMENT PANEL",
                "main_sub": "AGU - Power Lab | Electrical Machines",
                "card1_title": "⚙️ Communication Network",
                "card1_desc": "Modbus Master configuration.",
                "card1_btn": "CONFIGURE SETTINGS",
                "card2_title": "📊 Control & Analysis",
                "card2_desc": "LabVIEW SCADA and live charts.",
                "card2_btn": "START SYSTEM",
                "sys_status": " System Status: ",
                "offline": "🔴 Offline (Waiting for Connection)",
                "online": "🟢 Online (Active)",
                "hardware": "Hardware: ABB ACS880-11-12A6-3 ",
                "win_ctrl_title": "ACS880 LabVIEW SCADA Panel",
                "tab_ctrl": "Control Settings",
                "tab_dp": "Drive Params",
                "tab_mdp": "More Drive Params",
                "tab_sw": "Status Word",
                "lf_mode": " Drive Mode & Direction ",
                "ctrl_mode": "Control Mode:",
                "dir": "Direction:",
                "fwd": "Forward",
                "rev": "Reverse",
                "lf_params": " Parameters (Interlock Protected) ",
                "col_param": "Parameter",
                "col_target": "Target",
                "col_current": "From Drive (Current)",
                "lf_digital": " Digital Indicators (Live) ",
                "btn_live_start": "📡 START LIVE COMMUNICATION",
                "btn_live_stop": "📡 STOP LIVE COMMUNICATION",
                "lbl_speed": "Current Motor Speed:",
                "lbl_torque": "Current Motor Torque:",
                "lbl_power": "Active Power Draw:",
                "lf_oper": " Operation & Reporting ",
                "btn_start": "▶ START MOTOR",
                "btn_stop": "⏹ STOP MOTOR",
                "btn_estop": "🛑 EMERGENCY STOP",
                "btn_report": "📊 FINISH TEST & REPORT",
                "tab_chart_curr": "Phase Currents (A)",
                "tab_chart_mech": "Mechanical (RPM & Torque)",
                "tab_chart_pwr": "Power & DC Bus",
                "chart_time": "Time (s)",
                "chart_curr": "Current (A)",
                "chart_speed": "Motor Speed (RPM)",
                "chart_torque": "Motor Torque (%)",
                "chart_power": "Active Power (kW)",
                "chart_volt": "DC Bus Voltage (V)",
                "msg_start": "Motor triggered. Power circuit active!",
                "msg_stop": "Ramp Stop command sent.",
                "msg_estop": "EMERGENCY STOP Activated!",
                "msg_conn_err": "Not connected to drive!",
                "msg_conn_ok": "Connection successful via ",
                "msg_rep_ok": "Report Saved: ",
                "msg_live_start": "Live communication started.",
                "msg_live_stop": "Live communication stopped.",
                "theme": "Theme:",
                "lang": "Language:",
                "win_conn_title": "Connection Configuration",
                "conn_settings": "Modbus Master Settings",
                "save_conn": "Save & Connect",
                "Speed Ref (RPM)": "Speed Ref (RPM)",
                "Torque Ref (%)": "Torque Ref (%)",
                "Ramp UP (s)": "Ramp UP (s)",
                "Ramp DOWN (s)": "Ramp DOWN (s)",
                "DC Voltage (V)": "DC Voltage (V)",
                "Mot. Spd. Est. (RPM)": "Mot. Spd. Est. (RPM)",
                "Encoder Spd. 1 Filtered": "Encoder Spd. 1 Filtered",
                "Output Frequency (Hz)": "Output Frequency (Hz)",
                "I_mot % of Motor Nom.": "I_mot % of Motor Nom.",
                "Output Voltage": "Output Voltage",
                "Out. Pwr. % of Nom.": "Out. Pwr. % of Nom.",
                "V-phase Curr. (A)": "V-phase Curr. (A)",
                "Motor Current (A)": "Motor Current (A)",
                "Mot. Spd. Used (RPM)": "Mot. Spd. Used (RPM)",
                "Encoder Spd. 2 Filtered": "Encoder Spd. 2 Filtered",
                "Motor Speed (%)": "Motor Speed (%)",
                "Motor Torque (%)": "Motor Torque (%)",
                "Output Power": "Output Power",
                "U-phase Curr. (A)": "U-phase Curr. (A)",
                "W-phase Curr. (A)": "W-phase Curr. (A)",
                "Flux Actual (%)": "Flux Actual (%)",
                "Nominal Trq. Scale (Nm)": "Nominal Trq. Scale (Nm)",
                "Ambient Temp. (C)": "Ambient Temp. (C)",
                "U-phase Cur. RMS (A)": "U-phase Cur. RMS (A)",
                "W-phase Cur. RMS (A)": "W-phase Cur. RMS (A)",
                "INU Moment. pf": "INU Moment. pf",
                "Spd. Change Rate (RPM/s)": "Spd. Change Rate (RPM/s)",
                "Step-up Mot. Cur. (A)": "Step-up Mot. Cur. (A)",
                "V-phase Cur. RMS (A)": "V-phase Cur. RMS (A)",
                "btn_calib": "⚙️ Hardware Config",
                "win_calib_title": "Hardware Calibration Settings",
                "calib_desc": "Set the multiplier/scale factors for Modbus registers to convert them into physical units (RPM, %, A, kW, etc).",
                "save_calib": "Save Configuration"
            },
            "TR": {
                "main_title": "⚡ ABB ACS880 AKILLI YÖNETİM PANELİ",
                "main_sub": "AGÜ - Power Lab | Elektrik Makineleri",
                "card1_title": "⚙️ Haberleşme Ağı",
                "card1_desc": "Modbus Master konfigürasyonu.",
                "card1_btn": "AYARLARI YAPILANDIR",
                "card2_title": "📊 Kontrol & Analiz",
                "card2_desc": "LabVIEW SCADA ve canlı grafikler.",
                "card2_btn": "SİSTEMİ BAŞLAT",
                "sys_status": " Sistem Durumu: ",
                "offline": "🔴 Çevrimdışı (Bağlantı Bekleniyor)",
                "online": "🟢 Çevrimiçi (Aktif)",
                "hardware": "Donanım: ABB ACS880-11-12A6-3 ",
                "win_ctrl_title": "ACS880 LabVIEW SCADA Paneli",
                "tab_ctrl": "Kontrol Ayarları",
                "tab_dp": "Sürücü Parametreleri",
                "tab_mdp": "Ek Parametreler",
                "tab_sw": "Durum Sözcüğü",
                "lf_mode": " Sürüş Modu & Yön ",
                "ctrl_mode": "Kontrol Modu:",
                "dir": "Yön:",
                "fwd": "İleri",
                "rev": "Geri",
                "lf_params": " Parametreler (Interlock Korumalı) ",
                "col_param": "Parametre",
                "col_target": "Hedef",
                "col_current": "Sürücüden (Güncel)",
                "lf_digital": " Dijital Göstergeler (Canlı) ",
                "btn_live_start": "📡 CANLI HABERLEŞMEYİ BAŞLAT",
                "btn_live_stop": "📡 CANLI HABERLEŞMEYİ DURDUR",
                "lbl_speed": "Anlık Motor Hızı:",
                "lbl_torque": "Anlık Motor Torku:",
                "lbl_power": "Çekilen Aktif Güç:",
                "lf_oper": " Operasyon & Raporlama ",
                "btn_start": "▶ MOTORU BAŞLAT",
                "btn_stop": "⏹ MOTORU DURDUR",
                "btn_estop": "🛑 ACİL STOP (Serbest Duruş)",
                "btn_report": "📊 TESTİ BİTİR VE RAPORLA",
                "tab_chart_curr": "Faz Akımları (A)",
                "tab_chart_mech": "Mekanik (Hız & Tork)",
                "tab_chart_pwr": "Güç ve DC Bara",
                "chart_time": "Zaman (s)",
                "chart_curr": "Amper (A)",
                "chart_speed": "Motor Hızı (RPM)",
                "chart_torque": "Motor Torku (%)",
                "chart_power": "Aktif Güç (kW)",
                "chart_volt": "DC Bara Voltajı (V)",
                "msg_start": "Motor tetiklendi. Güç devresi aktif!",
                "msg_stop": "Ramp Stop komutu gönderildi.",
                "msg_estop": "ACİL STOP Tetiklendi!",
                "msg_conn_err": "Sürücüye bağlı değilsiniz!",
                "msg_conn_ok": "Üzerinden başarıyla bağlanıldı: ",
                "msg_rep_ok": "Rapor Kaydedildi: ",
                "msg_live_start": "Canlı haberleşme başlatıldı.",
                "msg_live_stop": "Haberleşme durduruldu.",
                "theme": "Tema:",
                "lang": "Dil:",
                "win_conn_title": "Bağlantı Konfigürasyonu",
                "conn_settings": "Modbus Master Ayarları",
                "save_conn": "Kaydet & Bağlan",
                "Speed Ref (RPM)": "Hız Referansı (RPM)",
                "Torque Ref (%)": "Tork Referansı (%)",
                "Ramp UP (s)": "Kalkış Rampası (s)",
                "Ramp DOWN (s)": "Duruş Rampası (s)",
                "DC Voltage (V)": "DC Gerilimi (V)",
                "Mot. Spd. Est. (RPM)": "Tahmini Motor Hızı (RPM)",
                "Encoder Spd. 1 Filtered": "Filtreli Enkoder Hızı 1",
                "Output Frequency (Hz)": "Çıkış Frekansı (Hz)",
                "I_mot % of Motor Nom.": "Motor Akımı (% Nominal)",
                "Output Voltage": "Çıkış Gerilimi",
                "Out. Pwr. % of Nom.": "Çıkış Gücü (% Nominal)",
                "V-phase Curr. (A)": "V-Fazı Akımı (A)",
                "Motor Current (A)": "Motor Akımı (A)",
                "Mot. Spd. Used (RPM)": "Kullanılan Motor Hızı (RPM)",
                "Encoder Spd. 2 Filtered": "Filtreli Enkoder Hızı 2",
                "Motor Speed (%)": "Motor Hızı (%)",
                "Motor Torque (%)": "Motor Torku (%)",
                "Output Power": "Çıkış Gücü",
                "U-phase Curr. (A)": "U-Fazı Akımı (A)",
                "W-phase Curr. (A)": "W-Fazı Akımı (A)",
                "Flux Actual (%)": "Gerçek Akı (%)",
                "Nominal Trq. Scale (Nm)": "Nominal Tork Skalası (Nm)",
                "Ambient Temp. (C)": "Ortam Sıcaklığı (C)",
                "U-phase Cur. RMS (A)": "U-Fazı Akımı RMS (A)",
                "W-phase Cur. RMS (A)": "W-Fazı Akımı RMS (A)",
                "INU Moment. pf": "INU Anlık pf",
                "Spd. Change Rate (RPM/s)": "Hız Değişim Oranı (RPM/s)",
                "Step-up Mot. Cur. (A)": "Step-up Motor Akımı (A)",
                "V-phase Cur. RMS (A)": "V-Fazı Akımı RMS (A)",
                "btn_calib": "⚙️ Donanım Kalibrasyonu",
                "win_calib_title": "Donanım Kalibrasyon Ayarları",
                "calib_desc": "Modbus okuma/yazma register değerlerini gerçek fiziksel birimlere (RPM, %, A, kW vb.) çevirmek için kullanılacak çarpanları ayarlayın.",
                "save_calib": "Ayarları Kaydet"
            }
        }
        
        self.sw_dict = {
            "RDY_ON": {"EN": {0: "Not Ready", 1: "Ready to Switch On"}, "TR": {0: "Hazır Değil", 1: "Açılmaya Hazır"}},
            "RDY_RUN": {"EN": {0: "Not Ready", 1: "Ready to Operate"}, "TR": {0: "Hazır Değil", 1: "Çalışmaya Hazır"}},
            "RDY_REF": {"EN": {0: "Not Ready", 1: "Operation Enabled"}, "TR": {0: "Hazır Değil", 1: "Operasyon Aktif"}},
            "TRIPPED": {"EN": {0: "No Fault", 1: "FAULT ACTIVE"}, "TR": {0: "Hata Yok", 1: "HATA AKTİF"}},
            "OFF_2_STA": {"EN": {0: "OFF2 Active", 1: "OFF2 Inactive"}, "TR": {0: "OFF2 Aktif", 1: "OFF2 Pasif"}},
            "OFF_3_STA": {"EN": {0: "OFF3 Active", 1: "OFF3 Inactive"}, "TR": {0: "OFF3 Aktif", 1: "OFF3 Pasif"}},
            "SWC_ON_INHIB": {"EN": {0: "No Inhibit", 1: "Switch-on Inhibited"}, "TR": {0: "Engel Yok", 1: "Açılma Engellendi"}},
            "ALARM": {"EN": {0: "No Warning", 1: "WARNING ACTIVE"}, "TR": {0: "Uyarı Yok", 1: "UYARI AKTİF"}},
            "AT_SETPOINT": {"EN": {0: "Not at Setpoint", 1: "At Setpoint"}, "TR": {0: "Hedefte Değil", 1: "Hedefe Ulaşıldı"}},
            "REMOTE": {"EN": {0: "Local Control", 1: "Remote Control"}, "TR": {0: "Lokal Kontrol", 1: "Uzaktan (Remote)"}},
            "ABOVE_LIMIT": {"EN": {0: "Below Limit", 1: "Above Limit"}, "TR": {0: "Limit Altı", 1: "Limit Üstü"}},
            "EXT_RUN_ENABLED": {"EN": {0: "Ext Run Disabled", 1: "Ext Run Enabled"}, "TR": {0: "Dış Çalışma Pasif", 1: "Dış Çalışma Aktif"}},
        }

        # --- SETTINGS MENU ---
        settings_frame = ttk.Frame(self.root)
        settings_frame.pack(side=TOP, anchor=NE, padx=20, pady=10)
        
        self.lbl_lang = self.create_t_widget(ttk.Label, settings_frame, "lang", font=("Segoe UI", 9))
        self.lbl_lang.pack(side=LEFT, padx=5)
        self.cb_lang = ttk.Combobox(settings_frame, values=["English", "Türkçe"], width=10, state="readonly")
        self.cb_lang.set("English")
        self.cb_lang.pack(side=LEFT, padx=5)
        self.cb_lang.bind("<<ComboboxSelected>>", self.degistir_dil)
        
        self.lbl_theme = self.create_t_widget(ttk.Label, settings_frame, "theme", font=("Segoe UI", 9))
        self.lbl_theme.pack(side=LEFT, padx=5)
        self.cb_theme = ttk.Combobox(settings_frame, values=["Dark", "Light"], width=10, state="readonly")
        self.cb_theme.set("Dark")
        self.cb_theme.pack(side=LEFT, padx=5)
        self.cb_theme.bind("<<ComboboxSelected>>", self.degistir_tema)
        
        self.btn_calib = self.create_t_widget(ttk.Button, settings_frame, "btn_calib", bootstyle=(PRIMARY, OUTLINE), command=self.pencere_kalibrasyon)
        self.btn_calib.pack(side=LEFT, padx=15)

        # --- ANA MENÜ ---
        self.center_frame = ttk.Frame(self.root)
        self.center_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        self.create_t_widget(ttk.Label, self.center_frame, "main_title", font=("Segoe UI", 36, "bold")).pack(pady=(0, 5))
        self.create_t_widget(ttk.Label, self.center_frame, "main_sub", font=("Segoe UI", 14, "italic")).pack(pady=(0, 45))

        cards_frame = ttk.Frame(self.center_frame)
        cards_frame.pack(fill=X)
        
        self.card1 = ttk.Frame(cards_frame, padding=35, bootstyle="dark")
        self.card1.pack(side=LEFT, padx=25, expand=True, fill=BOTH)
        self.create_t_widget(ttk.Label, self.card1, "card1_title", font=("Segoe UI", 16, "bold"), bootstyle=INFO).pack(pady=10)
        self.create_t_widget(ttk.Label, self.card1, "card1_desc", justify=CENTER).pack(pady=15)
        self.create_t_widget(ttk.Button, self.card1, "card1_btn", bootstyle=(INFO, OUTLINE), width=25, command=self.pencere_baglanti).pack(pady=15, ipady=8)
        
        self.card2 = ttk.Frame(cards_frame, padding=35, bootstyle="dark")
        self.card2.pack(side=LEFT, padx=25, expand=True, fill=BOTH)
        self.create_t_widget(ttk.Label, self.card2, "card2_title", font=("Segoe UI", 16, "bold"), bootstyle=WARNING).pack(pady=10)
        self.create_t_widget(ttk.Label, self.card2, "card2_desc", justify=CENTER).pack(pady=15)
        self.create_t_widget(ttk.Button, self.card2, "card2_btn", bootstyle=(WARNING, OUTLINE), width=25, command=self.pencere_kontrol).pack(pady=15, ipady=8)

        self.durum_frame = ttk.Frame(self.root, bootstyle="dark", padding=12)
        self.durum_frame.pack(side=BOTTOM, fill=X)
        
        self.create_t_widget(ttk.Label, self.durum_frame, "sys_status", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=(10, 5))
        self.durum_label = self.create_t_widget(ttk.Label, self.durum_frame, "offline", font=("Segoe UI", 10), bootstyle=DANGER)
        self.durum_label.pack(side=LEFT)
        self.create_t_widget(ttk.Label, self.durum_frame, "hardware", font=("Segoe UI", 10, "italic")).pack(side=RIGHT, padx=20)

        self.canli_okuma_dongusu()

    def yukle_ayarlar(self):
        self.katsayi_tablosu = {
            "hiz_okuma": 1.0, "hiz_yazma": 0.075, "akim": 0.01, "tork_okuma": 0.1, 
            "tork_yazma": 0.01, "rampa": 0.1, "guc": 0.01, "voltaj": 0.1, "frekans": 0.01
        }
        self.adres_haritasi = {
            "write_cw": 0, "write_hiz": 1, "write_tork": 2, "write_ramp_up": 2311, "write_ramp_down": 2312,
            "read_hiz_gercek": 101, "read_frekans": 105, "read_akim_motor": 106, "read_tork": 109,
            "read_dc_voltaj": 110, "read_guc": 113, "read_akim_u": 120, "read_akim_v": 121, "read_akim_w": 122,
            "read_status_word": 3
        }
        self.serial_config = {
            "parity": "NONE",
            "stopbits": 1.0,
            "timeout": 0.2
        }
        self.control_words = {
            "cw_speed_rdy": 1142,
            "cw_speed_run": 1151,
            "cw_torque_rdy": 3190,
            "cw_torque_run": 3199,
            "cw_stop": 1142,
            "cw_estop": 1138,
            "ext_mode_reg": 1910
        }
        self.config_dosyasi = "config.json"
        
        if os.path.exists(self.config_dosyasi):
            try:
                with open(self.config_dosyasi, "r", encoding="utf-8") as f:
                    kayitli = json.load(f)
                    
                if "scaling_factors" in kayitli:
                    for k, v in kayitli["scaling_factors"].items():
                        if k in self.katsayi_tablosu: self.katsayi_tablosu[k] = float(v)
                
                if "modbus_addresses" in kayitli:
                    for k, v in kayitli["modbus_addresses"].items():
                        if k in self.adres_haritasi: self.adres_haritasi[k] = int(v)
                        
                if "serial_config" in kayitli:
                    for k, v in kayitli["serial_config"].items():
                        if k in self.serial_config:
                            if k == "parity": self.serial_config[k] = str(v).upper()
                            else: self.serial_config[k] = float(v)
                            
                if "control_words" in kayitli:
                    for k, v in kayitli["control_words"].items():
                        if k in self.control_words: self.control_words[k] = int(v)
            except: pass
        else:
            self.kaydet_ayarlar()

    def kaydet_ayarlar(self):
        veri = {
            "scaling_factors": self.katsayi_tablosu,
            "modbus_addresses": self.adres_haritasi,
            "serial_config": self.serial_config,
            "control_words": self.control_words
        }
        try:
            with open(self.config_dosyasi, "w", encoding="utf-8") as f:
                json.dump(veri, f, indent=4)
        except: pass

    def pencere_kalibrasyon(self):
        calib_win = ttk.Toplevel(self.root)
        calib_win.title(self.texts[self.dil]["win_calib_title"])
        calib_win.geometry("550x650")
        self.ui_widgets.append((calib_win, "win_calib_title"))
        
        self.create_t_widget(ttk.Label, calib_win, "win_calib_title", font=("Segoe UI", 14, "bold"), bootstyle=INFO).pack(pady=(15, 5))
        self.create_t_widget(ttk.Label, calib_win, "calib_desc", wraplength=450, justify=CENTER).pack(pady=(0, 15))
        
        nb = ttk.Notebook(calib_win)
        nb.pack(fill=BOTH, expand=True, padx=20)
        
        tab_scale = ttk.Frame(nb, padding=15)
        tab_addr = ttk.Frame(nb, padding=15)
        tab_cw = ttk.Frame(nb, padding=15)
        tab_serial = ttk.Frame(nb, padding=15)
        
        nb.add(tab_serial, text="Serial Config")
        nb.add(tab_cw, text="Control Words")
        nb.add(tab_addr, text="Modbus Addresses")
        nb.add(tab_scale, text="Scale Factors")
        
        self.calib_entries = {}
        self.addr_entries = {}
        self.cw_entries = {}
        self.serial_entries = {}
        
        scale_labels = {
            "hiz_okuma": "Speed Read Scale", "hiz_yazma": "Speed Write Scale", "akim": "Current Scale",
            "tork_okuma": "Torque Read Scale", "tork_yazma": "Torque Write Scale", "rampa": "Ramp Time Scale",
            "guc": "Power Scale", "voltaj": "Voltage Scale", "frekans": "Frequency Scale"
        }
        
        addr_labels = {
            "write_cw": "Control Word (CW) Addr", "write_hiz": "Speed Ref Addr", "write_tork": "Torque Ref Addr",
            "write_ramp_up": "Ramp Up Time Addr", "write_ramp_down": "Ramp Down Time Addr",
            "read_hiz_gercek": "Actual Speed Addr", "read_frekans": "Output Freq Addr", "read_akim_motor": "Motor Current Addr",
            "read_tork": "Actual Torque Addr", "read_dc_voltaj": "DC Bus Voltage Addr", "read_guc": "Active Power Addr",
            "read_akim_u": "U-Phase Current Addr", "read_akim_v": "V-Phase Current Addr", "read_akim_w": "W-Phase Current Addr",
            "read_status_word": "Status Word (SW) Addr"
        }
        
        cw_labels = {
            "cw_speed_rdy": "Speed Ready (CW)", "cw_speed_run": "Speed Run (CW)",
            "cw_torque_rdy": "Torque Ready (CW)", "cw_torque_run": "Torque Run (CW)",
            "cw_stop": "Ramp Stop (CW)", "cw_estop": "Emergency Stop (CW)",
            "ext_mode_reg": "Ext. Mode Selection Reg"
        }
        
        serial_labels = {
            "parity": "Parity (NONE/EVEN/ODD)",
            "stopbits": "Stop Bits (1 or 2)",
            "timeout": "Timeout (sec)"
        }
        
        # Serial Tab
        row = 0
        for k, v in self.serial_config.items():
            ttk.Label(tab_serial, text=serial_labels.get(k, k), font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky=W, pady=8, padx=10)
            ent = ttk.Entry(tab_serial, width=15)
            ent.insert(0, str(v))
            ent.grid(row=row, column=1, pady=8, padx=10)
            self.serial_entries[k] = ent
            row += 1
            
        # CW Tab
        row = 0
        for k, v in self.control_words.items():
            ttk.Label(tab_cw, text=cw_labels.get(k, k), font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky=W, pady=6, padx=10)
            ent = ttk.Entry(tab_cw, width=15)
            ent.insert(0, str(v))
            ent.grid(row=row, column=1, pady=6, padx=10)
            self.cw_entries[k] = ent
            row += 1
        
        # Scale Tab
        row = 0
        for k, v in self.katsayi_tablosu.items():
            ttk.Label(tab_scale, text=scale_labels.get(k, k), font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky=W, pady=8, padx=10)
            ent = ttk.Entry(tab_scale, width=15)
            ent.insert(0, str(v))
            ent.grid(row=row, column=1, pady=8, padx=10)
            self.calib_entries[k] = ent
            row += 1
            
        # Addr Tab
        row = 0
        for k, v in self.adres_haritasi.items():
            ttk.Label(tab_addr, text=addr_labels.get(k, k), font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky=W, pady=6, padx=10)
            ent = ttk.Entry(tab_addr, width=15)
            ent.insert(0, str(v))
            ent.grid(row=row, column=1, pady=6, padx=10)
            self.addr_entries[k] = ent
            row += 1
            
        btn_frame = ttk.Frame(calib_win)
        btn_frame.pack(fill=X, pady=20, padx=10)
        
        btn_import = ttk.Button(btn_frame, text="📥 Import Profile", bootstyle=(PRIMARY, OUTLINE), command=self.profil_ice_aktar)
        btn_import.pack(side=LEFT, padx=5)
        
        btn_export = ttk.Button(btn_frame, text="📤 Export Profile", bootstyle=(PRIMARY, OUTLINE), command=self.profil_disa_aktar)
        btn_export.pack(side=LEFT, padx=5)
        
        self.create_t_widget(ttk.Button, btn_frame, "save_calib", bootstyle=SUCCESS, command=lambda: self.kalibrasyon_kaydet(calib_win)).pack(side=RIGHT, ipady=5, ipadx=10)
        
    def profil_ice_aktar(self):
        dosya = filedialog.askopenfilename(title="Profil Seç", filetypes=[("JSON Files", "*.json")])
        if not dosya: return
        try:
            with open(dosya, "r", encoding="utf-8") as f:
                kayitli = json.load(f)
                
            if "scaling_factors" in kayitli:
                for k, v in kayitli["scaling_factors"].items():
                    if k in self.calib_entries:
                        self.calib_entries[k].delete(0, 'end')
                        self.calib_entries[k].insert(0, str(v))
                        
            if "modbus_addresses" in kayitli:
                for k, v in kayitli["modbus_addresses"].items():
                    if k in self.addr_entries:
                        self.addr_entries[k].delete(0, 'end')
                        self.addr_entries[k].insert(0, str(v))
                        
            if "serial_config" in kayitli:
                for k, v in kayitli["serial_config"].items():
                    if k in self.serial_entries:
                        self.serial_entries[k].delete(0, 'end')
                        if k == "parity": self.serial_entries[k].insert(0, str(v).upper())
                        else: self.serial_entries[k].insert(0, str(v))
                        
            if "control_words" in kayitli:
                for k, v in kayitli["control_words"].items():
                    if k in self.cw_entries:
                        self.cw_entries[k].delete(0, 'end')
                        self.cw_entries[k].insert(0, str(v))
                        
            Messagebox.show_info("Profil başarıyla içe aktarıldı. Uygulamak için 'Kaydet' butonuna basınız.", title="Başarılı")
        except Exception as e:
            Messagebox.show_error(f"Dosya okunamadı: {e}", title="Hata")

    def profil_disa_aktar(self):
        dosya = filedialog.asksaveasfilename(title="Profili Kaydet", defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not dosya: return
        
        veri = {
            "scaling_factors": {k: ent.get() for k, ent in self.calib_entries.items()},
            "modbus_addresses": {k: ent.get() for k, ent in self.addr_entries.items()},
            "serial_config": {k: ent.get() for k, ent in self.serial_entries.items()},
            "control_words": {k: ent.get() for k, ent in self.cw_entries.items()}
        }
        
        try:
            with open(dosya, "w", encoding="utf-8") as f:
                json.dump(veri, f, indent=4)
            Messagebox.show_info("Profil başarıyla dışa aktarıldı.", title="Başarılı")
        except Exception as e:
            Messagebox.show_error(f"Dosya kaydedilemedi: {e}", title="Hata")

    def kalibrasyon_kaydet(self, window):
        for k, ent in self.calib_entries.items():
            try: self.katsayi_tablosu[k] = float(ent.get())
            except ValueError:
                Messagebox.show_error(f"Geçersiz çarpan değeri: {ent.get()}", title="Hata")
                return
                
        for k, ent in self.addr_entries.items():
            try: self.adres_haritasi[k] = int(ent.get())
            except ValueError:
                Messagebox.show_error(f"Geçersiz adres formatı (tam sayı olmalı): {ent.get()}", title="Hata")
                return
                
        for k, ent in self.cw_entries.items():
            try: self.control_words[k] = int(ent.get())
            except ValueError:
                Messagebox.show_error(f"Geçersiz Control Word (tam sayı olmalı): {ent.get()}", title="Hata")
                return
                
        for k, ent in self.serial_entries.items():
            try:
                if k == "parity": self.serial_config[k] = str(ent.get()).upper()
                else: self.serial_config[k] = float(ent.get())
            except ValueError:
                Messagebox.show_error(f"Geçersiz Seri Haberleşme parametresi: {ent.get()}", title="Hata")
                return
                
        self.kaydet_ayarlar()
        window.destroy()
        Messagebox.show_info(self.texts[self.dil]["msg_rep_ok"] + " config.json", title="Başarılı")

    def create_t_widget(self, widget_class, parent, key, **kwargs):
        text = self.texts[self.dil].get(key, key)
        w = widget_class(parent, text=text, **kwargs)
        self.ui_widgets.append((w, key))
        return w

    def grafik_yazilari_guncelle(self):
        if not hasattr(self, 'ax_mech'): return
        self.ax_mech[0].set_title(self.texts[self.dil]["chart_speed"])
        self.ax_mech[1].set_title(self.texts[self.dil]["chart_torque"])
        self.ax_pwr[0].set_title(self.texts[self.dil]["chart_power"])
        self.ax_pwr[1].set_title(self.texts[self.dil]["chart_volt"])
        for axes in [self.ax_curr, self.ax_mech, self.ax_pwr]:
            axes[-1].set_xlabel(self.texts[self.dil]["chart_time"])
            for ax in axes:
                ax.set_ylabel(self.texts[self.dil]["chart_curr"] if axes is self.ax_curr else "")
        self.grafik_tema_guncelle()

    def degistir_dil(self, event=None):
        secim = self.cb_lang.get()
        self.dil = "TR" if secim == "Türkçe" else "EN"
        
        for w, key in self.ui_widgets:
            try: w.config(text=self.texts[self.dil].get(key, key))
            except: pass
            
        for nb, idx, key in self.ui_tabs:
            try: nb.tab(idx, text=self.texts[self.dil].get(key, key))
            except: pass
            
        self.durum_sifirla()
        self.grafik_yazilari_guncelle()

    def degistir_tema(self, event=None):
        secim = self.cb_theme.get()
        self.tema = "light" if secim == "Light" else "dark"
        if self.tema == "light":
            self.root.style.theme_use("cosmo")
            if hasattr(self, 'card1'): self.card1.configure(bootstyle="secondary")
            if hasattr(self, 'card2'): self.card2.configure(bootstyle="secondary")
            if hasattr(self, 'durum_frame'): self.durum_frame.configure(bootstyle="secondary")
        else:
            self.root.style.theme_use("darkly")
            if hasattr(self, 'card1'): self.card1.configure(bootstyle="dark")
            if hasattr(self, 'card2'): self.card2.configure(bootstyle="dark")
            if hasattr(self, 'durum_frame'): self.durum_frame.configure(bootstyle="dark")
        self.grafik_tema_guncelle()

    def goster_bildirim(self, mesaj, tur="info"):
        renk = DANGER if tur == "error" else WARNING if tur == "warning" else SUCCESS
        self.durum_label.config(text=f"🔔 {mesaj}", bootstyle=renk)
        self.root.after(4000, self.durum_sifirla)

    def durum_sifirla(self):
        if self.baglanti_aktif:
            self.durum_label.config(text=self.texts[self.dil]["online"], bootstyle=SUCCESS)
        else:
            self.durum_label.config(text=self.texts[self.dil]["offline"], bootstyle=DANGER)

    def arayuz_kutu_guncelle(self, widget, metin, tur="info"):
        if widget:
            widget.configure(state="normal")
            widget.delete(0, END)
            widget.insert(0, metin)
            
            # Renk uygulaması Status Word için
            if tur == "danger": widget.configure(bootstyle=DANGER)
            elif tur == "success": widget.configure(bootstyle=SUCCESS)
            elif tur == "warning": widget.configure(bootstyle=WARNING)
            else: widget.configure(bootstyle=INFO)
            
            widget.configure(state="readonly")

    def toggle_haberlesme(self):
        if not self.baglanti_aktif:
            Messagebox.show_error(self.texts[self.dil]["msg_conn_err"], title="Bağlantı Hatası")
            return
            
        self.canli_okuma_aktif = not getattr(self, 'canli_okuma_aktif', False)
        self.veri_gonderim_aktif = self.canli_okuma_aktif
        
        if self.canli_okuma_aktif:
            self.t_start = time.time()
            self.btn_canli_veri.config(text=self.texts[self.dil]["btn_live_stop"], bootstyle=(DANGER, OUTLINE))
            self.goster_bildirim(self.texts[self.dil]["msg_live_start"], "info")
            self.veri_gonderim_dongusu()
        else:
            self.btn_canli_veri.config(text=self.texts[self.dil]["btn_live_start"], bootstyle=(INFO, OUTLINE))
            self.goster_bildirim(self.texts[self.dil]["msg_live_stop"], "warning")

    def veri_gonderim_dongusu(self):
        if self.baglanti_aktif and getattr(self, 'veri_gonderim_aktif', False) and self.instrument:
            self.tum_parametreleri_yaz()
            self.root.after(200, self.veri_gonderim_dongusu)

    def motor_baslat(self):
        if self.baglanti_aktif and self.instrument:
            self.motor_calisiyor = True
            secilen_mod = self.cb_control_mode.get() if hasattr(self, 'cb_control_mode') else "Speed"
            cw_hazirlik = self.control_words["cw_speed_rdy"] if secilen_mod == "Speed" else self.control_words["cw_torque_rdy"]
            cw_start = self.control_words["cw_speed_run"] if secilen_mod == "Speed" else self.control_words["cw_torque_run"]
            try:
                self.instrument.write_register(self.adres_haritasi["write_cw"], cw_hazirlik, 0)
                self.root.after(100, lambda: self.instrument.write_register(self.adres_haritasi["write_cw"], cw_start, 0))
                self.goster_bildirim(self.texts[self.dil]["msg_start"], "success")
            except Exception as e:
                Messagebox.show_error(f"Hata: {e}", title="Haberleşme Hatası")
        else:
            Messagebox.show_error(self.texts[self.dil]["msg_conn_err"], title="Bağlantı Hatası")

    def motor_durdur(self):
        if self.baglanti_aktif and self.instrument:
            self.motor_calisiyor = False
            try:
                self.instrument.write_register(self.adres_haritasi["write_cw"], self.control_words["cw_stop"], 0)
                self.instrument.write_register(self.adres_haritasi["write_hiz"], 0, 0)
                self.goster_bildirim(self.texts[self.dil]["msg_stop"], "warning")
            except Exception as e:
                Messagebox.show_error(f"Hata: {e}", title="Haberleşme Hatası")
        else:
            Messagebox.show_error(self.texts[self.dil]["msg_conn_err"], title="Bağlantı Hatası")

    def motor_acil_stop(self):
        if self.baglanti_aktif and self.instrument:
            self.motor_calisiyor = False
            try:
                self.instrument.write_register(self.adres_haritasi["write_cw"], self.control_words["cw_estop"], 0)
                self.instrument.write_register(self.adres_haritasi["write_hiz"], 0, 0)
                self.goster_bildirim(self.texts[self.dil]["msg_estop"], "error")
            except Exception as e:
                Messagebox.show_error(f"Hata: {e}", title="Haberleşme Hatası")
        else:
            Messagebox.show_error(self.texts[self.dil]["msg_conn_err"], title="Bağlantı Hatası")

    def modbus_baglan(self, port, baud, mode, slave_id, window):
        try:
            self.instrument = minimalmodbus.Instrument(port, slave_id)
            self.instrument.serial.baudrate = baud
            self.instrument.serial.bytesize = 8
            
            p_str = self.serial_config.get("parity", "NONE")
            if p_str == "EVEN": p = serial.PARITY_EVEN
            elif p_str == "ODD": p = serial.PARITY_ODD
            else: p = serial.PARITY_NONE
            
            self.instrument.serial.parity = p
            self.instrument.serial.stopbits = self.serial_config.get("stopbits", 1.0)
            self.instrument.serial.timeout = self.serial_config.get("timeout", 0.2)
            
            self.instrument.mode = minimalmodbus.MODE_RTU if mode == "RTU" else minimalmodbus.MODE_ASCII
            self.baglanti_aktif = True
            
            self.durum_sifirla()
            window.destroy() 
            self.goster_bildirim(self.texts[self.dil]["msg_conn_ok"] + port, "success")
        except Exception as e:
            self.baglanti_aktif = False
            Messagebox.show_error(f"Bağlantı kurulamadı:\n{e}", title="Bağlantı Hatası")
            self.goster_bildirim(f"Error: {e}", "error")

    def canli_okuma_dongusu(self):
        if self.baglanti_aktif and self.canli_okuma_aktif and self.instrument:
            secilen_mod = self.cb_control_mode.get() if hasattr(self, 'cb_control_mode') else "Speed"
            
            # --- Değişkenleri güvenli başlat ---
            gercek_hiz = 0.0
            gercek_tork = 0.0
            gercek_guc = 0.0
            dc_v = 0.0
            u_curr = 0.0
            v_curr = 0.0
            w_curr = 0.0
            
            if secilen_mod == "Speed":
                try:
                    ham_hiz = self.instrument.read_register(self.adres_haritasi["read_hiz_gercek"], 0, signed=True)
                    gercek_hiz = ham_hiz * self.katsayi_tablosu["hiz_okuma"] 
                    if hasattr(self, 'lbl_anlik_hiz'):
                        self.lbl_anlik_hiz_title.config(text=self.texts[self.dil]["lbl_speed"])
                        self.lbl_anlik_hiz.config(text=f"{gercek_hiz:.1f} RPM")
                except: pass
            else:
                try:
                    ham_tork = self.instrument.read_register(self.adres_haritasi["read_tork"], 0, signed=True)
                    gercek_tork = ham_tork * self.katsayi_tablosu["tork_okuma"]
                    if hasattr(self, 'lbl_anlik_hiz'):
                        self.lbl_anlik_hiz_title.config(text=self.texts[self.dil]["lbl_torque"])
                        self.lbl_anlik_hiz.config(text=f"{gercek_tork:.1f} %")
                except: pass
                
            try:
                ham_guc = self.instrument.read_register(self.adres_haritasi["read_guc"], 0, signed=True)
                gercek_guc = ham_guc * self.katsayi_tablosu["guc"]
                if hasattr(self, 'lbl_anlik_guc'):
                    self.lbl_anlik_guc.config(text=f"{gercek_guc:.2f} kW")
            except: pass

            try:
                dc_v = self.instrument.read_register(self.adres_haritasi["read_dc_voltaj"], 0) * self.katsayi_tablosu["voltaj"]
                self.arayuz_kutu_guncelle(self.dp_kutulari.get("DC Voltage (V)"), f"{dc_v:.1f}")
            except: pass
                
            try:
                m_curr = self.instrument.read_register(self.adres_haritasi["read_akim_motor"], 0) * self.katsayi_tablosu["akim"]
                self.arayuz_kutu_guncelle(self.dp_kutulari.get("Motor Current (A)"), f"{m_curr:.2f}")
            except: pass
                
            try:
                o_freq = self.instrument.read_register(self.adres_haritasi["read_frekans"], 0, signed=True) * self.katsayi_tablosu["frekans"]
                self.arayuz_kutu_guncelle(self.dp_kutulari.get("Output Frequency (Hz)"), f"{o_freq:.2f}")
            except: pass

            try:
                flux = self.instrument.read_register(123, 0) 
                self.arayuz_kutu_guncelle(self.dp_kutulari.get("Flux Actual (%)"), f"{flux:.1f}")
            except: pass
                
            try:
                ham_tork_full = self.instrument.read_register(self.adres_haritasi["read_tork"], 0, signed=True)
                gercek_tork = ham_tork_full * self.katsayi_tablosu["tork_okuma"] # update also in speed mode
                self.arayuz_kutu_guncelle(self.dp_kutulari.get("Motor Torque (%)"), f"{gercek_tork:.1f}")
            except: pass

            # Read U,V,W currents specifically for the plot
            try:
                u_curr = self.instrument.read_register(self.adres_haritasi["read_akim_u"], 0) * self.katsayi_tablosu["akim"]
                v_curr = self.instrument.read_register(self.adres_haritasi["read_akim_v"], 0) * self.katsayi_tablosu["akim"]
                w_curr = self.instrument.read_register(self.adres_haritasi["read_akim_w"], 0) * self.katsayi_tablosu["akim"]
            except: pass

            try:
                sw_val = self.instrument.read_register(self.adres_haritasi["read_status_word"], 0)
                sw_bits = [(sw_val >> i) & 1 for i in range(16)]
                
                status_keys = ["RDY_ON", "RDY_RUN", "RDY_REF", "TRIPPED", "OFF_2_STA", "OFF_3_STA", "SWC_ON_INHIB", "ALARM", "AT_SETPOINT", "REMOTE", "ABOVE_LIMIT", "EXT_RUN_ENABLED"]
                for idx, key in enumerate(status_keys):
                    val = sw_bits[idx]
                    text_val = self.sw_dict[key][self.dil].get(val, str(val))
                    
                    tur = "info"
                    if key in ["TRIPPED", "ALARM"] and val == 1: tur = "danger"
                    elif key in ["RDY_ON", "RDY_RUN", "RDY_REF"] and val == 1: tur = "success"
                    elif key == "SWC_ON_INHIB" and val == 1: tur = "warning"
                    
                    self.arayuz_kutu_guncelle(self.sw_kutulari.get(key), text_val, tur)
            except: pass
            
            # --- CANLI GRAFİKLERİ GÜNCELLE ---
            t = time.time() - self.t_start
            self.hist_t.append(t)
            self.hist_hiz.append(gercek_hiz)
            self.hist_tork.append(gercek_tork)
            self.hist_guc.append(gercek_guc)
            self.hist_volt.append(dc_v)
            self.hist_u.append(u_curr)
            self.hist_v.append(v_curr)
            self.hist_w.append(w_curr)
            
            if hasattr(self, 'lines_curr'):
                # 1. Faz Akımları
                self.lines_curr[0].set_data(self.hist_t, self.hist_u)
                self.lines_curr[1].set_data(self.hist_t, self.hist_v)
                self.lines_curr[2].set_data(self.hist_t, self.hist_w)
                for ax in self.ax_curr:
                    ax.relim()
                    ax.autoscale_view()
                self.canvas_curr.draw_idle()
                
                # 2. Mekanik (Hız/Tork)
                self.line_speed.set_data(self.hist_t, self.hist_hiz)
                self.line_torque.set_data(self.hist_t, self.hist_tork)
                for ax in self.ax_mech:
                    ax.relim()
                    ax.autoscale_view()
                self.canvas_mech.draw_idle()
                
                # 3. Güç (Aktif Güç/DC Bara)
                self.line_power.set_data(self.hist_t, self.hist_guc)
                self.line_volt.set_data(self.hist_t, self.hist_volt)
                for ax in self.ax_pwr:
                    ax.relim()
                    ax.autoscale_view()
                self.canvas_pwr.draw_idle()
                
        self.root.after(500, self.canli_okuma_dongusu)

    def tum_parametreleri_yaz(self):
        secilen_mod = self.cb_control_mode.get() if hasattr(self, 'cb_control_mode') else "Speed"
        param_listesi = [
            ("Ramp UP (s)", 30, "write_ramp_up", "rampa"),
            ("Ramp DOWN (s)", 30, "write_ramp_down", "rampa"),
            ("Speed Ref (RPM)", 3000, "write_hiz", "hiz_yazma") if secilen_mod == "Speed" else ("Torque Ref (%)", 300, "write_tork", "tork_yazma")
        ]
        
        hatali_veri = False
        for isim, limit, adres, katsayi_anahtar in param_listesi:
            widget = self.giris_kutulari.get(isim)
            if not widget: continue
            try:
                deger = float(widget.get())
                if deger > limit:
                    widget.delete(0, END)
                    widget.insert(0, str(limit))
                    hatali_veri = True
                    break 
            except ValueError:
                hatali_veri = True
                break
                
        if not hatali_veri and self.baglanti_aktif and self.instrument:
            if getattr(self, 'motor_calisiyor', False):
                cw_degeri = self.control_words["cw_speed_run"] if secilen_mod == "Speed" else self.control_words["cw_torque_run"]
            else:
                cw_degeri = self.control_words["cw_speed_rdy"] if secilen_mod == "Speed" else self.control_words["cw_torque_rdy"]
                
            ext_mod = 0 if secilen_mod == "Speed" else 1 
            
            try:
                self.instrument.write_register(self.control_words["ext_mode_reg"], ext_mod, 0) 
                self.instrument.write_register(self.adres_haritasi["write_cw"], cw_degeri, 0)
            except: pass
            
            for isim, limit, adres, katsayi_anahtar in param_listesi:
                widget = self.giris_kutulari.get(isim)
                if not widget: continue
                try:
                    deger = float(widget.get())
                    if hasattr(self, 'var_yon') and self.var_yon.get() == "REV":
                        if "Ref" in isim: deger = -abs(deger)
                    else:
                        if "Ref" in isim: deger = abs(deger)
                            
                    gonderilecek_veri = int(deger / self.katsayi_tablosu.get(katsayi_anahtar, 1.0))
                    is_signed = True if "Ref" in isim else False
                    self.instrument.write_register(self.adres_haritasi[adres], gonderilecek_veri, 0, signed=is_signed)
                    
                    if hasattr(self, 'okunan_kutular') and isim in self.okunan_kutular:
                        self.arayuz_kutu_guncelle(self.okunan_kutular[isim], str(deger))
                except: pass

    def rapor_olustur(self):
        ornek_veri = [
            {"Zaman": "10:01:00", "Faz U (A)": 12.1, "Faz V (A)": 12.0, "Faz W (A)": 12.2, "Hız (RPM)": 1498, "Güç (kW)": 8.5},
            {"Zaman": "10:01:01", "Faz U (A)": 12.5, "Faz V (A)": 12.4, "Faz W (A)": 12.6, "Hız (RPM)": 1500, "Güç (kW)": 8.7}
        ]
        df = pd.DataFrame(ornek_veri)
        dosya_adi = f"AGU_PowerLab_DeneyRaporu_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        df.to_excel(dosya_adi, index=False)
        self.goster_bildirim(self.texts[self.dil]["msg_rep_ok"] + dosya_adi, "success")

    def pencere_baglanti(self):
        baglanti_win = ttk.Toplevel(self.root)
        baglanti_win.title(self.texts[self.dil]["win_conn_title"])
        baglanti_win.geometry("600x480")
        self.ui_widgets.append((baglanti_win, "win_conn_title"))

        self.create_t_widget(ttk.Label, baglanti_win, "conn_settings", font=("Segoe UI", 14, "bold"), bootstyle=INFO).pack(pady=15)
        form = ttk.Frame(baglanti_win, padding=15)
        form.pack(fill=BOTH, expand=True)

        top_frame = ttk.Frame(form)
        top_frame.pack(fill=X, pady=5)
        
        ttk.Label(top_frame, text="Serial Port", font=("Segoe UI", 9)).grid(row=0, column=0, padx=10, sticky=W)
        cb_port = ttk.Combobox(top_frame, values=["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"], width=12)
        cb_port.set("COM2")
        cb_port.grid(row=1, column=0, padx=10)
        
        ttk.Label(top_frame, text="Mode (RTU)", font=("Segoe UI", 9)).grid(row=0, column=1, padx=10, sticky=W)
        cb_mode = ttk.Combobox(top_frame, values=["RTU", "ASCII"], width=12)
        cb_mode.set("RTU")
        cb_mode.grid(row=1, column=1, padx=10)
        
        ttk.Label(top_frame, text="Slave ID", font=("Segoe UI", 9)).grid(row=0, column=2, padx=10, sticky=W)
        ent_slave = ttk.Entry(top_frame, width=12)
        ent_slave.insert(0, "1")
        ent_slave.grid(row=1, column=2, padx=10)

        mid_frame = ttk.Frame(form)
        mid_frame.pack(fill=BOTH, expand=True, pady=15)

        diag_frame = ttk.Labelframe(mid_frame, text=" Comm Diagnostics ", padding=10)
        diag_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        d_top = ttk.Frame(diag_frame)
        d_top.pack(fill=X)
        ttk.Label(d_top, text="status").grid(row=0, column=0, padx=5, sticky=W)
        ttk.Checkbutton(d_top, bootstyle="success-round-toggle").grid(row=1, column=0, padx=5, sticky=W)
        
        ttk.Label(d_top, text="code").grid(row=0, column=1, padx=5, sticky=W)
        c_ent = ttk.Entry(d_top, width=12)
        c_ent.insert(0, "0")
        c_ent.grid(row=1, column=1, padx=5, sticky=W)
        
        ttk.Text(diag_frame, height=10, width=20).pack(fill=BOTH, expand=True, pady=(15,0))

        config_frame = ttk.Labelframe(mid_frame, text=" Serial Config ", padding=10)
        config_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))

        configs = [
            ("baud rate (bps)", ["9600", "19200", "38400", "115200"], "19200"),
            ("stop bits", ["1.0", "1.5", "2.0"], "1.0"),
            ("parity", ["None", "Odd", "Even", "Mark", "Space"], "None"),
            ("flow control", ["None", "XON/XOFF", "RTS/CTS"], "None")
        ]
        
        self.baglanti_kombulari = {}
        for i, (lbl, vals, def_val) in enumerate(configs):
            ttk.Label(config_frame, text=lbl, font=("Segoe UI", 9)).grid(row=i*2, column=0, sticky=W, pady=(2,0))
            cb = ttk.Combobox(config_frame, values=vals, width=18)
            cb.set(def_val)
            cb.grid(row=i*2+1, column=0, sticky=W)
            self.baglanti_kombulari[lbl] = cb
            
        ttk.Label(config_frame, text="timeout", font=("Segoe UI", 9)).grid(row=8, column=0, sticky=W, pady=(2,0))
        t_ent = ttk.Entry(config_frame, width=22)
        t_ent.insert(0, "1000")
        t_ent.grid(row=9, column=0, sticky=W)
        
        ttk.Label(config_frame, text="retries", font=("Segoe UI", 9)).grid(row=10, column=0, sticky=W, pady=(2,0))
        r_ent = ttk.Entry(config_frame, width=22)
        r_ent.insert(0, "1")
        r_ent.grid(row=11, column=0, sticky=W)

        self.create_t_widget(ttk.Button, top_frame, "save_conn", bootstyle=SUCCESS, 
                   command=lambda: self.modbus_baglan(
                       cb_port.get(), 
                       int(self.baglanti_kombulari["baud rate (bps)"].get()), 
                       cb_mode.get(), 
                       int(ent_slave.get()), 
                       baglanti_win
                   )).grid(row=1, column=3, padx=(15, 0), sticky=W)

    def pencere_kontrol(self):
        kontrol_win = ttk.Toplevel(self.root)
        kontrol_win.title(self.texts[self.dil]["win_ctrl_title"])
        kontrol_win.state('zoomed')
        self.ui_widgets.append((kontrol_win, "win_ctrl_title"))

        main_layout = ttk.Frame(kontrol_win, padding=10)
        main_layout.pack(fill=BOTH, expand=True)

        sol_panel = ttk.Frame(main_layout, width=480)
        sol_panel.pack(side=LEFT, fill=Y, padx=5)

        self.notebook = ttk.Notebook(sol_panel, bootstyle="info")
        self.notebook.pack(fill=BOTH, expand=True, pady=5)

        tab_control = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_control, text=self.texts[self.dil]["tab_ctrl"])
        self.ui_tabs.append((self.notebook, 0, "tab_ctrl"))

        tab_drive_params = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_drive_params, text=self.texts[self.dil]["tab_dp"])
        self.ui_tabs.append((self.notebook, 1, "tab_dp"))

        tab_more_params = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_more_params, text=self.texts[self.dil]["tab_mdp"])
        self.ui_tabs.append((self.notebook, 2, "tab_mdp"))

        tab_status = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_status, text=self.texts[self.dil]["tab_sw"])
        self.ui_tabs.append((self.notebook, 3, "tab_sw"))

        # --- SEKME 1: CONTROL SETTINGS ---
        mod_frame = self.create_t_widget(ttk.Labelframe, tab_control, "lf_mode", padding=10)
        mod_frame.pack(fill=X, pady=4)
        
        self.create_t_widget(ttk.Label, mod_frame, "ctrl_mode").grid(row=0, column=0, sticky=W, pady=4)
        self.cb_control_mode = ttk.Combobox(mod_frame, values=["Speed", "Torque"], width=12)
        self.cb_control_mode.current(0)
        self.cb_control_mode.grid(row=0, column=1, padx=5)
        
        self.create_t_widget(ttk.Label, mod_frame, "dir").grid(row=1, column=0, sticky=W, pady=4)
        yon_frame = ttk.Frame(mod_frame)
        yon_frame.grid(row=1, column=1, sticky=W, padx=5)
        self.var_yon = ttk.StringVar(value="FWD")
        self.create_t_widget(ttk.Radiobutton, yon_frame, "fwd", value="FWD", variable=self.var_yon, bootstyle=INFO).pack(side=LEFT, padx=2)
        self.create_t_widget(ttk.Radiobutton, yon_frame, "rev", value="REV", variable=self.var_yon, bootstyle=INFO).pack(side=LEFT, padx=2)

        param_frame = self.create_t_widget(ttk.Labelframe, tab_control, "lf_params", padding=10)
        param_frame.pack(fill=X, pady=4)
        
        self.create_t_widget(ttk.Label, param_frame, "col_param", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=W)
        self.create_t_widget(ttk.Label, param_frame, "col_target", font=("Segoe UI", 9, "bold")).grid(row=0, column=1)
        self.create_t_widget(ttk.Label, param_frame, "col_current", font=("Segoe UI", 9, "bold"), bootstyle=WARNING).grid(row=0, column=2)

        parametreler = [
            ("Speed Ref (RPM)", "1500", 3000),
            ("Torque Ref (%)", "100", 300),
            ("Ramp UP (s)", "5", 30),
            ("Ramp DOWN (s)", "5", 30)
        ]

        self.giris_kutulari = {}
        self.okunan_kutular = {}
        for i, (isim, varsayilan, limit) in enumerate(parametreler, start=1):
            self.create_t_widget(ttk.Label, param_frame, isim, font=("Segoe UI", 9)).grid(row=i, column=0, sticky=W, pady=5)
            
            ent = ttk.Entry(param_frame, width=8)
            ent.insert(0, varsayilan)
            ent.grid(row=i, column=1, padx=3)
            self.giris_kutulari[isim] = ent
            
            okunan = ttk.Entry(param_frame, width=12, bootstyle=WARNING)
            okunan.insert(0, varsayilan)
            okunan.configure(state="readonly")
            okunan.grid(row=i, column=2, padx=3)
            self.okunan_kutular[isim] = okunan

        # --- SEKME 2: DRIVE PARAMS ---
        dp_col1 = ["DC Voltage (V)", "Mot. Spd. Est. (RPM)", "Encoder Spd. 1 Filtered", "Output Frequency (Hz)", 
                   "I_mot % of Motor Nom.", "Output Voltage", "Out. Pwr. % of Nom.", "V-phase Curr. (A)"]
        dp_col2 = ["Motor Current (A)", "Mot. Spd. Used (RPM)", "Encoder Spd. 2 Filtered", "Motor Speed (%)", 
                   "Motor Torque (%)", "Output Power", "U-phase Curr. (A)", "W-phase Curr. (A)"]
        
        for r, item in enumerate(dp_col1):
            self.create_t_widget(ttk.Label, tab_drive_params, item, font=("Segoe UI", 9)).grid(row=r*2, column=0, sticky=W, padx=10, pady=(4,0))
            ent = ttk.Entry(tab_drive_params, width=18)
            ent.insert(0, "-")
            ent.configure(state="readonly")
            ent.grid(row=r*2+1, column=0, sticky=W, padx=10, pady=(0,5))
            self.dp_kutulari[item] = ent 
            
        for r, item in enumerate(dp_col2):
            self.create_t_widget(ttk.Label, tab_drive_params, item, font=("Segoe UI", 9)).grid(row=r*2, column=1, sticky=W, padx=10, pady=(4,0))
            ent = ttk.Entry(tab_drive_params, width=18)
            ent.insert(0, "-")
            ent.configure(state="readonly")
            ent.grid(row=r*2+1, column=1, sticky=W, padx=10, pady=(0,5))
            self.dp_kutulari[item] = ent 

        # --- SEKME 3: MORE DRIVE PARAMS ---
        mdp_col1 = ["Flux Actual (%)", "Nominal Trq. Scale (Nm)", "Ambient Temp. (C)", "U-phase Cur. RMS (A)", "W-phase Cur. RMS (A)"]
        mdp_col2 = ["INU Moment. pf", "Spd. Change Rate (RPM/s)", "Step-up Mot. Cur. (A)", "V-phase Cur. RMS (A)"]
        
        for r, item in enumerate(mdp_col1):
            self.create_t_widget(ttk.Label, tab_more_params, item, font=("Segoe UI", 9)).grid(row=r*2, column=0, sticky=W, padx=10, pady=(4,0))
            ent = ttk.Entry(tab_more_params, width=18)
            ent.insert(0, "-")
            ent.configure(state="readonly")
            ent.grid(row=r*2+1, column=0, sticky=W, padx=10, pady=(0,5))
            self.dp_kutulari[item] = ent
            
        for r, item in enumerate(mdp_col2):
            self.create_t_widget(ttk.Label, tab_more_params, item, font=("Segoe UI", 9)).grid(row=r*2, column=1, sticky=W, padx=10, pady=(4,0))
            ent = ttk.Entry(tab_more_params, width=18)
            ent.insert(0, "-")
            ent.configure(state="readonly")
            ent.grid(row=r*2+1, column=1, sticky=W, padx=10, pady=(0,5))
            self.dp_kutulari[item] = ent

        # --- SEKME 4: STATUS WORD ---
        status_col1 = ["RDY_ON", "RDY_RUN", "RDY_REF", "TRIPPED", "OFF_2_STA", "OFF_3_STA", "SWC_ON_INHIB"]
        status_col2 = ["ALARM", "AT_SETPOINT", "REMOTE", "ABOVE_LIMIT", "EXT_RUN_ENABLED"]
        
        for r, item in enumerate(status_col1):
            ttk.Label(tab_status, text=item, font=("Segoe UI", 9, "bold")).grid(row=r*2, column=0, sticky=W, padx=10, pady=(6,0))
            ent = ttk.Entry(tab_status, width=22, bootstyle=INFO)
            ent.insert(0, "-")
            ent.configure(state="readonly")
            ent.grid(row=r*2+1, column=0, sticky=W, padx=10, pady=(0,6))
            self.sw_kutulari[item] = ent
            
        for r, item in enumerate(status_col2):
            ttk.Label(tab_status, text=item, font=("Segoe UI", 9, "bold")).grid(row=r*2, column=1, sticky=W, padx=10, pady=(6,0))
            ent = ttk.Entry(tab_status, width=22, bootstyle=WARNING)
            ent.insert(0, "-")
            ent.configure(state="readonly")
            ent.grid(row=r*2+1, column=1, sticky=W, padx=10, pady=(0,6))
            self.sw_kutulari[item] = ent

        # --- SABİT ALT PANELLER ---
        guc_frame = self.create_t_widget(ttk.Labelframe, sol_panel, "lf_digital", padding=10)
        guc_frame.pack(fill=X, pady=4)
        
        key_btn_live = "btn_live_stop" if self.canli_okuma_aktif else "btn_live_start"
        boot_live = (DANGER, OUTLINE) if self.canli_okuma_aktif else (INFO, OUTLINE)
        self.btn_canli_veri = self.create_t_widget(ttk.Button, guc_frame, key_btn_live, bootstyle=boot_live, command=self.toggle_haberlesme)
        self.btn_canli_veri.grid(row=0, column=0, columnspan=2, sticky=EW, pady=(0, 10))
        
        self.lbl_anlik_hiz_title = self.create_t_widget(ttk.Label, guc_frame, "lbl_speed", font=("Segoe UI", 10))
        self.lbl_anlik_hiz_title.grid(row=1, column=0, sticky=W, pady=3)
        self.lbl_anlik_hiz = ttk.Label(guc_frame, text="---", font=("Segoe UI", 11, "bold"), bootstyle=INFO)
        self.lbl_anlik_hiz.grid(row=1, column=1, sticky=E, pady=3, padx=20)
        
        self.create_t_widget(ttk.Label, guc_frame, "lbl_power", font=("Segoe UI", 10)).grid(row=2, column=0, sticky=W, pady=3)
        self.lbl_anlik_guc = ttk.Label(guc_frame, text="---", font=("Segoe UI", 11, "bold"), bootstyle=WARNING)
        self.lbl_anlik_guc.grid(row=2, column=1, sticky=E, pady=3, padx=20)

        stop_frame = self.create_t_widget(ttk.Labelframe, sol_panel, "lf_oper", padding=10)
        stop_frame.pack(fill=X, pady=4)
        
        btn_frame = ttk.Frame(stop_frame)
        btn_frame.pack(fill=X, pady=4)
        self.create_t_widget(ttk.Button, btn_frame, "btn_start", bootstyle=SUCCESS, command=self.motor_baslat).pack(side=LEFT, fill=X, expand=True, padx=(0, 2))
        self.create_t_widget(ttk.Button, btn_frame, "btn_stop", bootstyle=WARNING, command=self.motor_durdur).pack(side=LEFT, fill=X, expand=True, padx=(2, 0))
        
        self.create_t_widget(ttk.Button, stop_frame, "btn_estop", bootstyle=DANGER, command=self.motor_acil_stop).pack(pady=4, fill=X)
        self.create_t_widget(ttk.Button, stop_frame, "btn_report", bootstyle=INFO, command=self.rapor_olustur).pack(pady=4, fill=X)

        # --- SAĞ PANEL (Grafikler Notebook) ---
        sag_panel = ttk.Frame(main_layout)
        sag_panel.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

        self.chart_notebook = ttk.Notebook(sag_panel, bootstyle="warning")
        self.chart_notebook.pack(fill=BOTH, expand=True)

        tab_curr = ttk.Frame(self.chart_notebook, padding=10)
        self.chart_notebook.add(tab_curr, text=self.texts[self.dil]["tab_chart_curr"])
        self.ui_tabs.append((self.chart_notebook, 0, "tab_chart_curr"))

        tab_mech = ttk.Frame(self.chart_notebook, padding=10)
        self.chart_notebook.add(tab_mech, text=self.texts[self.dil]["tab_chart_mech"])
        self.ui_tabs.append((self.chart_notebook, 1, "tab_chart_mech"))

        tab_pwr = ttk.Frame(self.chart_notebook, padding=10)
        self.chart_notebook.add(tab_pwr, text=self.texts[self.dil]["tab_chart_pwr"])
        self.ui_tabs.append((self.chart_notebook, 2, "tab_chart_pwr"))

        # 1. Faz Akımları
        self.fig_curr, self.ax_curr = plt.subplots(3, 1, figsize=(8, 6), dpi=95)
        self.fig_curr.tight_layout(pad=3.0)
        self.lines_curr = []
        for ax, title, color in zip(self.ax_curr, ["U Phase Current", "V Phase Current", "W Phase Current"], ['r', 'g', 'b']):
            ax.set_title(title, fontdict={'fontsize': 10, 'fontweight': 'bold'})
            line, = ax.plot([], [], color=color, linewidth=2)
            self.lines_curr.append(line)
        self.canvas_curr = FigureCanvasTkAgg(self.fig_curr, master=tab_curr)
        self.canvas_curr.get_tk_widget().pack(fill=BOTH, expand=True)

        # 2. Mekanik (Hız/Tork)
        self.fig_mech, self.ax_mech = plt.subplots(2, 1, figsize=(8, 6), dpi=95)
        self.fig_mech.tight_layout(pad=3.0)
        self.ax_mech[0].set_title(self.texts[self.dil]["chart_speed"], fontdict={'fontsize': 10, 'fontweight': 'bold'})
        self.line_speed, = self.ax_mech[0].plot([], [], color='cyan', linewidth=2)
        self.ax_mech[1].set_title(self.texts[self.dil]["chart_torque"], fontdict={'fontsize': 10, 'fontweight': 'bold'})
        self.line_torque, = self.ax_mech[1].plot([], [], color='orange', linewidth=2)
        self.canvas_mech = FigureCanvasTkAgg(self.fig_mech, master=tab_mech)
        self.canvas_mech.get_tk_widget().pack(fill=BOTH, expand=True)

        # 3. Güç (Bara/Aktif)
        self.fig_pwr, self.ax_pwr = plt.subplots(2, 1, figsize=(8, 6), dpi=95)
        self.fig_pwr.tight_layout(pad=3.0)
        self.ax_pwr[0].set_title(self.texts[self.dil]["chart_power"], fontdict={'fontsize': 10, 'fontweight': 'bold'})
        self.line_power, = self.ax_pwr[0].plot([], [], color='magenta', linewidth=2)
        self.ax_pwr[1].set_title(self.texts[self.dil]["chart_volt"], fontdict={'fontsize': 10, 'fontweight': 'bold'})
        self.line_volt, = self.ax_pwr[1].plot([], [], color='yellow', linewidth=2)
        self.canvas_pwr = FigureCanvasTkAgg(self.fig_pwr, master=tab_pwr)
        self.canvas_pwr.get_tk_widget().pack(fill=BOTH, expand=True)

        self.grafik_tema_guncelle()

    def grafik_tema_guncelle(self):
        if not hasattr(self, 'fig_curr'): return
        bg_color = '#ffffff' if self.tema == 'light' else '#1e1e1e'
        fig_bg = '#f5f5f5' if self.tema == 'light' else '#222222'
        grid_color = '#e0e0e0' if self.tema == 'light' else '#333333'
        text_color = '#333333' if self.tema == 'light' else '#aaaaaa'
        title_color = '#000000' if self.tema == 'light' else '#ffffff'
        
        figures = [(self.fig_curr, self.ax_curr), (self.fig_mech, self.ax_mech), (self.fig_pwr, self.ax_pwr)]
        
        for fig, axes in figures:
            fig.patch.set_facecolor(fig_bg)
            for ax in axes:
                ax.set_facecolor(bg_color)
                ax.grid(True, color=grid_color, linestyle='--')
                ax.tick_params(colors=text_color)
                ax.title.set_color(title_color)
                for spine in ax.spines.values():
                    spine.set_color(grid_color)
            axes[-1].set_xlabel(self.texts[self.dil]["chart_time"], color=text_color)
            if axes is self.ax_curr:
                for ax in axes: ax.set_ylabel(self.texts[self.dil]["chart_curr"], color=text_color)
            
        self.canvas_curr.draw()
        self.canvas_mech.draw()
        self.canvas_pwr.draw()

if __name__ == "__main__":
    app_root = ttk.Window(themename="darkly") 
    app = UltimateACS880App(app_root)
    app_root.mainloop()