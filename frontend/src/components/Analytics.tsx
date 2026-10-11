import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

interface AnalyticsProps {
  stats: any;
}

export const ApplicationTrendChart = ({ stats }: AnalyticsProps) => {
  // Generate sample data for demonstration
  const data = [
    { name: 'Mon', applications: 4, success: 3 },
    { name: 'Tue', applications: 3, success: 2 },
    { name: 'Wed', applications: 5, success: 4 },
    { name: 'Thu', applications: 2, success: 2 },
    { name: 'Fri', applications: 4, success: 3 },
    { name: 'Sat', applications: 1, success: 1 },
    { name: 'Sun', applications: 0, success: 0 },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="applications" stroke="#8884d8" name="Total Applications" />
        <Line type="monotone" dataKey="success" stroke="#82ca9d" name="Successful" />
      </LineChart>
    </ResponsiveContainer>
  );
};

export const SuccessRateByRole = ({ stats }: AnalyticsProps) => {
  const data = [
    { role: 'Full Stack', rate: 85 },
    { role: 'React Dev', rate: 78 },
    { role: 'Node.js', rate: 72 },
    { role: 'Frontend', rate: 90 },
    { role: 'Software Eng', rate: 68 },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="role" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="rate" fill="#8884d8" name="Success Rate %" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export const ApplicationStatus = ({ stats }: AnalyticsProps) => {
  const data = [
    { name: 'Applied', value: stats?.total_applied || 10 },
    { name: 'Skipped', value: stats?.total_skipped || 3 },
    { name: 'Pending', value: 2 },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
};

export const TopCompanies = ({ stats }: AnalyticsProps) => {
  const data = [
    { company: 'Google', applications: 3 },
    { company: 'Amazon', applications: 2 },
    { company: 'Microsoft', applications: 2 },
    { company: 'Infosys', applications: 1 },
    { company: 'TCS', applications: 1 },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="company" type="category" width={100} />
        <Tooltip />
        <Legend />
        <Bar dataKey="applications" fill="#8884d8" name="Applications" />
      </BarChart>
    </ResponsiveContainer>
  );
};
