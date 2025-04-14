import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar/Navbar';
import Footer from './components/Footer/Footer';
import PredictionPage from './pages/PredictionPage/PredictionPage';
import PresentationPage from './pages/PresentationPage/PresentationPage';
import RealtimePage from './pages/RealtimePage/RealtimePage';
import './App.css'

function App() {
    return (
        <div className='App'> 
            <Navbar />
            <div className="Content">
                <Routes>
                    <Route path="/" element={<PresentationPage />} />
                    <Route path="/prediction" element={<PredictionPage />} />
                    <Route path="/realtime" element={<RealtimePage />} />
                </Routes>
            </div>
            <Footer />
        </div>
    );
}

export default App;