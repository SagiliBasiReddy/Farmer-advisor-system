# SRM Agro Advisor

An AI-powered agricultural advisory system providing intelligent farming guidance in multiple Indian languages. Built with Python Flask backend and React TypeScript frontend for farmers across India.

## 🌾 Features

- **Multilingual Support**: Hindi, Bengali, Marathi, Assamese, and more
- **Intelligent Query Processing**: 
  - Translation to English
  - Query canonicalization
  - Semantic search from agricultural database
  - Crop-specific recommendations
- **Real-time Advisory**: Instant agricultural recommendations for farmers
- **Responsive UI**: Modern React frontend with Tailwind CSS
- **Production Ready**: CORS-enabled, optimized retrieval system

## 📋 Tech Stack

### Backend
- **Framework**: Flask
- **Python Libraries**:
  - `pandas` - Data processing
  - `numpy` - Numerical computations
  - `scikit-learn` - TF-IDF vectorization
  - `rank-bm25` - BM25 ranking algorithm
  - `sentence-transformers` - Semantic embeddings
  - `deep-translator` - Multi-language translation
  - `requests` - HTTP client
  - `flask-cors` - Cross-origin support
  - `python-dotenv` - Environment variable management

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **UI Components**: shadcn/ui

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/SagiliBasiReddy/Agro-Advisor.git
cd Agro-Advisor
```

### 2. Setup Backend

```bash
# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Frontend

```bash
cd agri-advisor
npm install
```

### 4. Run Development Servers

**Terminal 1 - Backend:**
```bash
python app.py
# Runs on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd agri-advisor
npm run dev
# Runs on http://localhost:8080
```

Visit `http://localhost:8080` in your browser

## 📁 Project Structure

```
.
├── app.py                                  # Flask main application
├── requirements.txt                        # Python dependencies
├── farmers_call_query_data_cleaned.csv    # Agricultural database (cleaned & deduplicated)
│
├── Backend Modules:
├── translator_fixed.py                    # Multi-language translator
├── soltrans.py                            # Solution translator (local language conversion)
├── canonicalizer.py                       # Query canonicalization
├── retriever.py                           # Semantic search & ranking (TF-IDF + BM25)
├── crop_preference.py                     # Crop-specific filtering
├── llm_validator.py                       # Answer validation
│
├── agri-advisor/                          # React Frontend
│   ├── src/
│   │   ├── components/                    # React components
│   │   │   ├── Header.tsx                 # SRM Agro Advisor branding
│   │   │   ├── QueryInput.tsx             # Multilingual voice/text input
│   │   │   ├── ResultsCard.tsx            # Results display
│   │   │   └── ...
│   │   ├── pages/                         # Page components
│   │   ├── types/                         # TypeScript types
│   │   └── main.tsx                       # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
│
├── .env                                   # Environment variables
├── .gitignore
└── README.md
```

## 🔄 API Endpoints

### POST `/ask`
Submit a farmer query and receive agricultural advisory

**Request:**
```json
{
  "query": "मेरी गोभी के पौधे पीले पड़ जा रहे हैं"
}
```

**Response:**
```json
{
  "translated": "My cabbage plants are turning yellow",
  "canonical": "yellowing of cabbage leaves causes solutions",
  "advice": "Apply NPK 19-19-19 @ 2-3 gm/l of water, spray 2 times at 15 days interval",
  "confidence": 0.85,
  "disclaimer": "This is advisory information based on agricultural data."
}
```

## 📊 How It Works

1. **User Query** → Farmer enters question via voice or text in any language
2. **Language Detection** → Detects Telugu, Tamil, Hindi, English, or mixed Romanized formats
3. **Translation** → Translates non-English queries to English
4. **Canonicalization** → Converts to standard query format
5. **Retrieval** → Hybrid semantic search (TF-IDF + BM25) in 65k+ agricultural records
6. **Filtering** → Crop-specific preference matching
7. **Solution Translation** → Translates response back to user's language
8. **Response** → Returns best matching advisory with confidence score

## 🔑 Environment Variables

Create `.env` file:
```
# Backend
FLASK_ENV=development
FLASK_DEBUG=True

# Frontend (.env in agri-advisor/)
VITE_API_URL=http://localhost:5000
```

## 📝 Database

**farmers_call_query_data_cleaned.csv** contains:
- 65,000+ agricultural Q&A pairs (deduplicated & cleaned)
- Multiple standardized question formats for each crop issue
- Topics: Cultivation, pest management, disease control, fertilizers, irrigation
- Crops: Vegetables, cereals, pulses, spices, fruits, etc.
- Quality: Cleaned dataset with standardized questions and comprehensive answers

## 🧪 Testing

Test with multilingual queries:

```bash
# English
"How to control leaf spot in cabbage?"

# Hindi
"गोभी में पत्ती धब्बे का नियंत्रण कैसे करें?"

# Bengali
"বাঁধাকপিতে পাতার দাগ রোগ নিয়ন্ত্রণ"
```

## 📦 Deployment

### Production Build

```bash
# Build frontend
cd agri-advisor
npm run build

# Frontend will be served from Flask at http://localhost:5000
cd ..
python app.py
```

### Using Docker (Optional)

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 🛠️ Development

### Adding New Features

1. **New Crop Support**: Add to `crop_preference.py`
2. **New Language**: Update `translator_fixed.py`
3. **UI Changes**: Modify React components in `agri-advisor/src/`
4. **Backend Logic**: Extend pipeline modules

### Running Tests

```bash
python -m pytest tests/
```

## 📚 Documentation

- [Backend Architecture](docs/backend.md)
- [Frontend Components](docs/frontend.md)
- [API Reference](docs/api.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📋 TODO

- [ ] Add more regional languages (Punjabi, Tamil, Telugu, Kannada)
- [ ] Implement user feedback system
- [ ] Add weather integration
- [ ] Create mobile app
- [ ] Add farmer registration & history
- [ ] Integration with government schemes

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Authors

- **SagiliBasiReddy** - Initial development

## 📞 Contact & Support

For issues, questions, or suggestions:
- GitHub Issues: [Create an issue](https://github.com/SagiliBasiReddy/Agro-Advisor/issues)

## 🔗 Links

- GitHub Repository: [SagiliBasiReddy/Agro-Advisor](https://github.com/SagiliBasiReddy/Agro-Advisor)
