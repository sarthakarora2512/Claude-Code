import { Link, useLocation } from 'react-router-dom'
import { FileText, Briefcase, Sparkles, Upload } from 'lucide-react'

export default function Navbar() {
  const location = useLocation()

  const isActive = (path) => location.pathname.startsWith(path)

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="bg-primary-600 text-white p-2 rounded-lg">
              <FileText size={20} />
            </div>
            <span className="text-xl font-bold text-gray-900">ResumeMatch</span>
          </Link>
          <div className="flex items-center gap-1">
            <Link
              to="/"
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                location.pathname === '/'
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Upload size={16} />
              Upload
            </Link>
            {isActive('/results') && (
              <span className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium bg-primary-50 text-primary-700">
                <Sparkles size={16} />
                Results
              </span>
            )}
            {isActive('/recommendations') && (
              <span className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium bg-primary-50 text-primary-700">
                <Sparkles size={16} />
                Recommendations
              </span>
            )}
            {isActive('/jobs') && (
              <span className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium bg-primary-50 text-primary-700">
                <Briefcase size={16} />
                Jobs
              </span>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
