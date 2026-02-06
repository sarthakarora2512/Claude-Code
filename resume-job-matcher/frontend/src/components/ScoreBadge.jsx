export default function ScoreBadge({ score, size = 'md' }) {
  const percentage = Math.round(score * 100)
  let colorClass = 'badge-red'
  if (percentage >= 70) colorClass = 'badge-green'
  else if (percentage >= 50) colorClass = 'badge-blue'
  else if (percentage >= 30) colorClass = 'badge-yellow'

  const sizeClass = size === 'lg' ? 'text-sm px-3 py-1' : ''

  return (
    <span className={`${colorClass} ${sizeClass}`}>
      {percentage}% match
    </span>
  )
}
