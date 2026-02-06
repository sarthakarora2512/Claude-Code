import { useState, useEffect } from 'react'
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom'
import { Sparkles, Briefcase, ChevronRight, Award, Code, GraduationCap, Clock } from 'lucide-react'
import { getResume } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ScoreBadge from '../components/ScoreBadge'

export default function ResultsPage() {
  const { resumeId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const [data, setData] = useState(location.state || null)
  const [loading, setLoading] = useState(!location.state)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!data) {
      getResume(resumeId)
        .then(setData)
        .catch(() => setError('Failed to load resume data'))
        .finally(() => setLoading(false))
    }
  }, [resumeId, data])

  if (loading) return <LoadingSpinner message="Loading results..." />
  if (error) {
    return (
      <div className="text-center py-16">
        <p className="text-red-600 mb-4">{error}</p>
        <button onClick={() => navigate('/')} className="btn-primary">Upload Again</button>
      </div>
    )
  }

  const { resume_data, role_matches } = data

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Resume Analysis</h1>
          <p className="text-gray-500 mt-1">{resume_data.filename}</p>
        </div>
        <div className="flex gap-3">
          <Link to={`/recommendations/${resumeId}`} className="btn-primary flex items-center gap-2">
            <Sparkles size={16} />
            Get Recommendations
          </Link>
          <Link to={`/jobs/${resumeId}`} className="btn-success flex items-center gap-2">
            <Briefcase size={16} />
            Find Jobs
          </Link>
        </div>
      </div>

      {/* Summary Card */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Summary</h2>
        <p className="text-gray-700">{resume_data.summary}</p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
              <Code size={14} />
              Skills Found
            </div>
            <span className="text-xl font-bold text-gray-900">{resume_data.skills.length}</span>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
              <Clock size={14} />
              Experience
            </div>
            <span className="text-xl font-bold text-gray-900">
              {resume_data.experience_years > 0 ? `${resume_data.experience_years} yrs` : 'N/A'}
            </span>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
              <GraduationCap size={14} />
              Education
            </div>
            <span className="text-xl font-bold text-gray-900">{resume_data.education.length}</span>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
              <Award size={14} />
              Role Matches
            </div>
            <span className="text-xl font-bold text-gray-900">{role_matches.length}</span>
          </div>
        </div>
      </div>

      {/* Skills */}
      <div className="card mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Skills Detected</h2>
        <div className="flex flex-wrap gap-2">
          {resume_data.skills.map((skill) => (
            <span key={skill} className="badge-blue">{skill}</span>
          ))}
          {resume_data.skills.length === 0 && (
            <p className="text-gray-500 text-sm">No specific skills detected. Upload a more detailed resume.</p>
          )}
        </div>
      </div>

      {/* Job Titles Found */}
      {resume_data.job_titles.length > 0 && (
        <div className="card mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Roles Identified in Resume</h2>
          <div className="flex flex-wrap gap-2">
            {resume_data.job_titles.map((title) => (
              <span key={title} className="badge-purple">{title}</span>
            ))}
          </div>
        </div>
      )}

      {/* Role Matches */}
      <div className="card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Matching Roles</h2>
        <div className="space-y-4">
          {role_matches.map((role, idx) => (
            <div
              key={idx}
              className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-gray-900">{role.role_title}</h3>
                  <p className="text-sm text-gray-500 mt-0.5">{role.description}</p>
                </div>
                <ScoreBadge score={role.match_score} size="lg" />
              </div>

              {role.matching_skills.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs text-gray-500 mb-1">Matching Skills</p>
                  <div className="flex flex-wrap gap-1">
                    {role.matching_skills.map((s) => (
                      <span key={s} className="badge-green text-xs">{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {role.missing_skills.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs text-gray-500 mb-1">Skills to Develop</p>
                  <div className="flex flex-wrap gap-1">
                    {role.missing_skills.map((s) => (
                      <span key={s} className="badge-red text-xs">{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Score bar */}
              <div className="mt-3">
                <div className="w-full bg-gray-100 rounded-full h-1.5">
                  <div
                    className="bg-primary-500 h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${Math.round(role.match_score * 100)}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
