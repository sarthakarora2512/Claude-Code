import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import UploadPage from './pages/UploadPage'
import ResultsPage from './pages/ResultsPage'
import RecommendationsPage from './pages/RecommendationsPage'
import JobsPage from './pages/JobsPage'

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/results/:resumeId" element={<ResultsPage />} />
            <Route path="/recommendations/:resumeId" element={<RecommendationsPage />} />
            <Route path="/jobs/:resumeId" element={<JobsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}
