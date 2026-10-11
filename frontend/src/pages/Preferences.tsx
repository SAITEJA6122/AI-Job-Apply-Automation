import { useState, useEffect } from 'react';
import apiService from '../services/api';
import type { Profile } from '../types';
import { toast } from 'react-toastify';
import { MapPin, DollarSign, Briefcase, Building, Trash2, Plus } from 'lucide-react';

const Preferences = () => {
  const [profile, setProfile] = useState<Profile>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newLocation, setNewLocation] = useState('');
  const [newBlacklistCompany, setNewBlacklistCompany] = useState('');

  useEffect(() => {
    loadProfile();

    // Listen for Naukri disconnect event to reload profile
    const handleDisconnect = () => {
      loadProfile();
    };
    window.addEventListener('naukri-disconnected', handleDisconnect);

    // Listen for resume approve event to reload profile
    const handleResumeApprove = () => {
      loadProfile();
    };
    window.addEventListener('resume-approved', handleResumeApprove);

    return () => {
      window.removeEventListener('naukri-disconnected', handleDisconnect);
      window.removeEventListener('resume-approved', handleResumeApprove);
    };
  }, []);

  const loadProfile = async () => {
    try {
      const data = await apiService.getProfile();
      setProfile(data);
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await apiService.updateProfile(profile);
      toast.success('Preferences saved successfully!');
    } catch (error) {
      toast.error('Failed to save preferences: ' + error);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof Profile, value: any) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  const addLocation = () => {
    if (newLocation.trim()) {
      setProfile(prev => ({
        ...prev,
        preferred_locations: [...(prev.preferred_locations || []), newLocation.trim()]
      }));
      setNewLocation('');
    }
  };

  const removeLocation = (location: string) => {
    setProfile(prev => ({
      ...prev,
      preferred_locations: prev.preferred_locations?.filter(l => l !== location) || []
    }));
  };

  const addBlacklistCompany = () => {
    if (newBlacklistCompany.trim()) {
      setProfile(prev => ({
        ...prev,
        company_exclude: [...(prev.company_exclude || []), newBlacklistCompany.trim()]
      }));
      setNewBlacklistCompany('');
    }
  };

  const removeBlacklistCompany = (company: string) => {
    setProfile(prev => ({
      ...prev,
      company_exclude: prev.company_exclude?.filter(c => c !== company) || []
    }));
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Job Preferences</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Configure your job search preferences</p>
      </div>

      <div className="space-y-6 max-w-4xl">
        {/* Target Roles */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <Briefcase className="w-5 h-5" />
            Target Roles
          </h3>
          <div>
            <label className="label">Target Job Roles (comma-separated)</label>
            <textarea
              className="input"
              rows={4}
              value={profile.target_roles?.join(', ') || ''}
              onChange={(e) => handleChange('target_roles', e.target.value.split(',').map(s => s.trim()))}
              placeholder="e.g., Software Developer, Full Stack Engineer, Backend Developer"
            />
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              These roles will be used to find matching jobs on Naukri
            </p>
          </div>
        </div>

        {/* Location Preferences */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <MapPin className="w-5 h-5" />
            Location Preferences
          </h3>
          <div className="space-y-4">
            <div>
              <label className="label">Preferred Locations</label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  className="input flex-1"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  placeholder="Add a city (e.g., Bangalore, Mumbai)"
                  onKeyPress={(e) => e.key === 'Enter' && addLocation()}
                />
                <button
                  onClick={addLocation}
                  className="btn btn-secondary flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.preferred_locations?.map((location, index) => (
                  <div
                    key={index}
                    className="bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-full flex items-center gap-2 text-gray-900 dark:text-white"
                  >
                    {location}
                    <button
                      onClick={() => removeLocation(location)}
                      className="text-gray-500 hover:text-red-500"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="relocate"
                checked={profile.relocate_cities || false}
                onChange={(e) => handleChange('relocate_cities', e.target.checked)}
                className="w-4 h-4"
              />
              <label htmlFor="relocate" className="text-gray-700 dark:text-gray-300">
                Willing to relocate
              </label>
            </div>
          </div>
        </div>

        {/* Salary Expectations */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <DollarSign className="w-5 h-5" />
            Salary Expectations
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Current CTC (LPA)</label>
              <input
                type="number"
                step="0.5"
                className="input"
                value={profile.current_ctc_lpa || 0}
                onChange={(e) => handleChange('current_ctc_lpa', parseFloat(e.target.value))}
              />
            </div>
            <div>
              <label className="label">Expected CTC (LPA)</label>
              <input
                type="number"
                step="0.5"
                className="input"
                value={profile.expected_ctc_lpa || 0}
                onChange={(e) => handleChange('expected_ctc_lpa', parseFloat(e.target.value))}
              />
            </div>
          </div>
        </div>

        {/* Company Filtering */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
            <Building className="w-5 h-5" />
            Company Filtering
          </h3>
          <div className="space-y-4">
            <div>
              <label className="label">Blacklisted Companies (won't apply to these)</label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  className="input flex-1"
                  value={newBlacklistCompany}
                  onChange={(e) => setNewBlacklistCompany(e.target.value)}
                  placeholder="Add company to blacklist"
                  onKeyPress={(e) => e.key === 'Enter' && addBlacklistCompany()}
                />
                <button
                  onClick={addBlacklistCompany}
                  className="btn btn-secondary flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.company_exclude?.map((company, index) => (
                  <div
                    key={index}
                    className="bg-red-100 dark:bg-red-900/30 px-3 py-1 rounded-full flex items-center gap-2 text-red-900 dark:text-red-300"
                  >
                    {company}
                    <button
                      onClick={() => removeBlacklistCompany(company)}
                      className="text-red-700 hover:text-red-900 dark:text-red-400 dark:hover:text-red-200"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Additional Preferences */}
        <div className="card bg-white dark:bg-gray-800">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Additional Preferences</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="night_shift"
                checked={profile.night_shift_ok || false}
                onChange={(e) => handleChange('night_shift_ok', e.target.checked)}
                className="w-4 h-4"
              />
              <label htmlFor="night_shift" className="text-gray-700 dark:text-gray-300">
                Open to night shifts
              </label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="weekend"
                checked={profile.weekend_ok || false}
                onChange={(e) => handleChange('weekend_ok', e.target.checked)}
                className="w-4 h-4"
              />
              <label htmlFor="weekend" className="text-gray-700 dark:text-gray-300">
                Open to weekend work
              </label>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="immediately"
                checked={profile.immediately_available || false}
                onChange={(e) => handleChange('immediately_available', e.target.checked)}
                className="w-4 h-4"
              />
              <label htmlFor="immediately" className="text-gray-700 dark:text-gray-300">
                Immediately available
              </label>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn btn-primary"
          >
            {saving ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Preferences;
