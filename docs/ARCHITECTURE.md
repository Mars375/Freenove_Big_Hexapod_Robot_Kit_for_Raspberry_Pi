# Tachikoma Project Architecture

This document outlines the core architecture of the Tachikoma project. Its purpose is to establish clear boundaries, define data and control flows, and provide strict guidelines for all developers (Agents) working on the project.

**The primary goal is to maintain a clean, decoupled, and stable core.**

## 1. Architectural Layers

The project is divided into distinct layers, each with a specific responsibility. Direct communication should only happen between adjacent layers.

```
+------------------+
|      GUI         |  (User Interface, e.g., Agent F)
+-------+----------+
        |
+-------v----------+
|      API         |  (HTTP/WebSocket endpoints, e.g., Agent G)
+-------+----------+
        |
+-------v----------+
|    Features      |  (Autonomous logic, Vision, e.g., Agent E, H)
+-------+----------+
        |
+-------v----------+
|      Core        |  (Business Logic, State, Interfaces - Agent A)
+-------+----------+
        |
+-------v----------+
|    Hardware      |  (Drivers, Implementations - Agent B, C, D)
+------------------+
```

-   **GUI (Graphic User Interface):** The presentation layer. It communicates exclusively with the `API` layer.
-   **API (Application Programming Interface):** The entry point for all external interactions. It exposes the robot's capabilities via HTTP and WebSockets. It translates external requests into calls to the `Core` or `Features`.
-   **Features:** High-level functionalities like autonomous navigation, object detection, etc. These features consume services from the `Core` layer.
-   **Core:** The brain of the robot. It contains the central `RobotState`, abstract `interfaces` for hardware control, and the main business logic that orchestrates hardware. **This layer must remain independent of any specific hardware implementation or high-level feature.**
-   **Hardware:** The implementation layer. It contains the concrete drivers and logic to control the physical hardware (servos, sensors, LEDs). It **must** implement the interfaces defined in the `Core` layer.

## 2. Data Flow (Hardware to User)

The data flow describes how information from the robot's sensors is propagated up to the user interface. The flow is unidirectional.

```
[Physical Sensors] -> [Hardware Drivers] -> [Core (SensorProvider)] -> [RobotState] -> [API (WebSocket)] -> [GUI]
```

1.  **Hardware Drivers** (e.g., `IMU.py`, `Ultrasonic.py`) read raw data from the physical sensors.
2.  The concrete **`SensorProvider` implementation** (Agent D) aggregates this data.
3.  A core process continuously calls the `SensorProvider.read()` method and updates the single, shared **`RobotState`**.
4.  The **API layer** (Agent G) observes changes in the `RobotState` and pushes them out via a WebSocket endpoint.
5.  The **GUI** (Agent F) subscribes to the WebSocket and updates the display in real-time.

## 3. Control Flow (User to Hardware)

The control flow describes how commands from a user or an autonomous system are propagated down to the hardware.

```
[GUI/Autonomy] -> [API (HTTP)] -> [Core (MovementController)] -> [Hardware Implementation] -> [Physical Servos]
```

1.  A **User Action (GUI)** or an **Autonomous Decision (Features)** is triggered.
2.  It sends a command to the **API layer** via an HTTP request (e.g., `POST /move`).
3.  The API endpoint validates the request and calls the appropriate method on a `Core` interface (e.g., `MovementController.move(...)`).
4.  The `Core` layer invokes the method on the concrete **Hardware Implementation** class that was injected.
5.  The hardware driver translates the command into low-level signals for the **Physical Servos**.

## 4. Rules and Prohibitions for Agents

To ensure the stability and scalability of the project, the following rules are **ABSOLUTE** and non-negotiable.

-   **DO NOT MODIFY THE `core/interfaces` or `core/types.py` files.** These form the central contract. Any change must be validated by Agent A.
-   **Hardware Agents (B, C, D) MUST implement the core interfaces.** Your implementation code lives in `tachikoma/hardware/*`. You do not call the API or modify the GUI.
-   **Feature Agents (E, H) MUST only interact with the `Core` interfaces.** You do not directly access the `Hardware` layer.
-   **API and GUI Agents (F, G) MUST only interact with the `Core` interfaces and `RobotState`.** You do not have knowledge of specific hardware implementations.
-   **The `Core` layer MUST NOT depend on any other layer.** It is the foundation. It cannot import from `api`, `features`, or `hardware` implementations.
-   **Keep interfaces SYNCHRONOUS.** Asynchronous operations will be handled at a higher level (e.g., in the API layer via FastAPI tasks).
-   **The `RobotState` is the SINGLE SOURCE OF TRUTH.** Do not maintain a separate state elsewhere. It represents what the robot *is*, not what it *should do*.
