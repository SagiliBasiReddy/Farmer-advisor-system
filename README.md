# Agricultural Advisory System - Farmers Call Center

A full-stack web application providing AI-powered agricultural guidance in multiple Indian languages (Hindi, Bengali, Marathi, etc.). Built with Python Flask backend and React TypeScript frontend.

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
  - `scikit-learn` - TF-IDF vectorization
  - `rank-bm25` - BM25 ranking
  - `sentence-transformers` - Semantic embeddings
  - `requests` - HTTP client
  - `flask-cors` - Cross-origin support

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
git clone https://github.com/yourusername/agricultural-advisory.git
cd agricultural-advisory
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
├── app.py                          # Flask main application
├── requirements.txt                # Python dependencies
├── farmers_call_query_data.csv     # Agricultural database (65k+ records)
├── test_multilingual_queries.csv   # Test queries in multiple languages
│
├── Backend Modules:
├── translator_fixed.py             # Multi-language translator
├── summarizer.py                   # Query summarizer (extracts crop)
├── canonicalizer.py                # Query canonicalization
├── retriever.py                    # Semantic search & ranking
├── crop_preference.py              # Crop-specific filtering
│
├── agri-advisor/                   # React Frontend
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Page components
│   │   └── main.tsx                # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
│
├── .env                            # Environment variables
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

1. **User Query** → Farmer enters question in any Indian language
2. **Translation** → LLM translates to English
3. **Summarization** → Extracts crop name (if mentioned)
4. **Canonicalization** → Converts to standard query format
5. **Retrieval** → Semantic search in 65k+ agricultural records
6. **Filtering** → Crop-specific preference matching
7. **Response** → Returns best matching advisory with confidence score

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

**farmers_call_query_data.csv** contains:
- 65,000+ agricultural Q&A pairs
- Topics: Cultivation, pest management, disease control, fertilizers, irrigation
- Crops: Vegetables, cereals, pulses, spices, fruits, etc.
- Languages: Primarily in English with regional language references

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

- **Sagil** - Initial development

## 🙏 Acknowledgments

- Krishi Vigyan Kendra (KVK), Darrang for agricultural data
- Farmers' call center data from Indian agricultural extension services
- Open source community for excellent libraries

## 📞 Contact & Support

For issues, questions, or suggestions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/agricultural-advisory/issues)
- Email: your.email@example.com

## 🔗 Links

- [Live Demo](https://agricultural-advisory.example.com)
- [Documentation](https://docs.example.com)
- [API Docs](https://api.example.com/docs)

---

Made with ❤️ for Indian Farmers
