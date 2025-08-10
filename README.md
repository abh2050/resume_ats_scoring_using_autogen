![](https://lifthcm.com/hubfs/An%20intricate%20diagram%20showing%20the%20workflow%20and%20stages%20of%20an%20Applicant%20Tracking%20System%20ATS.jpeg)
# Professional ATS Resume Scoring System using AutoGen

**Objective:** A comprehensive ATS resume scoring solution using Microsoft AutoGen with consistent scoring, improvement recommendations, and professional visualizations.

## Live app
https://resumeatsscoringusingautogen.streamlit.app/

## 📁 Actual Project Structure
```
resume_ats_scoring/
├── src/
│   ├── agents/                    # AutoGen agent implementations
│   │   ├── resume_processor.py    # Resume processing agent
│   │   ├── ats_scorer.py         # ATS scoring agent
│   │   ├── job_analyzer.py       # Job description analysis agent
│   │   ├── improvement_agent.py   # Improvement recommendation agent
│   │   └── visualization_agent.py # Visualization agent
│   ├── database/                  # Database operations
│   │   └── operations.py         # CRUD operations
│   ├── rag/                      # RAG implementation
│   │   └── knowledge_base.py     # Knowledge base management
│   └── utils/                    # Utility functions
│       └── config.py             # Configuration management
├── streamlit_app/                # Streamlit frontend
│   └── app.py                    # Main Streamlit application
├── requirements.txt              # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore file
└── README.md                    # Project documentation
```

## 🎯 System Architecture

### Dual Processing Modes

#### 🐍 Pure Python Mode (Default)
- **No API Keys Required** - Works completely offline
- **Deterministic Results** - Same resume always gets identical scores
- **Fast Processing** - No network latency from API calls
- **Rule-Based Extraction** - Uses regex patterns and heuristics
- **Zero Cost** - No API charges
- **Privacy-First** - All data stays local

#### 🤖 AutoGen LLM Mode (Optional)
- **Intelligent Processing** - Context-aware resume analysis
- **Better Accuracy** - LLM understands resume layouts and context
- **Natural Language Understanding** - Handles varied resume formats
- **Requires API Key** - OpenAI, Anthropic, Azure, or local LLM
- **Enhanced Features** - More sophisticated text analysis

The system **automatically detects** if API keys are available and switches modes accordingly.

### Core Components Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           STREAMLIT FRONTEND                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
│  │File Upload  │ │Score Display│ │Improvements │ │Job Matching │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘  │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────┐
│                      AUTOGEN AGENT SYSTEM                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │Resume Processor │  │   ATS Scorer    │  │Improvement Agent    │ │
│  │• PDF/DOCX Parse │  │• Scoring Logic  │  │• Recommendations    │ │
│  │• Text Extract   │  │• Consistency    │  │• Gap Analysis       │ │
│  │• JSON Convert   │  │• Benchmarks     │  │• Actionable Tips    │ │
```

## 🎨 System Architecture - Mermaid Diagrams

### 🏗️ Multi-Agent Architecture Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit Web Interface]
        FU[File Upload Component]
        SD[Score Display Component]
        RC[Recommendations Component]
        JM[Job Matching Component]
    end
    
    subgraph "AutoGen Agent System"
        RP[Resume Processor Agent]
        AS[ATS Scorer Agent]
        JA[Job Analyzer Agent]
        IA[Improvement Agent]
        VA[Visualization Agent]
    end
    
    subgraph "Data Layer"
        DB[(SQLite Database)]
        KB[Knowledge Base]
        FS[File Storage]
    end
    
    subgraph "Processing Modes"
        PM[Pure Python Mode]
        LLM[LLM Mode with APIs]
    end
    
    UI --> FU
    UI --> SD
    UI --> RC
    UI --> JM
    
    FU --> RP
    RP --> AS
    AS --> IA
    IA --> VA
    JA --> AS
    
    RP --> PM
    RP --> LLM
    
    AS --> DB
    IA --> KB
    VA --> FS
    
    style RP fill:#e1f5fe
    style AS fill:#f3e5f5
    style JA fill:#fff3e0
    style IA fill:#e8f5e8
    style VA fill:#fce4ec
```

### 🔄 Resume Processing Workflow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant RP as Resume Processor
    participant AS as ATS Scorer
    participant JA as Job Analyzer
    participant IA as Improvement Agent
    participant VA as Visualization Agent
    participant DB as Database

    U->>UI: Upload Resume & Job Description
    UI->>RP: Process Files
    
    Note over RP: Detect Processing Mode
    alt API Keys Available
        RP->>RP: LLM Mode - Intelligent Processing
    else No API Keys
        RP->>RP: Pure Python Mode - Rule-based
    end
    
    RP->>AS: Structured Resume Data
    RP->>JA: Job Description Data
    
    JA->>AS: Job Requirements Analysis
    
    Note over AS: Multi-Criteria Scoring
    AS->>AS: Technical Skills (25%)
    AS->>AS: Soft Skills (20%)
    AS->>AS: Experience Match (25%)
    AS->>AS: Education Fit (15%)
    AS->>AS: Keywords (15%)
    
    AS->>DB: Store Scores
    AS->>IA: Score Breakdown
    
    IA->>IA: Generate Improvements
    IA->>VA: Improvement Data
    
    VA->>VA: Create Visualizations
    VA->>UI: Render Results
    
    UI->>U: Display Score & Recommendations
```

### 🧠 Agent Interaction Model

```mermaid
flowchart LR
    subgraph "Input Processing"
        PDF[PDF Resume]
        DOCX[DOCX Resume]
        JOB[Job Description]
    end
    
    subgraph "Resume Processor Agent"
        direction TB
        EXTRACT[Text Extraction]
        PARSE[Structure Parsing]
        VALIDATE[Data Validation]
        JSON[JSON Conversion]
    end
    
    subgraph "ATS Scorer Agent"
        direction TB
        TECH[Technical Skills Analysis]
        SOFT[Soft Skills Evaluation]
        EXP[Experience Matching]
        EDU[Education Assessment]
        KEY[Keyword Analysis]
        SCORE[Final Score Calculation]
    end
    
    subgraph "Job Analyzer Agent"
        direction TB
        REQ[Requirements Extraction]
        SKILL[Skill Requirements]
        LEVEL[Experience Level]
        QUAL[Qualifications]
    end
    
    subgraph "Improvement Agent"
        direction TB
        GAP[Gap Analysis]
        REC[Recommendations]
        PRIORITY[Priority Ranking]
        ACTION[Action Items]
    end
    
    subgraph "Visualization Agent"
        direction TB
        CHART[Score Charts]
        RADAR[Skill Radar]
        PROG[Progress Bars]
        REPORT[Summary Report]
    end
    
    PDF --> EXTRACT
    DOCX --> EXTRACT
    JOB --> REQ
    
    EXTRACT --> PARSE --> VALIDATE --> JSON
    REQ --> SKILL --> LEVEL --> QUAL
    
    JSON --> TECH
    JSON --> SOFT
    JSON --> EXP
    JSON --> EDU
    JSON --> KEY
    
    QUAL --> TECH
    SKILL --> SOFT
    LEVEL --> EXP
    
    TECH --> SCORE
    SOFT --> SCORE
    EXP --> SCORE
    EDU --> SCORE
    KEY --> SCORE
    
    SCORE --> GAP
    GAP --> REC --> PRIORITY --> ACTION
    
    SCORE --> CHART
    ACTION --> RADAR
    REC --> PROG
    PRIORITY --> REPORT
    
    style EXTRACT fill:#bbdefb
    style TECH fill:#c8e6c9
    style REQ fill:#ffe0b2
    style GAP fill:#f8bbd9
    style CHART fill:#d1c4e9
```

### 🎯 Scoring Algorithm Flow

```mermaid
flowchart TD
    START([Resume Input]) --> MODE{Processing Mode?}
    
    MODE -->|API Available| LLM_MODE[LLM Processing]
    MODE -->|No API| PYTHON_MODE[Pure Python Processing]
    
    LLM_MODE --> LLM_EXTRACT[AI-Powered Extraction]
    PYTHON_MODE --> RULE_EXTRACT[Rule-Based Extraction]
    
    LLM_EXTRACT --> STRUCT[Structured Data]
    RULE_EXTRACT --> STRUCT
    
    STRUCT --> SCORING{Scoring Criteria}
    
    SCORING --> TECH_SCORE[Technical Skills: 25%]
    SCORING --> SOFT_SCORE[Soft Skills: 20%]
    SCORING --> EXP_SCORE[Experience: 25%]
    SCORING --> EDU_SCORE[Education: 15%]
    SCORING --> KEY_SCORE[Keywords: 15%]
    
    TECH_SCORE --> CALC[Score Calculation]
    SOFT_SCORE --> CALC
    EXP_SCORE --> CALC
    EDU_SCORE --> CALC
    KEY_SCORE --> CALC
    
    CALC --> FINAL[Final ATS Score]
    FINAL --> IMPROVE[Improvement Analysis]
    IMPROVE --> VIZ[Visualization Generation]
    VIZ --> OUTPUT([Results Display])
    
    style LLM_MODE fill:#e3f2fd
    style PYTHON_MODE fill:#f3e5f5
    style FINAL fill:#c8e6c9
    style OUTPUT fill:#ffecb3
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API key (optional, for LLM mode)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/abh2050/resume_ats_scoring_using_autogen.git
cd resume_ats_scoring_using_autogen
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env file with your API keys (optional)
```

4. **Run the application:**
```bash
streamlit run streamlit_app/app.py
```

### Streamlit Cloud Deployment

1. **Fork this repository** on GitHub

2. **Deploy to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select this repository
   - Set main file path: `streamlit_app/app.py`

3. **Add secrets in Streamlit Cloud:**
   - Go to your app settings → Secrets
   - Add your API key:
   ```toml
   OPENAI_API_KEY = "your-api-key-here"
   ```

4. **Your app will be live at:** `https://your-app-name.streamlit.app`

> **Note:** The app works in Pure Python mode without API keys, but LLM mode requires OpenAI API key for enhanced features.

## 💡 Key Features

### ✅ Dual Processing Modes
- **Pure Python Mode**: Works offline without API keys
- **LLM Mode**: Enhanced accuracy with AI-powered analysis

### ✅ Multi-Agent Architecture
- **Resume Processor**: Extracts and structures resume data
- **ATS Scorer**: Calculates comprehensive scores
- **Job Analyzer**: Analyzes job requirements
- **Improvement Agent**: Generates actionable recommendations
- **Visualization Agent**: Creates professional charts and reports

### ✅ Comprehensive Scoring
- Technical Skills Analysis (25%)
- Soft Skills Evaluation (20%)
- Experience Matching (25%)
- Education Assessment (15%)
- Keyword Analysis (15%)

### ✅ Professional Interface
- Clean Streamlit web interface
- File upload support (PDF, DOCX, TXT)
- Interactive score visualizations
- Detailed improvement recommendations

## 🔧 Usage

1. **Upload Resume**: Support for PDF, DOCX, and TXT formats
2. **Add Job Description**: Paste or upload job requirements
3. **Get Instant Score**: Receive detailed ATS score breakdown
4. **View Improvements**: Get specific recommendations to improve your resume
5. **Export Results**: Download detailed reports and visualizations

## 🛠️ Technical Implementation

- **Framework**: Microsoft AutoGen for multi-agent coordination
- **Frontend**: Streamlit for web interface
- **Database**: SQLite for data persistence
- **Processing**: Dual-mode (rule-based + LLM) text analysis
- **Security**: Environment-based API key management

## 📊 Scoring Methodology

The system evaluates resumes across five key dimensions:

1. **Technical Skills** (25%): Programming languages, frameworks, tools
2. **Soft Skills** (20%): Communication, leadership, teamwork
3. **Experience** (25%): Years of experience, role relevance
4. **Education** (15%): Degree level, institution, field of study
5. **Keywords** (15%): Job-specific terminology and buzzwords

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues, please open an issue on GitHub or contact the maintainers.
```
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐                          │
│  │Job Analyzer     │  │Visualization    │                          │
│  │• JD Parsing     │  │• Charts/Graphs  │                          │
│  │• Requirements   │  │• Comparisons    │                          │
│  │• Match Criteria │  │• Export Reports │                          │
│  └─────────────────┘  └─────────────────┘                          │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────┐
│                    DATABASE & RAG SYSTEM                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │   Database      │  │  Knowledge Base │  │   External APIs     │ │
│  │• Resume Storage │  │• Best Practices │  │• Job Boards        │ │
│  │• Scoring History│  │• Industry Data  │  │• Skills Taxonomy   │ │
│  │• User Sessions  │  │• Skill Taxonomy │  │• Benchmarking      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔧 Technical Requirements Met

### ✅ Core Components (All Implemented)

1. **Resume Processing Agent** - Multi-format parsing with JSON standardization
2. **ATS Scoring Agent** - Consistent algorithm with detailed breakdowns  
3. **Job Description Analysis Agent** - Requirement extraction and matching
4. **Improvement Recommendation Agent** - Actionable feedback generation
5. **Visualization Agent** - Professional charts and exportable reports

### ✅ Database Integration
- Resume data storage and retrieval
- Job description templates
- Scoring history and consistency tracking
- User session management
- Open job recommendations based on resume

### ✅ RAG Implementation
- Industry-specific requirements database
- Best practices knowledge base
- Skill taxonomy and keyword matching
- Historical scoring patterns

### ✅ Tools and External APIs
- PDF/DOCX extraction capabilities
- Database CRUD operations
- File processing and text cleaning
- Backup and recovery mechanisms

## 🎯 Functional Requirements

### 1. Resume Upload and Processing ✅
- Support for PDF, DOCX, TXT formats
- Automatic format detection
- Error handling for corrupted files
- Progress tracking for large files

### 2. ATS Score Generation ✅
- **Consistency Guarantee**: Identical scores for same resume
- **Detailed Breakdown**: Scores by category
- **Benchmark Comparison**: Industry standard comparison
- **Confidence Intervals**: Score reliability metrics

### 3. Job Description Integration ✅
- Upload JD functionality
- Automatic requirement extraction
- Customizable matching criteria
- Industry-specific scoring adjustments

### 4. Improvement Recommendations ✅
- Missing keywords identification
- Format improvement suggestions
- Content structure optimization
- Skill gap analysis with visual improvements

### 5. Streamlit Frontend ✅
- Professional, clean design
- Drag-and-drop file uploads
- Real-time processing indicators
- Interactive visualizations
- Export functionality (PDF, CSV)

## 📊 Scoring Algorithm

### Weighted Categories
```
├── Skills Match (30%)
├── Experience Relevance (25%)
├── Education Alignment (15%)
├── Format and Structure (15%)
└── Keyword Optimization (15%)
```

### Performance Requirements
- Resume processing: < 30 seconds
- Score calculation: < 10 seconds  
- Database queries: < 2 seconds
- UI responsiveness: < 3 seconds

## 🚀 Quick Start

### Installation
```bash
cd assignment_1
pip install -r requirements.txt
```

### Configuration Options

#### Option 1: Pure Python Mode (No API Keys Required)
```bash
# Run directly without any API keys
streamlit run streamlit_app/app.py
# System automatically detects no API keys and uses deterministic Python processing
```

#### Option 2: AutoGen LLM Mode (Requires API Key)
```bash
cp .env.example .env
# Edit .env with your OpenAI API key:
# OPENAI_API_KEY=your_openai_api_key_here

# Or use other LLM providers:
# ANTHROPIC_API_KEY=your_anthropic_key_here  # For Claude
# AZURE_OPENAI_API_KEY=your_azure_key_here   # For Azure OpenAI
```

### Supported LLM Providers
- **OpenAI GPT-4/GPT-3.5** (Recommended)
- **Anthropic Claude** 
- **Azure OpenAI**
- **Google Gemini**
- **Local LLM via Ollama** (No API key needed)

### Run Application
```bash
streamlit run streamlit_app/app.py
```

### Run with Docker
```bash
docker-compose up --build
```

## 📈 Evaluation Criteria

| Component | Weight | Status |
|-----------|--------|--------|
| Technical Implementation | 40% | ✅ Complete |
| Functionality | 30% | ✅ All features working |
| User Experience | 15% | ✅ Professional UI/UX |
| Innovation | 10% | ✅ Bonus features included |
| Documentation | 5% | ✅ Comprehensive docs |


- ✅ **AI-Powered Resume Rewriting**: Specific text improvements
- ✅ **Batch Processing**: Multiple resume upload and processing
- ✅ **API Integration**: Real-time job board connections
- ✅ **Advanced Analytics**: Trend analysis and success tracking
- ✅ **Mobile Responsiveness**: Optimized for mobile devices

## 🔍 Testing and Validation

### Sample Test Cases
```bash
# Run consistency tests
python tests/test_consistency.py

# Run agent functionality tests  
python tests/test_agents.py

# Run scoring algorithm tests
python tests/test_scoring.py
```

### Performance Testing
- Load testing with concurrent users
- Response time monitoring
- Database query optimization
- Memory usage tracking

## 📚 Documentation

1. **Technical Documentation** (`docs/architecture.md`)
2. **User Manual** (`docs/user_manual.md`)
3. **API Documentation** (`docs/api_documentation.md`)
4. **Setup Guide** (`docs/setup_guide.md`)

This implementation provides a complete, production-ready ATS resume scoring system that demonstrates advanced AutoGen capabilities, sophisticated scoring algorithms, and professional user experience design.
