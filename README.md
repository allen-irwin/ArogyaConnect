# ArogyaConnect: Autonomous Healthcare Routing Concierge

ArogyaConnect is a multi-agent healthcare concierge system built with the Google Agent Development Kit (ADK 2.0). It intelligently triages patient symptoms, enforces strict clinical safety guardrails, and autonomously routes users to the appropriate medical specialists within the Bengaluru healthcare network.

This project was developed as a capstone submission for the Intensive Vibe Coding Course.

---

## 🛑 The Problem
Navigating the healthcare system is often overwhelming for patients. When individuals experience symptoms, they frequently struggle to accurately assess the urgency of their condition or identify the correct specialist. This leads to delayed emergency care for critical issues and inefficient booking for routine inquiries, burdening both the patient and the medical infrastructure.

## 💡 The Solution
ArogyaConnect acts as an intelligent first point of contact. Instead of forcing users through complex clinical dropdown menus, patients can describe their symptoms in plain language. The system utilizes a multi-agent graph architecture to:
1. **Triage** the urgency of the condition.
2. **Short-circuit** the workflow to provide immediate guidance for critical emergencies.
3. **Route** routine inquiries to a specialist matcher.
4. **Query** a local hospital database via an MCP server to recommend specific doctors and facilitate booking.
5. **Securely deflect** any requests for clinical diagnoses or prescriptions, ensuring patient safety.

---

## 🏗️ System Architecture

ArogyaConnect utilizes a graph-based workflow managed by the ADK. The workload is distributed across specialized AI agents to ensure accurate routing and maintain strict operational boundaries.

```text
[User Input: Plain-language symptoms]
       |
       v
+--------------------------+
|    Classifier Agent      |  <-- Assesses urgency and extracts entities
+--------------------------+
       |
       +------------------------------------+
       |                                    |
 [CRITICAL URGENCY]                  [ROUTINE URGENCY]
       |                                    |
       v                                    v
+--------------------------+      +--------------------------+
|    Emergency Agent       |      | Specialist Matcher Agent |  <-- Guardrails enforced
+--------------------------+      +--------------------------+
(Provides immediate first-                    |
 aid protocols & escalation)                  v
                                  +--------------------------+
                                  |       MCP Server         |  <-- Tool: get_doctors_by_specialty
                                  |  (Bengaluru Doctor DB)   |
                                  +--------------------------+
