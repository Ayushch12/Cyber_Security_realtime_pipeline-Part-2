# 🛡️ SOC Security Data Pipeline & Dashboard

> **CYNA – Data Engineer Internship Technical Test**

## Overview

This project simulates a Security Operations Center (SOC) data pipeline.

The system ingests IDS (Intrusion Detection System) logs in real time, enriches them with external threat intelligence, and stores the results for visualization and analysis using Grafana.

The primary objective is to :
- Ingest IDS logs continuously
- Detect connections involving malicious IPs
- Enrich events with threat intelligence confidence scores
- Store structured data in Elasticsearch
- Visualize security insights in real time

The project focuses exclusively on IDS logs (ids.log), because they contain explicit network connections (source -> estination), which directly align with malicious IP enrichment.

The focus of this project is clarity, correctness, and realistic design choices, rather than building an overly complex system.

---

##  Architecture
<img width="2459" height="1376" alt="SOC CYNA Arch" src="https://github.com/user-attachments/assets/79f154d9-6f94-475e-b5ab-040284205f90" />
---

# Architectural Choices

## 1. Event-Driven Architecture

This project is built using an event driven architecture to simulate how modern Security Operations Centers (SOCs) process logs in real time.
Instead of directly pushing logs into a database, events flow through a streaming pipeline. This design improves:
- Reliability  
- Scalability  
- Separation of concerns between system components  

## 2. Apache Kafka as the Streaming Layer

Apache Kafka is used as the central event streaming platform.
It provides:

- Reliable message buffering  
- Decoupling between producers and consumers  
- Fault tolerance  
- Scalability through consumer groups  

Kafka ensures that IDS events are not lost, even if downstream systems temporarily fail. It also allows the system to scale horizontally in the future.

## 3. Elasticsearch for Storage and Analytics

Elasticsearch is used as the storage and analytics engine.
It was chosen because it:

- Indexes logs in near real time  
- Supports fast full-text search  
- Provides powerful aggregation capabilities  
- Is widely used in security and SIEM platforms  

This makes it ideal for storing enriched IDS events and running analytical queries on security data.

## 4. Grafana for Visualization
Grafana is used to build the SOC dashboard layer.
It allows:

- Real time data visualization  
- Aggregation based panels  
- Clear representation of security trends  
- Operational monitoring views  

This transforms raw security events into actionable insights.

## 5. Threat Intelligence Enrichment

Raw IDS logs alone provide limited context.
This system enriches events using an external threat intelligence feed (IPSum).
Enrichment enables:
- Identification of malicious IP addresses  
- Context-aware analysis  
- Enhanced visibility into attack behavior  

This makes the pipeline more aligned with real-world SOC practices.

## 6. Containerized Deployment

All core services (Kafka, Elasticsearch, Grafana) run in Docker containers.
This provides:
- Environment consistency  
- Easy setup and deployment  
- Service isolation  
- Reproducibility  

The project can be launched quickly using Docker Compose.

# Why This Design Matters

This architecture reflects how real-world security monitoring systems are structured:
- Logs are streamed  
- Events are enriched  
- Data is indexed  
- Dashboards provide insight  

The system is modular, scalable, and designed with production-style principles in mind.

# Running the Project
---
## 1. Start Infrastructure
Navigate to the docker directory and start all services:

```bash
docker compose up -d
```
This will start:
- Kafka
- Zookeeper
- Elasticsearch
- Grafana
- Other required services
## 2. Start Kafka : Consumer
Run the Kafka consumer to begin processing incoming events:

```bash
python -m consumer.consumer
```
The consumer will:
- Read messages from Kafka
- Perform enrichment
- Send events to Elasticsearch
## 3. Replay IDS Logs : Producer
Replay the IDS logs to simulate real-time traffic:
```bash
python -m replay.replay_ids_log
```
This will:

- Read logs from sample_logs/ids.log
- Send events to Kafka
- Trigger the full processing pipeline
## 4. Open Grafana
Open Grafana in your browser:
```
http://localhost:3000
```
Default login credentials:
```
User name: admin / Password: admin
```
```
Click on New Dashboard Folder for the Granafa Dashboard.
```
## Configure Elasticsearch Data Source in Grafana

Add a new Elasticsearch data source with the following settings:

URL:
http://elasticsearch:9200

Index:
```
ids-events
```
Time field:
``` 
@timestamp
```

## Tech Stack

- **Language:**   Python 3.10
- **framework:**   FastAPI
- **Streaming:**   Apache Kafka  
- **Storage:**   Elasticsearch 8  
- **Dashboard:** Grafana  
- **Containerization:** Docker/Docker Compose
- **Log Generation:** Security Log Generator  
- **Threat Intelligence:** IPSUM
  
# Data Pipeline
This section describes how security events flow through the system, from raw IDS logs to indexed documents in Elasticsearch.

## Step-by-Step Data Flow

### 1. IDS Log Ingestion
Logs are replayed from:
```bash
sample_logs/ids.log
```
Each line is parsed into structured JSON:
```json
{
  "@timestamp": "...",
  "log_type": "ids",
  "severity": "...",
  "protocol": "...",
  "source_ip": "...",
  "destination_ip": "...",
  "attack_type": "..."
}
```
### 2. Threat Intelligence Enrichment
The system integrates with the IPSum threat intelligence feed.
The feed provides:
```
IP → blacklist confidence score
```
For each event:
- Check source_ip against the threat feed
- Check destination_ip against the threat feed
- If a match is found, mark the event as malicious
- Attach the blacklist confidence score

