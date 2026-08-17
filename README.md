# ⚡ ABB ACS880 Smart Management & SCADA Panel

This project is an advanced, industrial-grade Python application designed to control, monitor, and analyze ABB ACS880 drives and connected motors via the **Modbus RTU/ASCII** protocol. It serves as a modern, lightweight alternative to heavy SCADA systems like LabVIEW, providing real-time telemetry, dynamic charts, and hardware configuration wizards.

Developed specifically for the **AGU Power Lab & Electrical Machines** environment.

## 🚀 Key Features

*   **Real-time Modbus Communication:** Fast and reliable connection via serial port (RS-485 / Modbus RTU).
*   **Universal Device Profile Wizard:** Easily swap torque sensors or motor drives. Instead of hardcoding parameters, the built-in wizard allows you to import/export JSON device profiles mapping Control Words, Scale Factors, and Modbus Addresses.
*   **Live Telemetry & Data Logging:** Dynamic tracking of:
    *   3-Phase Currents (U, V, W)
    *   Motor Speed (RPM) & Torque (%)
    *   Active Power (kW) & DC Bus Voltage
*   **Professional UI/UX:** Built using `ttkbootstrap` for a sleek, dark/light themed, responsive dashboard.
*   **Bilingual Support:** Seamlessly switch between English and Turkish interfaces.
*   **Safety First:** Includes software-level Emergency Stop (E-Stop) and drive fault/alarm status monitoring via a parsed 16-bit Status Word.

## 🛠️ Technology Stack
*   **Language:** Python 3
*   **GUI Framework:** `ttkbootstrap` (Tkinter)
*   **Modbus Protocol:** `minimalmodbus`, `pyserial`
*   **Data Visualization:** `matplotlib`, `pandas`

## ⚙️ How to Run

1. Clone or download the repository.
2. Install the required dependencies:
   ```bash
   pip install ttkbootstrap matplotlib pandas minimalmodbus pyserial
   ```
3. Run the main application:
   ```bash
   python app1.py
   ```
4. Configure your COM Port and click **Start Communication**.

## 🔌 Hardware Configuration (JSON Profiles)
You do not need to modify the Python code to change the target drive. Click the **Hardware Config (⚙️)** button in the UI to:
*   Set new Control Words (Start/Stop registers).
*   Change scaling multipliers for torque/speed sensors.
*   Update Parity, Stop Bits, and Timeout settings.
*   Export these settings as a `.json` profile for future use!

---
*Designed for robust industrial automation and academic motor testing.*
