# ♻️ EcoSort AI — AI Waste Segregation Advisor

An intelligent waste segregation advisor that helps people identify waste categories and understand safer disposal methods.

EcoSort AI combines a React frontend, Python backend, AI classification integration, and a deterministic rules engine to provide waste classification, preparation instructions, and safety warnings.

Built for the **Environmental Hacks 2026 Hackathon**.

## 🌍 Problem Statement

People often struggle to determine whether an item belongs in recycling, compost, hazardous waste, or general waste.

Incorrect disposal can contaminate recyclable materials, damage waste-processing equipment, and expose sanitation workers to hazardous substances.

Items such as lithium-ion batteries, chemical containers, and fluorescent bulbs require special handling rather than ordinary disposal.

## 💡 Our Solution

EcoSort AI provides a simple interface where users can describe a waste item or upload an image to receive disposal guidance.

The application combines classification logic with a deterministic Python rules engine to apply safety checks and provide practical recommendations.

## ✨ Key Features

- **Text-Based Classification:** Enter a description of a waste item.
- **Image Upload:** Upload a waste image for analysis.
- **Four Waste Categories:**
  - ♻️ Recyclable
  - 🌱 Organic
  - ⚠️ Hazardous
  - 🗑️ General Waste
- **Safety Warnings:** Highlight potential hazards associated with waste items.
- **Uncertainty Handling:** Flag uncertain classifications rather than presenting every result as reliable.
- **Contamination Prevention:** Provide guidance for food-soiled packaging and other contaminated materials.
- **Preparation Instructions:** Explain steps such as rinsing containers and safely handling batteries.
- **Interactive Interface:** Explore results through a React-based web application.
- **Local Mock Mode:** Run and test the application without requiring AWS credentials.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| React | Frontend user interface |
| Vite | Frontend development and build tooling |
| Tailwind CSS | UI styling |
| Python | Backend processing |
| AWS Lambda | Serverless backend handler |
| Amazon Bedrock | AI inference integration |
| AWS API Gateway | HTTP API integration |
| Pytest | Backend testing |

## 🏗️ Architecture

The application follows a simple request-processing flow:

```text
User
 |
 v
React Frontend
 |
 | POST /analyze
 v
Backend API
 |
 v
Python Lambda Handler
 |
 v
AI Classifier
 |
 v
Deterministic Rules Engine
 |
 v
Structured Analysis Result
 |
 v
React Frontend
 |
 v
Waste Category, Instructions and Safety Warnings
```

During local development, the frontend communicates with the Python local server.

For AWS deployment, the intended architecture uses API Gateway and AWS Lambda, with Amazon Bedrock available for AI inference when correctly configured.

## 📁 Project Structure

