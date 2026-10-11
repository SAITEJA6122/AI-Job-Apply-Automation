import { useState, useEffect } from 'react';
import apiService from '../services/api';
import { toast } from 'react-toastify';
import {
  CheckCircle,
  XCircle,
  Play,
  StopCircle,
  TrendingUp,
  Briefcase,
  AlertCircle,
  Clock,
  FileText
} from 'lucide-react';
import RealTimeProgress from '../components/RealTimeProgress';
import TerminalOutput from '../components/TerminalOutput';
import StatisticsCharts from '../components/StatisticsCharts';
import LiveScreen from '../components/LiveScreen';

const Dashboard = () => {
  const [sessionStatus, setSessionStatus] = useState<any>(null);
  const [automationRunning, setAutomationRunning] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [loginData, setLoginData] = useState({ email: '', password: '' });
  const [loginLoading, setLoginLoading] = useState(false);
  const [resumeStatus, setResumeStatus] = useState<any>(null);
  const [previousRunningState, setPreviousRunningState] = useState(false);

  useEffect(() => {
    loadData();
    // Refresh every 2 seconds when automation is running, 5 seconds otherwise
    const interval = setInterval(loadData, automationRunning ? 2000 : 5000);

    // Listen for Naukri disconnect event to reload data
    const handleDisconnect = () => {
      loadData();
    };
    window.addEventListener('naukri-disconnected', handleDisconnect);

    // Listen for resume delete event to reload data
    const handleResumeDelete = () => {
      loadData();
    };
    window.addEventListener('resume-deleted', handleResumeDelete);

    // Listen for resume approve event to reload data
    const handleResumeApprove = () => {
      loadData();
    };
    window.addEventListener('resume-approved', handleResumeApprove);

    return () => {
      clearInterval(interval);
      window.removeEventListener('naukri-disconnected', handleDisconnect);
      window.removeEventListener('resume-deleted', handleResumeDelete);
      window.removeEventListener('resume-approved', handleResumeApprove);
    };
  }, [automationRunning]);

  const loadData = async () => {
    try {
      const [session, autoStatus, statsData, resumeData] = await Promise.all([
        apiService.getSessionStatus(),
        apiService.getAutomationStatus(),
        apiService.getStats().catch(() => null),
        apiService.getResumeStatus().catch(() => ({ has_resume: false, profile_complete: false })),
      ]);

      setSessionStatus(session);

      // Check if automation status changed from running to stopped
      if (previousRunningState && !autoStatus.running) {
        toast.info('Automation has stopped', {
          position: 'top-right',
          autoClose: 5000,
        });
      }

      setAutomationRunning(autoStatus.running);
      setPreviousRunningState(autoStatus.running);
      setStats(statsData);
      setResumeStatus(resumeData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectNaukri = async () => {
    // Check if resume has been uploaded first
    if (!resumeStatus?.has_resume || !resumeStatus?.profile_complete) {
      toast.error('Please upload and approve your resume first before connecting to Naukri.');
      return;
    }
    // Show login form instead of direct connection
    setShowLoginForm(true);
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginLoading(true);

    try {
      const response = await apiService.loginWithCredentials(loginData);
      if (response.success) {
        toast.success('Login successful! Session created.');
        setShowLoginForm(false);
        setLoginData({ email: '', password: '' });
        loadData();
        // Auto-start automation after successful login
        setTimeout(async () => {
          try {
            await apiService.startAutomation();
            loadData();
            toast.info('Automation started automatically.');
          } catch (error: any) {
            console.error('Failed to auto-start automation:', error);
            if (error.response?.data?.error) {
              toast.error(error.response.data.error);
            } else {
              toast.error('Failed to start automation. Please start manually.');
            }
          }
        }, 2000);
      } else {
        toast.error('Login failed: ' + (response.error || 'Unknown error'));
      }
    } catch (error: any) {
      if (error.response?.data?.error) {
        toast.error(error.response.data.error);
      } else {
        toast.error('Login failed: ' + error);
      }
    } finally {
      setLoginLoading(false);
    }
  };

  const handleDisconnectNaukri = async () => {
    try {
      await apiService.disconnectNaukri();
      toast.success('Naukri disconnected successfully.');
      loadData();
      // Emit event to clear profile data on all pages
      window.dispatchEvent(new CustomEvent('naukri-disconnected'));
      // Emit event to clear resume status
      window.dispatchEvent(new CustomEvent('resume-deleted'));
    } catch (error) {
      toast.error('Failed to disconnect: ' + error);
    }
  };

  const handleStartAutomation = async () => {
    try {
      const response = await apiService.startAutomation();
      if (response.success) {
        toast.success('Automation started successfully.');
        loadData();
      } else {
        toast.error(response.error || 'Failed to start automation');
      }
    } catch (error: any) {
      if (error.response?.data?.error) {
        toast.error(error.response.data.error);
      } else {
        toast.error('Failed to start automation: ' + error);
      }
    }
  };

  const handleStopAutomation = async () => {
    try {
      await apiService.stopAutomation();
      toast.success('Automation stopped successfully.');
      loadData();
    } catch (error) {
      toast.error('Failed to stop automation: ' + error);
    }
  };

  const formatTimeRemaining = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  // Login Form Modal
  if (showLoginForm) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-8 max-w-md w-full mx-4">
          <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Connect Naukri Account</h2>
          <form onSubmit={handleLoginSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email / Username
              </label>
              <input
                type="text"
                value={loginData.email}
                onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Enter your Naukri email or username"
                required
              />
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Password
              </label>
              <input
                type="password"
                value={loginData.password}
                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Enter your Naukri password"
                required
              />
            </div>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-6">
              <p className="text-sm text-yellow-800 dark:text-yellow-200">
                <strong>Security Note:</strong> Your credentials are used only to create a secure session.
                They are never stored and will be deleted immediately after login.
              </p>
            </div>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => {
                  setShowLoginForm(false);
                  setLoginData({ email: '', password: '' });
                }}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-white"
                disabled={loginLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                disabled={loginLoading}
              >
                {loginLoading ? 'Logging in...' : 'Connect & Start'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Monitor your job application automation</p>
      </div>

      {/* Session Status Card */}
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {sessionStatus?.connected ? (
              <CheckCircle className="w-8 h-8 text-green-600 mr-4" />
            ) : (
              <XCircle className="w-8 h-8 text-red-600 mr-4" />
            )}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Naukri Account Status</h3>
              <p className="text-gray-600 dark:text-gray-400">
                {sessionStatus?.connected ? 'Connected' : 'Not Connected'}
              </p>
              {!sessionStatus?.connected && (
                <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                  {!resumeStatus?.has_resume ? (
                    <>
                      <span className="text-yellow-600 font-medium">Step 1:</span> Upload your resume first
                    </>
                  ) : (
                    'Login to start automated job applications'
                  )}
                </p>
              )}
              {sessionStatus?.connected && sessionStatus.time_remaining_seconds && (
                <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                  Expires in: {formatTimeRemaining(sessionStatus.time_remaining_seconds)}
                </p>
              )}
            </div>
          </div>
          <div>
            {sessionStatus?.connected ? (
              <button
                onClick={handleDisconnectNaukri}
                className="btn btn-danger"
              >
                Disconnect
              </button>
            ) : (
              <button
                onClick={handleConnectNaukri}
                className="btn btn-primary"
                disabled={!resumeStatus?.has_resume}
                title={!resumeStatus?.has_resume ? 'Upload resume first' : 'Login with Naukri'}
              >
                {resumeStatus?.has_resume ? 'Login with Naukri' : 'Upload Resume First'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Resume Status Card */}
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {resumeStatus?.has_resume ? (
              <CheckCircle className="w-8 h-8 text-green-600 mr-4" />
            ) : (
              <FileText className="w-8 h-8 text-yellow-600 mr-4" />
            )}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Resume Status</h3>
              <p className="text-gray-600 dark:text-gray-400">
                {resumeStatus?.has_resume ? 'Resume uploaded and profile populated' : 'No resume uploaded'}
              </p>
              {!resumeStatus?.has_resume && (
                <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                  Upload your resume to extract skills, experience, and job roles
                </p>
              )}
              {resumeStatus?.has_resume && resumeStatus?.profile && (
                <>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                    {resumeStatus.profile.skills?.length || 0} skills extracted
                  </p>
                  {resumeStatus.resume_filename && (
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                      File: {resumeStatus.resume_filename}
                    </p>
                  )}
                </>
              )}
            </div>
          </div>
          <div>
            <a
              href="/resume"
              className="btn btn-secondary"
            >
              {resumeStatus?.has_resume ? 'View Profile' : 'Upload Resume'}
            </a>
          </div>
        </div>
      </div>

      {/* Real-time Progress */}
      <RealTimeProgress />

      {/* Automation Control */}
      <div className="card bg-white dark:bg-gray-800 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {automationRunning ? (
              <Play className="w-8 h-8 text-green-600 mr-4" />
            ) : (
              <StopCircle className="w-8 h-8 text-gray-600 mr-4" />
            )}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Automation Status</h3>
              <p className="text-gray-600 dark:text-gray-400">
                {automationRunning ? 'Running' : 'Stopped'}
              </p>
            </div>
          </div>
          <div>
            {automationRunning ? (
              <button
                onClick={handleStopAutomation}
                className="btn btn-danger"
              >
                Stop Automation
              </button>
            ) : (
              <button
                onClick={handleStartAutomation}
                className="btn btn-success"
                disabled={!sessionStatus?.connected}
              >
                Start Automation
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Statistics Grid */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-6">
          <div className="card bg-white dark:bg-gray-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Jobs Found</p>
                <p className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">{stats.total_seen || 0}</p>
              </div>
              <Briefcase className="w-6 h-6 lg:w-8 lg:h-8 text-primary-600" />
            </div>
          </div>

          <div className="card bg-white dark:bg-gray-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Applications</p>
                <p className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">{stats.total_applied || 0}</p>
              </div>
              <TrendingUp className="w-6 h-6 lg:w-8 lg:h-8 text-green-600" />
            </div>
          </div>

          <div className="card bg-white dark:bg-gray-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Skipped</p>
                <p className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">{stats.total_skipped || 0}</p>
              </div>
              <AlertCircle className="w-6 h-6 lg:w-8 lg:h-8 text-yellow-600" />
            </div>
          </div>

          <div className="card bg-white dark:bg-gray-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Success Rate</p>
                <p className="text-2xl lg:text-3xl font-bold text-gray-900 dark:text-white">
                  {stats.success_rate ? stats.success_rate.toFixed(1) : 0}%
                </p>
              </div>
              <Clock className="w-6 h-6 lg:w-8 lg:h-8 text-blue-600" />
            </div>
          </div>
        </div>
      )}

      {/* Statistics Charts */}
      {stats && <StatisticsCharts stats={stats} />}

      {/* Quick Actions */}
      <div className="card bg-white dark:bg-gray-800">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="btn btn-secondary w-full text-gray-900 dark:text-white">
            View Application History
          </button>
          <button className="btn btn-secondary w-full text-gray-900 dark:text-white">
            Update Profile
          </button>
          <button className="btn btn-secondary w-full text-gray-900 dark:text-white">
            Configure Job Preferences
          </button>
        </div>
      </div>

      {/* Terminal Output */}
      <TerminalOutput />

      {/* Live Screen */}
      <LiveScreen />
    </div>
  );
};

export default Dashboard;
