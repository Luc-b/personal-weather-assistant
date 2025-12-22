# Personal Weather Assistant 🌦️

A smart weather assistant that provides personalized outfit and activity recommendations based on real-time weather forecasts, powered by AI.

---

## Overview

Personal Weather Assistant combines real-time weather data from OpenWeatherMap with AI-powered analysis to deliver personalized recommendations. Simply enter a city and date, and get tailored advice on what to wear, activities to do, and important weather warnings.

---

## Features

- Real-time weather forecasts for any city
- AI-powered outfit and activity recommendations
- 5-day weather forecast support
- Personalized tips and warnings
- Fast and responsive interface
- Error handling for invalid inputs

---

## Tech Stack

### Backend
- **Python** - Core language
- **FastAPI** - Web framework
- **OpenWeather API** - Weather data provider
- **Groq API** - LLM for AI recommendations

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **HTTP API** - Backend communication

---

## Project Structure
```
personal-weather-assistant/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
└── weather-frontend/
    ├── src/
    ├── package.json
    └── vite.config.js
```

---

## Prerequisites

- Python 3.10 or newer
- Node.js 18+ and npm
- OpenWeather API key ([Get one here](https://openweathermap.org/api))
- Groq API key ([Get one here](https://console.groq.com))

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd personal-weather-assistant
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend/` directory:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENWEATHER_API_KEY=your_openweathermap_key_here
GROQ_API_KEY=your_groq_key_here
```

### 4. Frontend Setup
```bash
cd ../weather-frontend
npm install
```

---

## Running the Application

### Start the Backend
```bash
cd backend
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uvicorn main:app --reload
```

Backend will be available at:
- API: http://127.0.0.1:8000
- API Documentation: http://127.0.0.1:8000/docs

### Start the Frontend

Open a new terminal:
```bash
cd weather-frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## Usage

1. Open http://localhost:5173 in your browser
2. Enter a city name (e.g., "Zagreb", "London", "New York")
3. Select a date (within the next 5 days)
4. Click "Get Recommendations"
5. View personalized weather insights and recommendations

---

## Example API Response
```json
{
  "summary": "Cold and cloudy with occasional rain.",
  "outfit": {
    "top": ["thermal shirt", "sweater"],
    "bottom": ["jeans"],
    "shoes": ["waterproof boots"],
    "outerwear": ["winter jacket"],
    "accessories": ["scarf", "gloves"]
  },
  "activities": {
    "outdoor": ["short walk in the park"],
    "indoor": ["museum visit", "coffee shop"]
  },
  "warnings": [
    "Slippery roads possible",
    "Temperature drops in the evening"
  ],
  "tips": [
    "Carry an umbrella",
    "Layer your clothing"
  ]
}
```

---

## Testing

### Manual Testing

1. **Start the backend:**
```bash
   cd backend
   uvicorn main:app --reload
```

2. **Start the frontend:**
```bash
   cd weather-frontend
   npm run dev
```

3. **Test the application:**
   - Open http://localhost:5173
   - Enter a city (e.g., "Zagreb")
   - Select a date within the next 5 days
   - Verify weather data and AI recommendations display correctly

### API Testing

Use the interactive API documentation at http://127.0.0.1:8000/docs to test endpoints directly.

---

## Known Limitations

- OpenWeatherMap free tier provides 5-day forecasts only
- Date must be within the next 5 days
- AI recommendations are in English
- Requires active internet connection

---

## Troubleshooting

### Backend won't start
- Check if Python virtual environment is activated
- Verify API keys are correctly set in `.env`
- Ensure port 8000 is not already in use

### Frontend won't connect
- Verify backend is running on http://127.0.0.1:8000
- Check browser console for CORS errors
- Ensure port 5173 is available

### API errors
- Verify API keys are valid and active
- Check OpenWeatherMap API quota limits
- Review backend logs for detailed error messages

---

## Contact

For questions or feedback, please open an issue on GitHub.

---
## Example

<img width="1431" height="871" alt="image" src="https://github.com/user-attachments/assets/57c1f157-673d-4f9d-8edb-3ca0a88f8d5a" />


**Built with ❤️ using FastAPI, React, and AI**
