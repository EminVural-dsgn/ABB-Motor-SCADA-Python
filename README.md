# ⚡ ABB ACS880 Smart Management & SCADA Panel

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Modbus](https://img.shields.io/badge/Protocol-Modbus_RTU-orange.svg)
![Tkinter](https://img.shields.io/badge/GUI-ttkbootstrap-brightgreen.svg)

This project is an advanced, industrial-grade Python application designed to control, monitor, and analyze ABB ACS880 drives and connected motors via the **Modbus RTU/ASCII** protocol. It serves as a modern, lightweight alternative to heavy SCADA systems like LabVIEW, providing real-time telemetry, dynamic charts, and hardware configuration wizards.

Developed specifically for the **AGU Power Lab & Electrical Machines** environment.

---

## 🎯 Project Motivation
Industrial drives usually require proprietary or highly complex software to monitor and control. The goal of this project was to build a highly responsive, bilingual (EN/TR), and visually appealing SCADA dashboard from scratch that directly communicates with the hardware. 

Rather than hardcoding the application for a single motor, the architecture was designed to be **Universal**, allowing seamless integration with different drives (e.g., Siemens, Danfoss) or custom torque sensors via a dynamic JSON profiling system.

---

## 🚀 Core Features & Architecture

### 1. Universal Device Profile Wizard
Different drives have completely different Modbus register maps and scaling requirements. We solved this by implementing a dynamic **Profile Manager**:
*   **Modbus Register Mapping:** Every parameter (Speed Ref, Torque Ref, Current, Voltage) is mapped to a specific address. The application reads these addresses dynamically.
*   **Control Words (State Machine):** To start the ABB drive in speed mode, the software must sequentially send `1142` (Ready) and then `1151` (Run). These "Control Words" are fully customizable via the UI, allowing adaptation to non-ABB drives.
*   **Import / Export `.json`:** Users can export the entire hardware configuration (Addresses, Multipliers, Parity, Stop bits) as a `.json` file and import new profiles with a single click—effectively digitizing the hardware manual.

### 2. Live Telemetry & Asynchronous Data Logging
*   **Non-Blocking UI:** Modbus communication inherently takes time. Using standard `time.sleep()` would freeze the GUI. We overcame this by utilizing Tkinter's `.after()` method, creating an asynchronous polling loop that fetches data every 200ms-500ms without interrupting the user experience.
*   **Dynamic Tracking:** Real-time plotting of 3-Phase Currents (U, V, W), Motor Speed (RPM), Torque (%), Active Power (kW), and DC Bus Voltage using `matplotlib`.

### 3. Safety & Status Word Parsing
*   **Emergency Stop:** Software-level E-Stop sequences are prioritized.
*   **16-bit Status Parsing:** The drive returns a single 16-bit Status Word. The software parses this integer bit-by-bit to isolate 12 distinct flags (e.g., `RDY_ON`, `TRIPPED`, `ALARM`) and updates the UI indicators dynamically with color-coded alerts (Red for Danger, Green for Safe).

### 4. Advanced Testing & Automated Reporting
*   **Timed Operation & Live Counter:** In addition to manual Start/Stop controls, a custom timer allows running tests for exact durations (Minutes or Seconds). The UI features a real-time visual countdown box (`Time Left: 00:00`), which automatically triggers a shutdown sequence when it reaches zero.
*   **Excel Telemetry Dumps:** Upon stopping the motor (manually or via timer), the entire run's telemetry data is automatically exported into a detailed Excel `.xlsx` report including timestamp, elapsed seconds, torque, speeds, active power, voltage, and individual phase currents.
*   **Compact UI & Dual Mode Control:** The left-hand operation panel is specifically designed to fit compact screen resolutions (e.g., 1366x768) without getting clipped. Full continuous support for both Speed Reference and Torque Reference commands without drive faults, preventing vibrations during torque holding.

---

## 🧠 Challenges & Lessons Learned

Building a bridge between software and heavy industrial hardware presented several engineering challenges:

1. **The UI Freezing Problem (Threading vs Event Loop):** 
   * *Challenge:* Initially, continuous Modbus reading caused the GUI to freeze. 
   * *Solution:* We learned that UI frameworks operate on a main event loop. By offloading the Modbus read/write commands to Tkinter's `root.after()` event scheduler, we achieved seamless live data streaming without the overhead of complex multithreading.
2. **Chart Theming & Matplotlib Integration:**
   * *Challenge:* When switching the UI between "Dark" and "Light" modes, the `matplotlib` charts remained glaringly white, breaking the visual immersion.
   * *Solution:* We engineered a custom theme-update function that dynamically modifies the figure facecolors, axis colors, and tick parameters of the embedded Matplotlib canvas on the fly.
3. **Hardcoded Limits vs Future Scalability:**
   * *Challenge:* Originally, torque multipliers and Modbus addresses were hardcoded. If a new torque sensor was installed in the lab, the Python code had to be manually edited.
   * *Solution:* We completely decoupled the configuration from the logic. Moving everything to the UI-driven `config.json` system taught us the importance of **Separation of Concerns** in software architecture.

---

## ⚙️ How to Run

**Option A: Running the Executable (Recommended)**
1. Navigate to the `dist` folder or the Desktop.
2. Double-click the compiled `ABB_Smart_SCADA_GUNCEL.exe` file. The application will launch instantly without requiring any Python installation.

**Option B: Running from Source**
1. Clone or download the repository.
2. Install the required dependencies:
   ```bash
   pip install ttkbootstrap matplotlib pandas minimalmodbus pyserial
   ```
3. Run the main application:
   ```bash
   python app1.py
   ```

**Post-Launch:** Click the **Hardware Config (⚙️)** button to set up your drive's Modbus addresses and COM port settings, then click **Start Communication**.

---
*Designed for robust industrial automation and academic motor testing.*