```text
ai-waste-segregation-advisor/
├── backend/
│   ├── __init__.py
│   ├── ai_classifier.py
│   ├── rules_engine.py
│   ├── lambda_handler.py
│   ├── local_server.py
│   ├── requirements.txt
│   └── tests/
│       ├── __init__.py
│       ├── test_ai_classifier.py
│       ├── test_lambda_handler.py
│       └── test_rules_engine.py
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   ├── src/
│   └── public/
│
├── deployment/
│   ├── template.yaml
│   ├── deploy-aws.sh
│   └── iam-policy.json
│
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### Prerequisites

Install the following tools:

- Python 3.10 or later
- Node.js 18 or later
- npm
- Git

AWS CLI and AWS SAM CLI are additionally required for AWS deployment.

### 1. Clone the Repository

```bash
git clone https://github.com/Mufeed06-cmd/EcoSort.git
cd EcoSort
```

### 2. Set Up the Python Backend

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

Install the backend dependencies:

```bash
pip install -r backend/requirements.txt
```

### 3. Install Frontend Dependencies

Open a terminal in the project directory and run:

```bash
cd frontend
npm install
```

Return to the project root:

```bash
cd ..
```

## ▶️ Running the Application

The local application can run using the mock classification engine without connecting to AWS.

### Start the Backend

From the project root:

```bash
source .venv/bin/activate
python -m backend.local_server
```

The backend runs at:

```text
http://localhost:5001
```

### Start the Frontend

Open a second terminal:

```bash
cd frontend
npm run dev
```

Open the local URL displayed by Vite. The current project configuration uses:

```text
http://localhost:3000
```

Keep both terminals running while using the application.

## 🧪 Testing

### Run Backend Tests

From the project root:

```bash
source .venv/bin/activate
python -m pytest backend/tests/ -v
```

The test suite covers backend classification behavior, disposal rules, safety handling, and API validation.

### Build the Frontend

```bash
cd frontend
npm run build
```

Vite generates the production build in:

```text
frontend/dist/
```

## 📡 API Overview

The backend exposes an analysis endpoint:

| Property | Value |
|---|---|
| Endpoint | `/analyze` |
| Method | `POST` |
| Content-Type | `application/json` |

### Example Request

```bash
curl -X POST http://localhost:5001/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "clean aluminum can", "mock": true}'
```

### Image Input

The API supports image uploads using Base64-encoded image data. Supported formats and size restrictions are enforced by the backend.

At least one input—a text description or an image—must be supplied.

Refer to `backend/lambda_handler.py` for the actual request validation and response structure.

## 🧠 AI Classification and Safety Rules

EcoSort AI separates item classification from disposal decision-making.

### 1. Classification

The classifier processes the provided description or, when configured for real multimodal inference, the image.

### 2. Deterministic Rules Engine

The rules engine applies additional checks to the classification result.

These checks include:

- Identifying hazardous waste.
- Handling uncertain classifications.
- Detecting contaminated packaging.
- Applying material-specific disposal guidance.
- Providing preparation instructions and safety warnings.

This separation helps prevent a classification result from automatically determining disposal instructions without additional safety checks.

## 🔍 Mock Mode vs. Amazon Bedrock

**Important:** The local mock engine and real AI inference are different.

### Mock Mode

- Runs locally without AWS credentials.
- Uses predefined classification logic.
- Supports testing common waste descriptions.
- Applies the deterministic disposal rules.
- Does not analyze raw image pixels using a computer vision model.

When an image is supplied without a description in mock mode, the application should report that the item could not be verified from the image.

### Amazon Bedrock

The backend includes integration with Amazon Bedrock for AI inference.

Using real multimodal inference requires appropriate AWS credentials, IAM permissions, model availability, and correct application configuration.

**Live Amazon Bedrock inference and cloud deployment must be configured and tested separately.** Their presence in the code does not mean they are already running.

## ⚠️ Current Limitations

- Mock mode cannot visually identify objects from image pixels.
- Real AI inference requires appropriate AWS configuration.
- Waste collection rules differ between municipalities.
- Classification results may be uncertain or incorrect.
- The current application focuses on individual waste items rather than comprehensive mixed-waste analysis.

## 🚀 Future Improvements

Potential future enhancements include:

- Location-aware municipal waste guidelines.
- Improved image-based classification.
- Barcode and recycling-symbol recognition.
- Support for multiple waste items in one image.
- A dashboard for tracking waste segregation.
- Integration with local recycling and hazardous-waste collection services.

## 🌱 Environmental Impact

EcoSort AI aims to encourage better waste segregation by making disposal guidance easier to understand.

By highlighting contamination risks, identifying potentially hazardous items, and explaining preparation steps, the project encourages more informed waste-management decisions.

## ⚠️ Safety Disclaimer

EcoSort AI provides educational disposal guidance. Waste collection rules and recycling acceptance criteria vary by location.

Always consult your local waste-management authority when uncertain about disposal requirements.

Never place potentially hazardous batteries, chemicals, or other dangerous materials into ordinary waste streams without checking the applicable safety guidance.

## 👨‍💻 Project Information

**Project:** EcoSort AI — AI Waste Segregation Advisor

**Event:** Environmental Hacks 2026 Hackathon

**Repository:** https://github.com/Mufeed06-cmd/EcoSort

---
