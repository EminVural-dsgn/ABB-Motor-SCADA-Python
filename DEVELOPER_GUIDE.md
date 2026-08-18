# 👨‍💻 DEVELOPER GUIDE & ARCHITECTURE DOCUMENT

## 🎯 Purpose of this File
This document is a technical onboarding guide designed for developers, contributors, and intelligent assistants who want to understand the codebase quickly. It explains the architecture, design patterns, and specific implementation details of the **ABB ACS880 SCADA Panel** project. Use this as your primary source of truth before modifying the code.

---

## 📂 Project Structure
*   `app1.py`: The monolithic main application file containing the UI (Tkinter), serial communication logic (minimalmodbus), and live plotting (matplotlib).
*   `config.json`: The dynamic configuration file that stores hardware profiles (Modbus addresses, Control words, Scaling multipliers). This allows the software to be hardware-agnostic.
*   `README.md`: General user-facing documentation.

---

## 🏗️ Core Architecture & Component Map (`app1.py`)

### 1. The Configuration Engine (Lines 300 - 350)
*   **Functions:** `yukle_ayarlar()`, `kaydet_ayarlar()`
*   **How it works:** Instead of hardcoding hardware dependencies, the system relies on 4 core dictionaries:
    *   `serial_config`: Holds `parity`, `stopbits`, `timeout`.
    *   `control_words`: Holds the state machine triggers (`cw_speed_rdy`, `cw_speed_run`, `cw_stop`, etc.).
    *   `adres_haritasi` (modbus_addresses): Maps UI actions to specific Modbus holding registers (e.g., `write_cw`, `read_tork`).
    *   `katsayi_tablosu` (scaling_factors): Holds float multipliers for raw sensor data (e.g., Speed Read Scale).
*   *Developer Note:* If you need to add a new parameter, add it to these dictionaries first. The UI and JSON system will automatically handle it.

### 2. The Setup Wizard & Profile Manager (Lines 350 - 550)
*   **Functions:** `pencere_kalibrasyon()`, `kalibrasyon_kaydet()`, `profil_ice_aktar()`, `profil_disa_aktar()`
*   **How it works:** A 4-tab `ttk.Notebook` UI that exposes the 4 configuration dictionaries to the user. 
*   **Import/Export:** Uses `tkinter.filedialog` to save/load the entire hardware state as `.json` files. *Developer Note:* When implementing new hardware features, ensure they are compatible with this JSON import/export pipeline.

### 3. Modbus Communication (Lines 600 - 650)
*   **Functions:** `modbus_baglan()`, `motor_baslat()`, `motor_durdur()`, `motor_acil_stop()`
*   **How it works:** Uses `minimalmodbus.Instrument` with `pyserial`.
*   *Critical Detail:* Control Words are fetched dynamically from `self.control_words`. For example, `motor_baslat()` fetches `cw_speed_rdy` and then schedules `cw_speed_run` 100ms later using `root.after(100)`.

### 4. Asynchronous Telemetry Loop (Lines 700 - 800)
*   **Functions:** `canli_okuma_dongusu()`, `tum_parametreleri_yaz()`
*   **How it works:** **DO NOT USE `time.sleep()` OR `threading` FOR MODBUS POLLING.** The system achieves a non-blocking UI by recursively calling `self.root.after(500, self.canli_okuma_dongusu)`.
*   *Data Parsing:* The Status Word is read as a 16-bit integer, shifted, and mapped to a 12-bit status list to update the UI indicators dynamically.

### 5. Live Plotting & Theming (Lines 150 - 250, 420 - 460)
*   **How it works:** Uses `matplotlib.backends.backend_tkagg.FigureCanvasTkAgg` embedded in Tkinter frames. Data is stored in `collections.deque` with a `maxlen` to prevent memory overflow.
*   *Theming Issue:* When Tkinter themes switch (Dark/Light), matplotlib doesn't auto-update. We wrote a custom `grafik_tema_guncelle()` function to explicitly change axis colors and figure facecolors on the fly.

---

## 🛠️ Strict Guidelines for Future Contributors
1.  **UI Updates:** We use `ttkbootstrap`, NOT standard `tkinter`. Always use `bootstyle` parameters for coloring buttons and labels.
2.  **Concurrency:** Avoid the `threading` module if possible. Stick to Tkinter's `.after()` loop for periodic Modbus tasks.
3.  **Language:** Keep the application's internal variables named in a mix of Turkish/English (as originally written), but keep the `self.texts` dictionary updated for EN/TR UI translations.
4.  **Hardware Independence:** Never hardcode a Modbus address or Control Word directly into `app1.py`'s logic functions. Always route it through the `self.control_words` or `self.adres_haritasi` dictionaries so it can be managed by the Profile Wizard.
