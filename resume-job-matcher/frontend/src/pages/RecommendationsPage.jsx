import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Sparkles, Download, ArrowLeft, Check, AlertTriangle, Briefcase } from 'lucide-react'
import { getRecommendations, applyRecommendations } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

export default function RecommendationsPage() {
  const { resumeId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [applying, setApplying] = useState(false)
  const [appliedResult, setAppliedResult] = useState(null)
  const [error, setError] = useState(null)
  const [selectedRecs, setSelectedRecs] = useState(new Set())

  useEffect(() => {
    getRecommendations(resumeId)
      .then((result) => {
        setData(result)
        // Select all by default
        setSelectedRecs(new Set(result.recommendations.map((_, i) => i)))
      })
      .catch(() => setError('Failed to load recommendations'))
      .finally(() => setLoading(false))
  }, [resumeId])

  const toggleRec = (index) => {
    setSelectedRecs((prev) => {
      const next = new Set(prev)
      if (next.has(index)) next.delete(index)
      else next.add(index)
      return next
    })
  }

  const handleApply = async () => {
    if (selectedRecs.size === 0) return
    setApplying(true)
    try {
      const selected = data.recommendations.filter((_, i) => selectedRecs.has(i))
      const result = await applyRecommendations(resumeId, selected)
      setAppliedResult(result)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to apply recommendations')
    } finally {
      setApplying(false)
    }
  }

  if (loading) return <LoadingSpinner message="Generating recommendations..." />
  if (error) {
    return (
      <div className="text-center py-16">
        <p className="text-red-600 mb-4">{error}</p>
        <button onClick={() => navigate('/')} className="btn-primary">Upload Again</button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link
            to={`/results/${resumeId}`}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-2"
          >
            <ArrowLeft size={14} />
            Back to Results
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Resume Recommendations</h1>
          <p className="text-gray-500 mt-1">
            Targeted for: <span className="font-medium text-primary-600">{data.target_role}</span>
          </p>
        </div>
        <div className="flex gap-3">
          <Link to={`/jobs/${resumeId}`} className="btn-secondary flex items-center gap-2">
            <Briefcase size={16} />
            Find Jobs
          </Link>
        </div>
      </div>

      {/* Applied success banner */}
      {appliedResult && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Check className="text-emerald-600" size={20} />
            <div>
              <p className="font-medium text-emerald-800">{appliedResult.message}</p>
              <p className="text-sm text-emerald-600 mt-0.5">Your optimized resume is ready for download.</p>
            </div>
          </div>
          <a
            href={appliedResult.modified_pdf_url}
            download
            className="btn-success flex items-center gap-2"
          >
            <Download size={16} />
            Download PDF
          </a>
        </div>
      )}

      {/* Recommendations list */}
      <div className="space-y-4">
        {data.recommendations.map((rec, idx) => (
          <div
            key={idx}
            className={`card cursor-pointer transition-all ${
              selectedRecs.has(idx)
                ? 'ring-2 ring-primary-500 border-primary-200'
                : 'opacity-75'
            }`}
            onClick={() => toggleRec(idx)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <div
                  className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                    selectedRecs.has(idx)
                      ? 'bg-primary-600 border-primary-600'
                      : 'border-gray-300'
                  }`}
                >
                  {selectedRecs.has(idx) && <Check size={12} className="text-white" />}
                </div>
                <span className="badge-blue">{rec.section}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
              <div>
                <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">Current</p>
                <div className="bg-red-50 border border-red-100 rounded-lg p-3">
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{rec.original_text}</p>
                </div>
              </div>
              <div>
                <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">Recommended</p>
                <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-3">
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{rec.recommended_text}</p>
                </div>
              </div>
            </div>

            <div className="flex items-start gap-2 bg-amber-50 rounded-lg px-3 py-2">
              <AlertTriangle size={14} className="text-amber-500 mt-0.5 shrink-0" />
              <p className="text-xs text-amber-700">{rec.reason}</p>
            </div>
          </div>
        ))}
      </div>

      {data.recommendations.length === 0 && (
        <div className="card text-center py-12">
          <Sparkles className="text-gray-300 mx-auto mb-3" size={48} />
          <p className="text-gray-500">Your resume looks great! No recommendations at this time.</p>
        </div>
      )}

      {/* Apply button */}
      {data.recommendations.length > 0 && !appliedResult && (
        <div className="sticky bottom-4 mt-6">
          <button
            onClick={handleApply}
            disabled={applying || selectedRecs.size === 0}
            className="btn-primary w-full py-3 text-base flex items-center justify-center gap-2 shadow-lg"
          >
            {applying ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                Applying changes...
              </>
            ) : (
              <>
                <Sparkles size={18} />
                Apply {selectedRecs.size} Recommendation{selectedRecs.size !== 1 ? 's' : ''} to PDF
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}