Example enriched event:

```json
{
  "source_ip": "213.209.159.158",
  "is_malicious": true,
  "confidence": 11
}
```

### 3. Kafka Streaming
Events are sent to the Kafka topic:
```
ids-raw-logs
```
This simulates real-time SOC ingestion and allows scalable event streaming.

### 4. Kafka Consumer Processing

The Kafka consumer:
- Reads events from ids-raw-logs
- Performs enrichment (if required)
- Processes and formats the event
- Indexes the event into Elasticsearch

### 5. Elasticsearch Storage

Events are indexed into:
```
ids-events
```
The index uses structured mappings with the following field types:

- date
- keyword
- ip
- boolean
- integer

This enables efficient querying, filtering, aggregation, and threat hunting.

# SOC Dashboard
### Total IDS Events Over Time

- Displays the volume of IDS events over a selected time range.  
- This helps detect traffic spikes or unusual activity.

### Malicious Events Count

- Shows how many events involve IPs flagged in the threat intelligence feed.

### Top Malicious Source IPs

- Identifies which source IPs are most frequently marked as malicious.

### Attack Type Distribution

- Breaks down events by attack type (e.g., Port Scanning, DoS, Malware).

### Severity Breakdown

- Shows the distribution of severity levels (low, medium, high, critical).

The dashboard simulates what a Security Operations Center (SOC) analyst would use to monitor threats in real time.

# What Was Achieved

This project successfully demonstrates:

- Real time ingestion of IDS logs  
- Kafka based streaming architecture  
- Threat intelligence enrichment using IPSum  
- Structured indexing in Elasticsearch  
- Real time visualization in Grafana  
- Dockerized infrastructure setup  
- Modular and maintainable Python codebase  

The pipeline processes security events end-to-end, from raw logs to visual insights.

# What Insights the Dashboard Provides

The dashboard allows analysts to:

- Detect malicious IP communication in real time  
- Identify spikes in suspicious network activity  
- Understand which attack types are most common  
- Monitor the severity of detected threats  
- Prioritize events based on confidence score  

It transforms raw IDS logs into actionable security intelligence.

# What Is Not Done Yet(This will be done during Stage in Cyna 😃)

The current implementation focuses on core functionality.

Possible improvements include:

- Real-time alerting (In email or Slack notifications)  
- Role-based access control and authentication  
- Kafka scaling with multiple partitions  
- Production-grade monitoring and logging  
- CI/CD pipeline for deployment automation  
## Why Did I Change the Architecture?
### Question:
Before I used batch processing and DuckDB, now I am using Kafka and Elasticsearch, why?
### Before:
I used batch processing with Python, DuckDB, and Streamlit. The system processed logs when I manually ran the backend script, enriched them using SQL joins, and displayed the results in a dashboard. It was simple, resource-efficient, and easy to debug.

### After:
I redesigned the project into a real-time streaming pipeline using Kafka, Elasticsearch, and Grafana. Logs are now streamed continuously, enriched dynamically, indexed in Elasticsearch, and visualized in real time.

### Why?
The first version helped validate the core logic  ingestion, enrichment, and analysis but it was batch-based and not real-time. 
In real SOC environments, security monitoring is continuous and event-driven. By moving to a streaming architecture, the system became more realistic, scalable, and aligned with production-level security systems.

## Challenges Faced

## Why I Chose This Stack

I chose this stack because I’m already comfortable with most of these technologies. I use Python (FastAPI) and work with data tools regularly in my daily learning and projects, so it felt natural to build the system around them.

Before, I was using DuckDB as the central database. It worked well for batch processing and analytical queries. But when I started moving toward a real-time streaming architecture, I found it a bit difficult to use DuckDB in that setup. It’s great for analytics, but not really designed for continuous real-time indexing and search.

That’s why I decided to switch to Elasticsearch. The only new technology for me was Elasticsearch 8. I hadn’t worked with it before in any project. To make the real-time architecture stronger and more realistic, I decided to implement it in this project.

I learned the basics from official documentation, Medium, AI,and by discussing with people who had experience with it. I’m not perfect in Elasticsearch yet, but through this project I understood the core concepts and how to implement it properly.

I wanted to challenge myself and learn something new instead of staying only with tools I already know. 

## Question

Why did you choose to use only IDS logs from the Security Log Generator instead of also using web access logs and endpoint logs?

## Answer :

I chose to focus on IDS logs because the project requirement clearly states that the system must “enrich security logs by identifying connections to/from malicious IPs.

IDS logs are the most appropriate source for this objective because they contain clear source and destination IP addresses. This makes it straightforward to detect and enrich malicious network connections.

Web access logs and endpoint logs also provide useful information, but they are less directly aligned with IP-based connection analysis. To keep the architecture focused and aligned with the core objective, I intentionally started with IDS logs.

Since the pipeline is modular and Kafka-based, additional log types (such as web or endpoint logs) can easily be integrated later without changing the overall design.


## Dashboard Grafana 

<img width="1324" height="612" alt="image" src="https://github.com/user-attachments/assets/9e621d92-d142-4231-ab2a-02ccdedd6334" />

I tried with the some of the malicious logs, to verify wheather its working or not.

In this system, an event is marked as malicious only if the source IP or destination IP exists in the IPSUM dataset. If there is no match, the event is treated as benign.

To confirm that the detection and enrichment logic works correctly, I tested the pipeline by manually adding a known malicious IP from the IPSUM dataset into the IDS logs.



                                                                             Merci ...


