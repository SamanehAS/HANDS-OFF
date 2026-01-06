
# Hands Off

## Overview

**Hands Off** is a background service designed to help users reduce **Body-Focused Repetitive Behaviors (BFRBs)** such as nail biting, skin picking, and similar unconscious habits that often occur during periods of stress or deep concentration—especially while working in front of a laptop.

The service runs **locally on the user's device** as a background process and continuously monitors hand-to-face interactions in real time. When a risky behavior is detected, Hands Off intervenes immediately through subtle feedback mechanisms to raise awareness and interrupt the habit.

---

## Problem Statement

Many people unconsciously engage in behaviors like nail biting or skin picking while studying, coding, or working under stress. These behaviors:

* Happen automatically and without awareness
* Are difficult to control using willpower alone
* Can lead to physical damage and long-term habits

Existing solutions are often limited to reminders or wearable devices and do not provide **real-time, context-aware intervention** on personal computers.

---

## Solution

Hands Off addresses this problem by combining **computer vision** and **real-time behavior analysis** in a privacy-preserving, offline desktop application.

Core ideas:

* Detect hand movements toward the face using a camera
* Identify patterns associated with BFRBs
* Trigger immediate feedback to stop the behavior before it continues

---

## Key Features

* Runs as a background service (no constant UI required)
* Real-time hand and face interaction detection
* Local processing (no cloud, no data upload)
* Immediate feedback via system notifications, audio cues, or peripheral signals
* Lightweight and resource-aware for long working sessions
* Modular architecture for future ML model improvements

---

## Target Users

* Students during long study sessions
* Developers and knowledge workers
* Individuals struggling with stress-induced BFRBs

---

## Project Status

This project is currently under active development. The initial focus is on:

* Designing the system architecture
* Implementing reliable hand-to-face detection
* Building a lightweight background service prototype

---

## Ethical & Privacy Considerations

* All processing is done locally
* No video data is stored or transmitted
* User privacy is a core design principle

---

## Future Work

* Personalized behavior modeling
* Adaptive feedback strategies
* Detailed analytics for habit tracking
* Support for multiple operating systems

---

## Team

This project is developed collaboratively as an open-source initiative.

Contributions, suggestions, and discussions are welcome.
