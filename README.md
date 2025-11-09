# BrandAI - AI-Powered Advertisement Critique Engine

**Version:** 1.0.0  
**Last Updated:** November 2024

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Development Journey: From Start to End](#development-journey-from-start-to-end)
4. [Critique Model Engine: Deep Dive](#critique-model-engine-deep-dive)
5. [Installation & Setup](#installation--setup)
6. [Running the Application](#running-the-application)
7. [Evaluation & Testing](#evaluation--testing)
8. [Project Structure](#project-structure)
9. [API Documentation](#api-documentation)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

BrandAI is an enterprise-grade AI system that generates, critiques, and refines advertisements using advanced multi-modal AI models. The system leverages Google's Vertex AI (Imagen 2, Veo 3.1), Gemini Vision API, CLIP models, and OpenCV to create a comprehensive pipeline that ensures generated ads meet high standards for brand alignment, visual quality, message clarity, and safety.

### Key Features

- **Multi-Modal Generation**: Generate both image and video advertisements using state-of-the-art AI models
- **Comprehensive Critique Engine**: Evaluate ads across 4 critical dimensions (Brand Alignment, Visual Quality, Message Clarity, Safety & Ethics)
- **Intelligent Refinement**: Automatically refine ads based on critique feedback using prompt optimization and image enhancement
- **Brand Kit Integration**: Extract and utilize brand colors, logos, and product images for consistent brand representation
- **Parallel Processing**: Efficient evaluation of multiple ad variations simultaneously
- **LangGraph Orchestration**: Sophisticated workflow management with retry logic and conditional routing

### Technology Stack

- **Backend Framework**: FastAPI (Python 3.12)
- **AI Models**: 
  - Gemini 2.5 Pro (Vision Analysis)
  - Vertex AI Imagen 2 (Image Generation)
  - Vertex AI Veo 3.1 (Video Generation)
  - CLIP (Logo/Product Matching)
- **Image Processing**: OpenCV, Pillow
- **Workflow Orchestration**: LangGraph
- **Containerization**: Docker & Docker Compose

---

## System Architecture

### High-Level Architecture

The BrandAI system follows a microservices-inspired architecture with a clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   API    │  │Orchestrator│ │  Agents  │  │ Services │   │
│  │  Routes  │→ │ (LangGraph)│→ │  Layer   │→ │  Layer   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Vertex AI   │  │ Gemini API    │  │  CLIP Model  │
│  (Generation)│  │  (Vision)     │  │  (Matching)  │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Workflow Pipeline

The complete workflow follows this sequence:

1. **Brand Kit Extraction** → Extract brand colors, logos, and product information
2. **Ad Generation** → Generate advertisement variations using Vertex AI
3. **Critique Evaluation** → Comprehensive multi-dimensional evaluation
4. **Refinement Decision** → Determine if refinement is needed
5. **Refinement Execution** → Improve ads through prompt refinement or image enhancement
6. **Final Output** → Return approved ads with detailed critique reports

---

## Development Journey: From Start to End

### Phase 1: Foundation Setup (Week 1)

We began by establishing the project structure and core infrastructure:

- **Project Structure**: Created a modular architecture with separate directories for agents, services, models, and utilities
- **FastAPI Setup**: Configured the main application with CORS, error handling, and health checks
- **Configuration Management**: Implemented environment-based configuration using Pydantic settings
- **Data Models**: Defined Pydantic models for requests, responses, and run status tracking

**Key Decisions:**
- Chose FastAPI for its async capabilities and automatic API documentation
- Used Pydantic for type-safe data validation
- Implemented in-memory run tracking (no database for MVP)

### Phase 2: Core Services (Week 1)

Built the foundational services that support the entire system:

- **Storage Service**: File upload/download, directory management, and asset storage
- **Run Manager**: UUID-based run ID generation and status tracking
- **Logger Service**: Structured logging with file and console output

**Implementation Details:**
- Storage service handles both brand assets and generated ads
- Run manager tracks workflow progress through stages
- Logger provides detailed debugging information

### Phase 3: Brand Kit Agent (Week 2)

Developed the brand extraction capabilities:

- **Logo Extractor**: OpenCV-based logo detection and feature extraction
- **Color Extractor**: Dominant color extraction using K-means clustering
- **External Scraper**: Optional website scraping for brand information

**Challenges & Solutions:**
- Logo detection required handling various image formats and sizes
- Color extraction needed to identify brand-specific color palettes
- External scraping added complexity but provided richer brand context

### Phase 4: Generation Agent (Week 2-3)

Implemented the ad generation pipeline:

- **Vertex AI Integration**: Connected to Imagen 2 and Veo 3.1 APIs
- **Prompt Engineering**: Context-aware prompt generation with brand kit integration
- **Variation Generator**: Generate multiple ad variations with different prompts
- **Image-to-Video Support**: Veo 3.1 I2V capability for logo/product integration

**Key Features:**
- Support for both text-to-image and text-to-video generation
- Image-to-video conversion for incorporating brand assets
- Brand kit data (colors, logo, product) integrated into prompts
- Sequential generation with proper error handling

### Phase 5: Critique Agent - The Heart of the System (Week 3-4)

This was the most critical and complex phase. We built a comprehensive evaluation engine:

#### 5.1 Multi-Modal Analysis Layer

- **Vision Analyzer**: Gemini 2.5 Pro for comprehensive image/video analysis
- **CLIP Analyzer**: Logo and product similarity matching
- **Image Processor**: OpenCV-based blur detection, color extraction, quality checks

#### 5.2 Four-Dimensional Evaluation System

**Brand Alignment Evaluator:**
- Logo presence and matching (CLIP similarity scoring)
- Color consistency (hex color comparison with brand palette)
- Tone evaluation (Gemini Vision analysis)

**Visual Quality Evaluator:**
- Blur detection (Laplacian variance algorithm)
- Artifact detection (contrast and quality checks)
- Composition analysis (resolution and aspect ratio evaluation)

**Message Clarity Evaluator:**
- Product visibility (CLIP matching or Vision analysis)
- Text clarity (readability assessment via Gemini)
- Message understanding (comprehensive semantic analysis)

**Safety & Ethics Evaluator:**
- Harmful content detection (comprehensive safety analysis)
- Stereotype detection (bias and discrimination checks)
- Misleading claims detection (truthfulness verification)

#### 5.3 Scoring & Ranking System

- **Per-Dimension Scoring**: Each evaluator returns a 0.0-1.0 score
- **Overall Score Calculation**: Weighted average of all dimensions
- **Pass/Fail Determination**: Configurable thresholds (default: 0.6 overall, 0.4 per dimension)
- **Variation Ranking**: Sort variations by overall score for best selection

**Implementation Highlights:**
- Parallel processing of all 4 evaluators for each variation
- Context-aware prompts that include brand kit and user intent
- Comprehensive feedback generation with specific issues and suggestions
- JSON-structured analysis results for programmatic access

### Phase 6: Refinement Agent (Week 4)

Built the refinement capabilities:

- **Prompt Refiner**: Analyze critique feedback and generate improved prompts
- **Image Enhancer**: OpenCV-based sharpening and denoising for simple issues
- **Decision Logic**: Determine whether to regenerate, enhance, approve, or reject

**Refinement Strategies:**
- **Approve**: Score ≥ 0.8, no critical issues
- **Regenerate**: Score 0.6-0.8, prompt refinement needed
- **Enhance**: Score 0.6-0.8, simple image fixes possible
- **Reject**: Score < 0.6 or safety violations

### Phase 7: LangGraph Orchestration (Week 5)

Implemented the workflow orchestration:

- **State Management**: TypedDict-based workflow state
- **Node Functions**: Brand Kit, Generation, Critique, Refinement nodes
- **Conditional Routing**: Decision logic for workflow continuation
- **Retry Mechanism**: Up to 3 retries for failed generations

**Workflow Graph:**
```
Brand Kit → Generation → Critique → Refinement
                                    ↓
                            ┌───────┴───────┐
                            │               │
                        Regenerate      Approve/Reject
                            │               │
                            └───────┬───────┘
                                  END
```

### Phase 8: API Endpoints (Week 5)

Created RESTful API endpoints:

- **POST /api/v1/generate**: Start ad generation (non-blocking)
- **GET /api/v1/status/{run_id}**: Check workflow progress
- **GET /api/v1/result/{run_id}**: Get final results
- **GET /api/v1/media/{path}**: Serve generated media files
- **GET /health**: Health check endpoint

**Key Features:**
- Background task execution for long-running workflows
- Real-time status updates via run manager
- File serving with security checks (path traversal prevention)

### Phase 9: Docker Setup (Week 6)

Containerized the application:

- **Dockerfile**: Multi-stage build with Python 3.12
- **Docker Compose**: Service configuration with volumes
- **Volume Mounts**: Storage, logs, and GCP credentials
- **Health Checks**: Automated container health monitoring

---

## Critique Model Engine: Deep Dive

The Critique Engine is the most sophisticated component of BrandAI. It provides comprehensive, multi-dimensional evaluation of generated advertisements.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Critique Agent                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │         Batch Input Handler                         │   │
│  │  (Processes 3-4 ad variations simultaneously)        │   │
│  └────────────────────────────────────────────────────┘   │
│                        │                                    │
│                        ▼                                    │
│  ┌────────────────────────────────────────────────────┐   │
│  │         Pre-Analysis Layer                          │   │
│  │  • Logo Detection (CLIP)                            │   │
│  │  • Product Detection (CLIP)                          │   │
│  │  • Blur Detection (OpenCV)                          │   │
│  │  • Basic Safety Flags                               │   │
│  └────────────────────────────────────────────────────┘   │
│                        │                                    │
│                        ▼                                    │
│  ┌────────────────────────────────────────────────────┐   │
│  │      Multi-Modal Analysis Layer                     │   │
│  │  • Gemini Vision API (Comprehensive Analysis)       │   │
│  │  • CLIP Model (Similarity Matching)                │   │
│  │  • OpenCV (Image Processing)                        │   │
│  └────────────────────────────────────────────────────┘   │
│                        │                                    │
│                        ▼                                    │
│  ┌────────────────────────────────────────────────────┐   │
│  │      Parallel Evaluator Execution                   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│   │
│  │  │  Brand   │ │ Quality  │ │ Clarity  │ │ Safety ││   │
│  │  │Evaluator│ │Evaluator │ │Evaluator │ │Evaluator││   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘│   │
│  └────────────────────────────────────────────────────┘   │
│                        │                                    │
│                        ▼                                    │
│  ┌────────────────────────────────────────────────────┐   │
│  │         Scoring & Ranking Layer                    │   │
│  │  • Per-Dimension Scoring                           │   │
│  │  • Overall Score Calculation                       │   │
│  │  • Variation Comparison                             │   │
│  │  • Ranking & Best Selection                        │   │
│  └────────────────────────────────────────────────────┘   │
│                        │                                    │
│                        ▼                                    │
│  ┌────────────────────────────────────────────────────┐   │
│  │         Output Formatter                           │   │
│  │  • Critique Report Generation                      │   │
│  │  • JSON Structure Creation                          │   │
│  │  • Feedback & Suggestions Compilation               │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Detailed Component Breakdown

#### 1. Vision Analyzer (Gemini 2.5 Pro)

**Purpose**: Comprehensive visual and semantic analysis of advertisements

**Capabilities:**
- Full video understanding (temporal analysis)
- Image analysis with context awareness
- Structured JSON response parsing
- Context-aware prompts with brand kit integration

**Implementation Details:**
```python
# Key Features:
- Base64 encoding for image/video data
- MIME type detection
- Context-aware prompt generation
- Fallback to alternative models if primary fails
- Error handling with graceful degradation
```

**Prompt Engineering:**
The Vision Analyzer uses sophisticated prompts that include:
- Brand context (name, colors, logo)
- User intent (original generation prompt)
- Media-specific instructions (video vs image)
- Structured output requirements (JSON format)

#### 2. CLIP Analyzer

**Purpose**: Accurate logo and product matching using semantic similarity

**How It Works:**
1. Load pre-trained CLIP model (ViT-B/32)
2. Encode both reference (logo/product) and generated ad
3. Calculate cosine similarity between embeddings
4. Determine if logo/product is present and recognizable

**Scoring Logic:**
- Similarity > 0.7: Strong match (score boost)
- Similarity 0.3-0.7: Moderate match
- Similarity < 0.3: Weak or no match (penalty)

**Advantages:**
- More accurate than pixel-based comparison
- Handles variations in logo/product appearance
- Works with different lighting and angles

#### 3. Image Processor (OpenCV)

**Purpose**: Low-level image quality analysis

**Capabilities:**
- **Blur Detection**: Laplacian variance algorithm
  - Sharp images: variance > 100
  - Blurry images: variance < 100
- **Color Extraction**: K-means clustering for dominant colors
- **Quality Checks**: Resolution, aspect ratio, contrast analysis

**Blur Detection Algorithm:**
```python
# Laplacian Variance Method
1. Convert image to grayscale
2. Apply Laplacian operator
3. Calculate variance of Laplacian
4. Threshold: < 100 = blurry, > 100 = sharp
```

#### 4. Brand Alignment Evaluator

**Evaluation Dimensions:**

**Logo Evaluation:**
- CLIP similarity matching with brand logo
- Detection confidence scoring
- Visibility and prominence assessment

**Color Consistency:**
- Extract dominant colors from ad
- Compare with brand color palette
- Hex color matching with tolerance (30 RGB units)
- Score based on number of brand colors found

**Tone Evaluation:**
- Gemini Vision analysis for brand tone matching
- Keyword-based heuristic analysis
- Professional, consistent, aligned indicators

**Scoring Formula:**
```
brand_alignment_score = (logo_score + color_score + tone_score) / 3
```

#### 5. Visual Quality Evaluator

**Evaluation Dimensions:**

**Blur Detection:**
- Laplacian variance calculation
- Normalized score: blur_score / threshold
- Feedback: Sharp, Minor blur, Moderate blur, Significant blur

**Artifact Detection:**
- Contrast analysis (low contrast = potential artifacts)
- Visual artifact identification
- Compression artifact detection

**Composition Analysis:**
- Resolution check (minimum 512px)
- Aspect ratio validation (0.5-2.0 range)
- Professional composition assessment

**Scoring Formula:**
```
visual_quality_score = (blur_score + artifact_score + composition_score) / 3
```

#### 6. Message Clarity Evaluator

**Evaluation Dimensions:**

**Product Visibility:**
- CLIP matching with product reference (if available)
- Gemini Vision analysis (if no reference)
- Prominence and recognizability assessment

**Text Clarity:**
- Text presence detection
- Readability assessment
- Font size and contrast evaluation

**Message Understanding:**
- Semantic analysis of ad message
- Clarity indicators (clear, understandable, obvious)
- Confusion detection (unclear, confusing, ambiguous)

**Scoring Formula:**
```
message_clarity_score = (product_score + text_score + message_score) / 3
```

#### 7. Safety & Ethics Evaluator

**Evaluation Dimensions:**

**Harmful Content Detection:**
- Violence and dangerous content
- Explicit or inappropriate imagery
- Hate speech and discrimination
- Comprehensive safety analysis via Gemini

**Stereotype Detection:**
- Gender bias and stereotypes
- Racial/ethnic bias
- Cultural stereotypes
- Inappropriate representation

**Misleading Claims:**
- False product claims
- Deceptive representations
- Exaggerated promises
- Truthfulness verification

**Scoring Logic:**
- High-confidence issues: score = 0.0
- Medium-confidence issues: score = 0.2
- Low-confidence issues: score = 0.4
- No issues: score = 1.0

**Safety Thresholds:**
- Any harmful content or high-confidence stereotype: automatic rejection
- Safety violations override other scores

### Parallel Processing

The Critique Engine processes all evaluators in parallel for efficiency:

```python
# ThreadPoolExecutor with 4 workers
with ThreadPoolExecutor(max_workers=4) as executor:
    brand_future = executor.submit(brand_evaluator.evaluate, ...)
    quality_future = executor.submit(quality_evaluator.evaluate, ...)
    clarity_future = executor.submit(clarity_evaluator.evaluate, ...)
    safety_future = executor.submit(safety_evaluator.evaluate, ...)
    
    # Wait for all to complete
    brand_result = brand_future.result()
    quality_result = quality_future.result()
    clarity_result = clarity_future.result()
    safety_result = safety_future.result()
```

### Scoring System

#### Overall Score Calculation

```python
overall_score = weighted_average(
    brand_alignment_score * weight_brand,
    visual_quality_score * weight_quality,
    message_clarity_score * weight_clarity,
    safety_ethics_score * weight_safety
)

# Default: Equal weights (0.25 each)
```

#### Pass/Fail Determination

```python
def determine_pass_fail(overall_score, dimension_scores):
    # Check overall threshold
    if overall_score < 0.6:
        return False
    
    # Check all dimensions meet minimum
    for dim_score in dimension_scores.values():
        if dim_score < 0.4:
            return False
    
    return True
```

#### Variation Ranking

Variations are ranked by:
1. Overall score (primary)
2. Safety score (tie-breaker)
3. Brand alignment (secondary tie-breaker)

### Critique Report Structure

```json
{
  "run_id": "uuid",
  "total_variations": 3,
  "passed_variations": 2,
  "failed_variations": 1,
  "best_variation": {
    "variation_id": "var_1",
    "file_path": "ads/run_id/var_1.png",
    "overall_score": 0.85,
    "scorecard": [
      {
        "dimension": "brand_alignment",
        "score": 0.90,
        "feedback": "Logo detected (similarity: 0.85) | Good color consistency (2/3 brand colors found) | Tone appears aligned with brand",
        "issues": [],
        "suggestions": []
      },
      {
        "dimension": "visual_quality",
        "score": 0.80,
        "feedback": "Image is sharp (blur score: 120.5) | No significant artifacts detected | Good composition (aspect ratio: 1.33)",
        "issues": [],
        "suggestions": []
      },
      {
        "dimension": "message_clarity",
        "score": 0.85,
        "feedback": "Product clearly visible (similarity: 0.82) | Text is clear and readable | Message is clear and understandable",
        "issues": [],
        "suggestions": []
      },
      {
        "dimension": "safety_ethics",
        "score": 1.0,
        "feedback": "No harmful content detected | No stereotypes detected | No misleading claims detected",
        "issues": [],
        "suggestions": []
      }
    ],
    "passed": true
  },
  "all_variations": [...],
  "generated_at": "2024-11-09T07:21:39Z"
}
```

### Performance Optimizations

1. **Parallel Evaluation**: All 4 evaluators run simultaneously
2. **Caching**: CLIP model loaded once, reused for all variations
3. **Batch Processing**: Process multiple variations in sequence
4. **Lazy Loading**: Vision analyzer initialized only when needed
5. **Error Handling**: Graceful degradation if one evaluator fails

---

## Installation & Setup

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Google Cloud Platform account with:
  - Vertex AI API enabled
  - Gemini API access
  - Service account with appropriate permissions
- GCP Service Account JSON key file

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd BrandAI-fork
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# GCP Configuration
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/app/config/gcp/service-account.json

# Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Application Settings
APP_ENV=production
LOG_LEVEL=INFO
```

### Step 3: Configure GCP Credentials

Place your GCP service account JSON file at:
```
config/gcp/service-account.json
```

### Step 4: Install Dependencies (Local Development)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 5: Build Docker Image (Recommended)

```bash
docker-compose build
```

---

## Running the Application

### Option 1: Docker Compose (Recommended)

```bash
# Start the backend service
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop the service
docker-compose down
```

The API will be available at `http://localhost:8000`

### Option 2: Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Set environment variables
export GCP_PROJECT_ID=your-project-id
export GEMINI_API_KEY=your-api-key
export GOOGLE_APPLICATION_CREDENTIALS=./config/gcp/service-account.json

# Run the server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using the Startup Script

```bash
# Make script executable
chmod +x scripts/run_backend.sh

# Run the script
./scripts/run_backend.sh
```

### Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

---

## Evaluation & Testing

### Manual Testing via API

#### 1. Generate an Advertisement

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -F "prompt=A sleek, modern advertisement for a premium running shoe with dynamic motion and vibrant colors" \
  -F "media_type=image" \
  -F "logo=@/path/to/logo.jpg" \
  -F "product=@/path/to/product.jpg"
```

**Response:**
```json
{
  "run_id": "60c0a4a8-bae5-47cb-b5d1-0d6203c93c3d",
  "status": "pending",
  "message": "Ad generation started. Use the run_id to check status.",
  "estimated_time": 120
}
```

#### 2. Check Status

```bash
curl "http://localhost:8000/api/v1/status/60c0a4a8-bae5-47cb-b5d1-0d6203c93c3d"
```

**Response:**
```json
{
  "run_id": "60c0a4a8-bae5-47cb-b5d1-0d6203c93c3d",
  "status": "processing",
  "progress": 75.0,
  "current_stage": "critique",
  "created_at": "2024-11-09T07:20:00Z",
  "updated_at": "2024-11-09T07:21:30Z"
}
```

#### 3. Get Final Results

```bash
curl "http://localhost:8000/api/v1/result/60c0a4a8-bae5-47cb-b5d1-0d6203c93c3d"
```

**Response:**
```json
{
  "run_id": "60c0a4a8-bae5-47cb-b5d1-0d6203c93c3d",
  "status": "completed",
  "success": true,
  "critique_report": {
    "total_variations": 1,
    "passed_variations": 1,
    "best_variation": {
      "variation_id": "var_1",
      "overall_score": 0.85,
      "scorecard": [...]
    }
  },
  "variations": [
    {
      "variation_id": "var_1",
      "file_path": "ads/60c0a4a8-bae5-47cb-b5d1-0d6203c93c3d/var_1.png",
      "media_type": "image",
      "overall_score": 0.85
    }
  ]
}
```

#### 4. View Generated Media

```bash
# Access via browser or curl
http://localhost:8000/api/v1/media/ads/60c0a4a8-bae5-47cb-b5d1-0d6203c93c3d/var_1.png
```

### Automated Testing Scripts

The project includes several test scripts in the `scripts/` directory:

```bash
# Test individual components
python scripts/test_phase2_services.py
python scripts/test_phase3_brand_kit.py
python scripts/test_phase4_generation.py
python scripts/test_phase5_critique.py
python scripts/test_phase6_refinement.py
python scripts/test_phase7_orchestrator.py
python scripts/test_phase8_api.py

# Test complete workflow
python scripts/test_server.py
```

### Evaluating Critique Engine Performance

#### 1. Test with Known Good Ads

Create test cases with ads that should score high:
- Clear logo presence
- Brand colors prominent
- Sharp, high-quality images
- Clear product visibility

#### 2. Test with Known Issues

Test cases that should be flagged:
- Blurry images
- Missing logos
- Off-brand colors
- Safety violations

#### 3. Analyze Critique Reports

Review the JSON critique reports in:
```
data/storage/reports/{run_id}/critique_report_*.json
```

**Key Metrics to Evaluate:**
- **Accuracy**: Do scores match human evaluation?
- **Consistency**: Similar ads get similar scores?
- **Completeness**: All dimensions properly evaluated?
- **Feedback Quality**: Are suggestions actionable?

#### 4. Performance Benchmarks

Measure evaluation time:
- Single image evaluation: ~5-10 seconds
- Single video evaluation: ~15-30 seconds
- Parallel evaluation of 3 variations: ~10-15 seconds

### Critique Engine Evaluation Checklist

- [ ] **Brand Alignment**: Logo detection accuracy > 80%
- [ ] **Visual Quality**: Blur detection accuracy > 90%
- [ ] **Message Clarity**: Product visibility detection > 75%
- [ ] **Safety**: Harmful content detection (no false positives)
- [ ] **Scoring Consistency**: Similar ads within 0.1 score variance
- [ ] **Feedback Quality**: Actionable suggestions provided
- [ ] **Performance**: Evaluation completes within 30 seconds

---

## Project Structure

```
BrandAI-fork/
├── backend/
│   ├── app/
│   │   ├── agents/              # All agent implementations
│   │   │   ├── brand_kit_agent/
│   │   │   ├── generation_agent/
│   │   │   ├── critique_agent/  # Critique engine
│   │   │   │   ├── evaluators/  # 4 dimension evaluators
│   │   │   │   ├── analyzers/   # Vision, CLIP, Image processing
│   │   │   │   └── scoring/     # Scoring and ranking
│   │   │   └── refinement_agent/
│   │   ├── api/                 # FastAPI routes
│   │   ├── core/                # Orchestrator and run manager
│   │   ├── models/              # Pydantic models
│   │   ├── services/            # Storage, logging
│   │   └── utils/               # Utility functions
│   ├── Dockerfile
│   └── requirements.txt
├── config/
│   └── gcp/                     # GCP credentials
├── data/
│   ├── storage/                 # Generated ads and reports
│   └── rag/                     # RAG database (if used)
├── scripts/                     # Test scripts
├── docs/                        # Documentation
├── docker-compose.yml
└── README.md
```

---

## API Documentation

### POST /api/v1/generate

Generate an advertisement.

**Request:**
- `prompt` (string, required): Description of the ad
- `media_type` (string, required): "image" or "video"
- `brand_website_url` (string, optional): Brand website URL
- `logo` (file, optional): Logo image file
- `product` (file, optional): Product image file

**Response:**
```json
{
  "run_id": "uuid",
  "status": "pending",
  "message": "Ad generation started...",
  "estimated_time": 120
}
```

### GET /api/v1/status/{run_id}

Get workflow status.

**Response:**
```json
{
  "run_id": "uuid",
  "status": "processing",
  "progress": 75.0,
  "current_stage": "critique",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### GET /api/v1/result/{run_id}

Get final results.

**Response:**
```json
{
  "run_id": "uuid",
  "status": "completed",
  "success": true,
  "critique_report": {...},
  "variations": [...]
}
```

### GET /api/v1/media/{path}

Serve generated media files.

**Example:**
```
GET /api/v1/media/ads/{run_id}/var_1.png
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-09T07:20:00Z"
}
```

---

## Troubleshooting

### Common Issues

#### 1. GCP Authentication Errors

**Problem**: `google.auth.exceptions.DefaultCredentialsError`

**Solution**:
- Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Ensure service account JSON file exists
- Check service account has required permissions

#### 2. Gemini API Errors

**Problem**: `API key not valid`

**Solution**:
- Verify `GEMINI_API_KEY` in `.env` file
- Check API key is active in Google AI Studio
- Ensure billing is enabled

#### 3. CLIP Model Loading Issues

**Problem**: `torch` import errors

**Solution**:
- Ensure PyTorch is installed: `pip install torch torchvision`
- Check CUDA compatibility if using GPU
- Verify model download completed

#### 4. Docker Volume Mount Errors

**Problem**: Permission denied errors

**Solution**:
```bash
# Fix permissions
sudo chown -R $USER:$USER data/
sudo chmod -R 755 data/
```

#### 5. Critique Evaluation Timeout

**Problem**: Evaluation takes too long

**Solution**:
- Check Gemini API rate limits
- Verify network connectivity
- Consider reducing number of variations

### Debug Mode

Enable detailed logging:

```bash
# In .env file
LOG_LEVEL=DEBUG
APP_ENV=development
```

View logs:
```bash
# Docker
docker-compose logs -f backend

# Local
tail -f logs/brandai.log
```

---

## Conclusion

BrandAI represents a comprehensive solution for AI-powered advertisement generation and critique. The Critique Engine, with its multi-dimensional evaluation system, ensures that generated ads meet high standards for brand alignment, quality, clarity, and safety.

The system's modular architecture, parallel processing capabilities, and intelligent refinement mechanisms make it suitable for enterprise-scale deployment while maintaining flexibility for customization and extension.

For questions, issues, or contributions, please refer to the project documentation or contact the development team.

---

**Built with ❤️ using FastAPI, LangGraph, Gemini, and Vertex AI**

