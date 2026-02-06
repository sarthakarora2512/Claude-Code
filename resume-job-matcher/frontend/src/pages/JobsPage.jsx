import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft, ExternalLink, MapPin, Building2, Globe, Filter,
  Briefcase, Zap, Search, RefreshCw,
} from 'lucide-react'
import { searchJobsForResume } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ScoreBadge from '../components/ScoreBadge'

export default function JobsPage() {
  const { resumeId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all') // 'all', 'easy_apply', 'greenhouse'
  const [sourceFilter, setSourceFilter] = useState('all')

  useEffect(() => {
    fetchJobs()
  }, [resumeId])

  const fetchJobs = () => {
    setLoading(true)
    setError(null)
    searchJobsForResume(resumeId)
      .then(setData)
      .catch(() => setError('Failed to fetch job postings. The job sites may be rate-limiting requests.'))
      .finally(() => setLoading(false))
  }

  if (loading) return <LoadingSpinner message="Crawling job postings from LinkedIn, Glassdoor, and Indeed..." />
  if (error) {
    return (
      <div className="text-center py-16">
        <p className="text-red-600 mb-4">{error}</p>
        <div className="flex gap-3 justify-center">
          <button onClick={fetchJobs} className="btn-primary flex items-center gap-2">
            <RefreshCw size={16} />
            Retry
          </button>
          <button onClick={() => navigate('/')} className="btn-secondary">Upload Again</button>
        </div>
      </div>
    )
  }

  const allJobs = [...(data.easy_apply_jobs || []), ...(data.other_jobs || [])]

  const filteredJobs = allJobs.filter((job) => {
    if (filter === 'easy_apply' && !job.is_easy_apply) return false
    if (filter === 'greenhouse' && job.platform !== 'greenhouse') return false
    if (sourceFilter !== 'all' && job.source.toLowerCase() !== sourceFilter) return false
    return true
  })

  const sources = [...new Set(allJobs.map((j) => j.source))]

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link
            to={`/results/${resumeId}`}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-2"
          >
            <ArrowLeft size={14} />
            Back to Results
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Job Postings</h1>
          <p className="text-gray-500 mt-1">
            Found {allJobs.length} jobs ({data.easy_apply_count || 0} with easy apply)
          </p>
        </div>
        <button onClick={fetchJobs} className="btn-secondary flex items-center gap-2">
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Filter size={16} className="text-gray-400" />
          <span className="text-sm font-medium text-gray-700">Filters</span>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filter === 'all' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All Jobs ({allJobs.length})
          </button>
          <button
            onClick={() => setFilter('easy_apply')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1 ${
              filter === 'easy_apply' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <Zap size={14} />
            Easy Apply ({data.easy_apply_count || 0})
          </button>
          <button
            onClick={() => setFilter('greenhouse')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filter === 'greenhouse' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Greenhouse
          </button>

          <div className="border-l border-gray-200 mx-2" />

          <button
            onClick={() => setSourceFilter('all')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              sourceFilter === 'all' ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All Sources
          </button>
          {sources.map((source) => (
            <button
              key={source}
              onClick={() => setSourceFilter(source.toLowerCase())}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                sourceFilter === source.toLowerCase()
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {source}
            </button>
          ))}
        </div>
      </div>

      {/* Job Listings */}
      {filteredJobs.length === 0 ? (
        <div className="card text-center py-12">
          <Search className="text-gray-300 mx-auto mb-3" size={48} />
          <p className="text-gray-500 mb-2">No jobs found matching your filters.</p>
          <p className="text-sm text-gray-400">
            Try adjusting filters or refreshing results. Job sites may limit scraping requests.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredJobs.map((job, idx) => (
            <div key={idx} className="card hover:border-primary-300 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <h3 className="font-semibold text-gray-900 truncate">{job.title}</h3>
                    {job.is_easy_apply && (
                      <span className="badge-green flex items-center gap-1">
                        <Zap size={10} />
                        Easy Apply
                      </span>
                    )}
                    {job.platform && (
                      <span className="badge-purple text-xs">{job.platform}</span>
                    )}
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-2">
                    <span className="flex items-center gap-1">
                      <Building2 size={14} />
                      {job.company}
                    </span>
                    {job.location && (
                      <span className="flex items-center gap-1">
                        <MapPin size={14} />
                        {job.location}
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      <Globe size={14} />
                      {job.source}
                    </span>
                  </div>

                  {job.description_snippet && (
                    <p className="text-sm text-gray-600 line-clamp-2">{job.description_snippet}</p>
                  )}
                </div>

                <div className="flex items-center gap-3 ml-4 shrink-0">
                  {job.match_score > 0 && <ScoreBadge score={job.match_score} />}
                  <a
                    href={job.url || job.apply_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary text-sm py-2 px-4 flex items-center gap-1.5"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Apply
                    <ExternalLink size={14} />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
