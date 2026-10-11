import { useState, useEffect } from 'react';
import apiService from '../services/api';
import { Trash2, AlertTriangle, Settings as SettingsIcon, Key, Bell, Zap, Eye, EyeOff, Save } from 'lucide-react';
import { toast } from 'react-toastify';
import ConfirmDialog from '../components/ConfirmDialog';
import type { Profile } from '../types';

const Settings = () => {
  const [cleaning, setCleaning] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState<Profile>({});
  const [showApiKeys, setShowApiKeys] = useState(false);
  const [apiKeyForm, setApiKeyForm] = useState({
    gemini: '',
    groq: '',
    openrouter: ''
  });
  const [apiKeysStatus, setApiKeysStatus] = useState({
    gemini_configured: false,
    groq_configured: false,
    openrouter_configured: false
  });

  useEffect(() => {
    loadProfile();
    loadApiKeysStatus();

    // Listen for Naukri disconnect event to reload profile
    const handleDisconnect = () => {
      loadProfile();
      loadApiKeysStatus();
    };
    window.addEventListener('naukri-disconnected', handleDisconnect);

    return () => {
      window.removeEventListener('naukri-disconnected', handleDisconnect);
    };
  }, []);

  const loadProfile = async () => {
    try {
      const data = await apiService.getProfile();
      setProfile(data);
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  };

  const loadApiKeysStatus = async () => {
    try {
      const status = await apiService.getApiKeysStatus();
      setApiKeysStatus(status);
    } catch (error) {
      console.error('Error loading API keys status:', error);
    }
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    try {
      await apiService.updateProfile(profile);
      toast.success('Settings saved successfully!');
    } catch (error) {
      toast.error('Failed to save settings: ' + error);
    } finally {
      setSaving(false);
    }
  };

  const handleCleanup = async () => {
    setCleaning(true);
    try {
      await apiService.triggerCleanup();
      toast.success('Cleanup completed successfully!');
    } catch (error) {
      toast.error('Failed to cleanup: ' + error);
    } finally {
      setCleaning(false);
    }
  };

  const handleChange = (field: keyof Profile, value: any) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  const handleSaveApiKeys = async () => {
    try {
      await apiService.saveApiKeys({
        gemini_key: apiKeyForm.gemini,
        groq_key: apiKeyForm.groq,
        openrouter_key: apiKeyForm.openrouter
      });
      toast.success('API keys saved successfully!');
    } catch (error) {
      toast.error('Failed to save API keys: ' + error);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your application settings</p>
      </div>

      <div className="space-y-6 max-w-4xl">
        {/* Automation Configuration */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <SettingsIcon className="w-5 h-5" />
            Automation Configuration
          </h3>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Max Applications per Day</label>
                <input
                  type="number"
                  className="input"
                  value={profile.max_applications_per_day || 20}
                  onChange={(e) => handleChange('max_applications_per_day', parseInt(e.target.value))}
                />
              </div>
              <div>
                <label className="label">Max Applications per Hour</label>
                <input
                  type="number"
                  className="input"
                  value={profile.max_applications_per_hour || 15}
                  onChange={(e) => handleChange('max_applications_per_hour', parseInt(e.target.value))}
                />
              </div>
              <div>
                <label className="label">Pace Between Applications (seconds)</label>
                <input
                  type="number"
                  className="input"
                  value={profile.pace_seconds_between_actions || 30}
                  onChange={(e) => handleChange('pace_seconds_between_actions', parseInt(e.target.value))}
                />
              </div>
              <div>
                <label className="label">Browser Mode</label>
                <select
                  className="input"
                  value={profile.browser_mode || 'minimized'}
                  onChange={(e) => handleChange('browser_mode', e.target.value)}
                >
                  <option value="minimized">Minimized</option>
                  <option value="visible">Visible</option>
                </select>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="stop_on_captcha"
                checked={profile.stop_on_captcha !== false}
                onChange={(e) => handleChange('stop_on_captcha', e.target.checked)}
                className="w-4 h-4"
              />
              <label htmlFor="stop_on_captcha" className="text-gray-700 dark:text-gray-300">
                Stop on CAPTCHA
              </label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="stop_on_rate_limit"
                checked={profile.stop_on_rate_limit !== false}
                onChange={(e) => handleChange('stop_on_rate_limit', e.target.checked)}
                className="w-4 h-4"
              />
              <label htmlFor="stop_on_rate_limit" className="text-gray-700 dark:text-gray-300">
                Stop on Rate Limit
              </label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="enable_screen_capture"
                checked={profile.enable_screen_capture !== false}
                onChange={(e) => handleChange('enable_screen_capture', e.target.checked)}
                className="w-4 h-4"
              />
              <label htmlFor="enable_screen_capture" className="text-gray-700 dark:text-gray-300">
                Enable Live Screen Capture
              </label>
            </div>
            <div>
              <label className="label">Screen Capture Interval (seconds)</label>
              <input
                type="number"
                className="input"
                value={profile.screen_capture_interval || 2}
                onChange={(e) => handleChange('screen_capture_interval', parseInt(e.target.value))}
                min="1"
                max="10"
              />
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                How often to capture screen updates (1-10 seconds)
              </p>
            </div>
          </div>
        </div>

        {/* API Key Management */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <Key className="w-5 h-5" />
            API Key Management
          </h3>
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <button
                onClick={() => setShowApiKeys(!showApiKeys)}
                className="btn btn-secondary flex items-center gap-2"
              >
                {showApiKeys ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                {showApiKeys ? 'Hide Keys' : 'Show Keys'}
              </button>
            </div>
            <div>
              <label className="label">Gemini API Key</label>
              <input
                type={showApiKeys ? 'text' : 'password'}
                className="input"
                value={apiKeyForm.gemini}
                onChange={(e) => setApiKeyForm({ ...apiKeyForm, gemini: e.target.value })}
                placeholder="Enter your Gemini API key"
              />
              <div className="flex items-center gap-2 mt-1">
                {apiKeysStatus.gemini_configured ? (
                  <span className="text-sm text-green-600 dark:text-green-400">✓ Configured</span>
                ) : (
                  <span className="text-sm text-yellow-600 dark:text-yellow-400">⚠ Not configured</span>
                )}
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Get your free key from: <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">https://aistudio.google.com/apikey</a>
              </p>
            </div>
            <div>
              <label className="label">Groq API Key (Optional)</label>
              <input
                type={showApiKeys ? 'text' : 'password'}
                className="input"
                value={apiKeyForm.groq}
                onChange={(e) => setApiKeyForm({ ...apiKeyForm, groq: e.target.value })}
                placeholder="Enter your Groq API key"
              />
              <div className="flex items-center gap-2 mt-1">
                {apiKeysStatus.groq_configured ? (
                  <span className="text-sm text-green-600 dark:text-green-400">✓ Configured</span>
                ) : (
                  <span className="text-sm text-gray-500 dark:text-gray-400">Optional</span>
                )}
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Used as fallback if Gemini quota is exhausted. Get your key from: <a href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">https://console.groq.com/keys</a>
              </p>
            </div>
            <div>
              <label className="label">OpenRouter API Key (Optional)</label>
              <input
                type={showApiKeys ? 'text' : 'password'}
                className="input"
                value={apiKeyForm.openrouter}
                onChange={(e) => setApiKeyForm({ ...apiKeyForm, openrouter: e.target.value })}
                placeholder="Enter your OpenRouter API key"
              />
              <div className="flex items-center gap-2 mt-1">
                {apiKeysStatus.openrouter_configured ? (
                  <span className="text-sm text-green-600 dark:text-green-400">✓ Configured</span>
                ) : (
                  <span className="text-sm text-gray-500 dark:text-gray-400">Optional</span>
                )}
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Used as fallback if Gemini and Groq are unavailable. Get your key from: <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">https://openrouter.ai/keys</a>
              </p>
            </div>
            <button
              onClick={handleSaveApiKeys}
              className="btn btn-primary flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save API Keys
            </button>
            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <strong>Note:</strong> API keys are stored in your .env file. Make sure .env is in .gitignore to prevent accidental commits.
              </p>
            </div>
          </div>
        </div>

        {/* Notification Preferences */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Notification Preferences
          </h3>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="email_notif"
                checked={profile.email_notifications !== false}
                onChange={(e) => handleChange('email_notifications', e.target.checked)}
                className="w-4 h-4"
              />
              <label htmlFor="email_notif" className="text-gray-700 dark:text-gray-300">
                Email notifications
              </label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="desktop_notif"
                checked={profile.desktop_notifications !== false}
                onChange={(e) => handleChange('desktop_notifications', e.target.checked)}
                className="w-4 h-4"
              />
              <label htmlFor="desktop_notif" className="text-gray-700 dark:text-gray-300">
                Desktop notifications
              </label>
            </div>
          </div>
        </div>

        {/* Rate Limiting */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Rate Limiting
          </h3>
          <div className="space-y-3 text-gray-600 dark:text-gray-400">
            <p>• API requests: 1000 per day, 200 per hour</p>
            <p>• Login attempts: 20 per hour</p>
            <p>• Burst allowance: Short-term high-frequency requests allowed</p>
            <p className="text-sm text-yellow-600 dark:text-yellow-400 mt-2">
              These limits prevent abuse while allowing normal usage
            </p>
          </div>
        </div>

        {/* Security Information */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Security Information</h3>
          <div className="space-y-3 text-gray-600 dark:text-gray-400">
            <p>• Naukri passwords are never stored by this application</p>
            <p>• Session data is automatically deleted after 12 hours</p>
            <p>• Authentication cookies are encrypted and protected</p>
            <p>• Resume files are stored temporarily and deleted after expiration</p>
          </div>
        </div>

        {/* Data Management */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Data Management</h3>
          <div className="space-y-4">
            <div className="flex items-start p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mr-3 mt-0.5" />
              <div>
                <p className="font-medium text-yellow-800 dark:text-yellow-200">Session Cleanup</p>
                <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                  Clean up expired sessions and temporary data. This action cannot be undone.
                </p>
              </div>
            </div>
            <button
              onClick={() => setShowConfirmDialog(true)}
              disabled={cleaning}
              className="btn btn-danger"
            >
              <Trash2 className="w-4 h-4 mr-2 inline" />
              {cleaning ? 'Cleaning...' : 'Clean Up Expired Sessions'}
            </button>
          </div>
        </div>

        {/* Save Settings Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSaveSettings}
            disabled={saving}
            className="btn btn-primary"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>

        {/* API Configuration */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">API Configuration</h3>
          <div className="space-y-3 text-gray-600 dark:text-gray-400">
            <p>• Backend API: <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">http://localhost:5000</code></p>
            <p>• Frontend: <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">http://localhost:3000</code></p>
            <p>• Session expiration: 12 hours</p>
          </div>
        </div>

        {/* Privacy Notice */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Privacy Notice</h3>
          <div className="space-y-3 text-gray-600 dark:text-gray-400">
            <p>This application processes your personal information for job application automation. By using this service, you agree to:</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Allow temporary storage of your session data (max 12 hours)</li>
              <li>Allow automated job applications on your behalf</li>
              <li>Allow AI-assisted screening question responses</li>
            </ul>
            <p className="mt-4 text-sm">
              All personal data is automatically deleted after 12 hours. You can manually disconnect your Naukri account at any time from the Dashboard.
            </p>
          </div>
        </div>
      </div>

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={showConfirmDialog}
        onClose={() => setShowConfirmDialog(false)}
        onConfirm={handleCleanup}
        title="Clean Up Expired Sessions"
        message="Are you sure you want to clean up expired sessions? This will delete all expired session data."
        confirmText="Clean Up"
        cancelText="Cancel"
        variant="danger"
      />
    </div>
  );
};

export default Settings;
