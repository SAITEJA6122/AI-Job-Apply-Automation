import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface StatisticsChartsProps {
  stats: any;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const StatisticsCharts = ({ stats }: StatisticsChartsProps) => {
  // Prepare data for role-based bar chart
  const roleData = Object.entries(stats.by_role || {}).map(([role, data]: [string, any]) => ({
    role: role.length > 20 ? role.substring(0, 20) + '...' : role,
    applied: data.applied || 0,
    skipped: data.skipped || 0,
    qualified: data.qualified || 0,
  }));

  // Prepare data for skip reasons pie chart
  const skipReasonData = Object.entries(stats.by_skip_reason || {})
    .filter(([_, count]) => count > 0)
    .sort(([, a], [, b]) => (b as number) - (a as number))
    .slice(0, 6)
    .map(([reason, count]) => ({
      name: reason.length > 30 ? reason.substring(0, 30) + '...' : reason,
      value: count,
    }));

  // Prepare data for error categories pie chart
  const errorData = Object.entries(stats.by_error_category || {})
    .filter(([_, count]) => count > 0)
    .map(([error, count]) => ({
      name: error,
      value: count,
    }));

  return (
    <div className="space-y-6">
      {/* Applications by Role - Bar Chart */}
      {roleData.length > 0 && (
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Applications by Role</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={roleData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="role" 
                tick={{ fill: '#6B7280', fontSize: 12 }}
                stroke="#6B7280"
              />
              <YAxis tick={{ fill: '#6B7280', fontSize: 12 }} stroke="#6B7280" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F3F4F6'
                }}
              />
              <Legend />
              <Bar dataKey="applied" fill="#10B981" name="Applied" />
              <Bar dataKey="skipped" fill="#F59E0B" name="Skipped" />
              <Bar dataKey="qualified" fill="#3B82F6" name="Qualified" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Skip Reasons - Pie Chart */}
      {skipReasonData.length > 0 && (
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Skip Reasons</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={skipReasonData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {skipReasonData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F3F4F6'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Error Categories - Pie Chart */}
      {errorData.length > 0 && (
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Error Categories</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={errorData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {errorData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px',
                  color: '#F3F4F6'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default StatisticsCharts;
