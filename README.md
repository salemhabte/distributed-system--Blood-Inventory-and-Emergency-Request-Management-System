# distributed-system--Blood-Inventory-and-Emergency-Request-Management-System


A distributed **microservices-based platform** designed to modernize and automate emergency blood requests between hospitals and blood banks using real-time communication and event-driven architecture.

---

## 📌 Overview

Traditional blood request workflows rely on manual phone calls and delayed coordination, which can cause critical delays during emergencies. This system solves those problems by enabling **fast, accurate, and automated communication** between hospitals and blood banks.

The platform is built using **independently deployable microservices** that communicate via **REST APIs** and **Pub/Sub messaging**, ensuring scalability, reliability, and rapid emergency response.

---

## 🧩 Microservices Architecture

The system consists of **three core microservices**:

### 1️⃣ Hospital Service

Handles all hospital-side operations.

**Responsibilities:**

* Create emergency and scheduled blood requests
* Maintain hospital-local blood inventory
* Track request statuses in real time
* Publish `BloodRequestCreated` events
* Subscribe to request decision and inventory events

---

### 2️⃣ Blood Bank Inventory Service

Acts as the central authority for blood inventory.

**Responsibilities:**

* Maintain blood inventory (type, quantity, expiry, batch)
* Validate and approve/reject blood requests
* Allocate blood units and update stock
* Publish inventory and decision events
* Generate low-stock alerts

---

### 3️⃣ Notification Service

Ensures all stakeholders are informed in real time.

**Responsibilities:**

* Subscribe to system events from all services
* Send in-app notifications for:

  * New blood requests
  * Request approvals or rejections
  * Inventory updates
  * Low or critical stock levels
* Publish notification delivery confirmation events

---

## 🔄 Communication Model

* **Synchronous:** REST APIs for CRUD and direct service interactions
* **Asynchronous:** Pub/Sub messaging (RabbitMQ, Kafka, or Redis Streams)
* **Event-driven workflows** for request handling and inventory updates

This design enables:

* Independent scaling
* Fault isolation
* High availability during emergencies

---

## 📊 High-Level Workflow

1. Hospital staff submit a blood request
2. Hospital Service publishes `hospital.blood.requested`
3. Blood Bank Inventory Service validates availability
4. Blood Bank publishes:

   * `bloodbank.blood.approved` **or**
   * `bloodbank.blood.rejected`
5. Notification Service alerts relevant users
6. Hospital dashboards update automatically

---

