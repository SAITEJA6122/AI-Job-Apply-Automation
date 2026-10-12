import { useState, useEffect } from 'react';
import apiService from '../services/api';
import type { Profile } from '../types';
import { toast } from 'react-toastify';
import { Plus, X } from 'lucide-react';

const JobPreferences = () => {
  const [profile, setProfile] = useState<Profile>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [customRole, setCustomRole] = useState('');

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
      // Map total_experience_years to seniority_floor and ceiling if not set
      if (data.total_experience_years && !data.seniority_floor_years) {
        data.seniority_floor_years = Math.max(0, data.total_experience_years - 1);
        data.seniority_ceiling_years = data.total_experience_years + 1;
      }
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

  const handleAddCustomRole = () => {
    if (customRole.trim()) {
      const currentRoles = profile.target_roles || [];
      if (!currentRoles.includes(customRole.trim())) {
        setProfile(prev => ({
          ...prev,
          target_roles: [...currentRoles, customRole.trim()]
        }));
        setCustomRole('');
      }
    }
  };

  const handleRemoveCustomRole = (role: string) => {
    const currentRoles = profile.target_roles || [];
    setProfile(prev => ({
      ...prev,
      target_roles: currentRoles.filter(r => r !== role)
    }));
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-4xl font-bold gradient-text text-shadow-lg">Job Preferences</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2 text-lg">Configure your job search preferences</p>
      </div>

      <div className="card-gradient max-w-4xl animate-slide-up">
        <div className="space-y-6">
          {/* Target Roles */}
          <div>
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Target Roles</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Roles automatically extracted from your resume. Add missing roles if needed.
            </p>

            {/* Roles from Resume */}
            <div className="flex flex-wrap gap-2 mb-4">
              {(profile.target_roles || []).map((role) => (
                <div
                  key={role}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30 text-blue-700 dark:text-blue-300 rounded-full border border-blue-200 dark:border-blue-700"
                >
                  {role}
                  <button
                    onClick={() => handleRemoveCustomRole(role)}
                    className="text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-200"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>

            {/* Add Custom Role */}
            <div className="flex gap-2">
              <input
                type="text"
                className="input flex-1"
                placeholder="Add missing role (e.g., Angular Developer)"
                value={customRole}
                onChange={(e) => setCustomRole(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleAddCustomRole();
                  }
                }}
              />
              <button
                onClick={handleAddCustomRole}
                className="btn btn-primary flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add
              </button>
            </div>
          </div>

          {/* Experience Range */}
          <div>
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Experience Range</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Minimum Experience (Years)</label>
                <input
                  type="number"
                  className="input"
                  value={profile.seniority_floor_years || 0}
                  onChange={(e) => setProfile(prev => ({ 
                    ...prev, 
                    seniority_floor_years: parseInt(e.target.value) 
                  }))}
                />
              </div>
              <div>
                <label className="label">Maximum Experience (Years)</label>
                <input
                  type="number"
                  className="input"
                  value={profile.seniority_ceiling_years || 1}
                  onChange={(e) => setProfile(prev => ({ 
                    ...prev, 
                    seniority_ceiling_years: parseInt(e.target.value) 
                  }))}
                />
              </div>
            </div>
          </div>

          {/* Location Preferences */}
          <div>
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Location Preferences</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Preferred Locations (comma-separated)</label>
                <input
                  type="text"
                  className="input"
                  value={(profile.preferred_locations || []).join(', ')}
                  onChange={(e) => setProfile(prev => ({ 
                    ...prev, 
                    preferred_locations: e.target.value.split(',').map(s => s.trim()) 
                  }))}
                />
              </div>
              <div className="flex items-center p-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-700">
                <input
                  type="checkbox"
                  id="relocate"
                  checked={profile.relocate_cities || false}
                  onChange={(e) => setProfile(prev => ({ 
                    ...prev, 
                    relocate_cities: e.target.checked 
                  }))}
                  className="mr-3 w-5 h-5"
                />
                <label htmlFor="relocate" className="text-gray-900 dark:text-white font-medium">
                  Willing to relocate
                </label>
              </div>
            </div>
          </div>

          {/* Salary Preferences */}
          <div>
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Salary Preferences</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Minimum CTC (LPA)</label>
                <input
                  type="number"
                  step="0.5"
                  className="input"
                  value={profile.salary_floor_lpa || 2.5}
                  onChange={(e) => setProfile(prev => ({ 
                    ...prev, 
                    salary_floor_lpa: parseFloat(e.target.value) 
                  }))}
                />
              </div>
              <div>
                <label className="label">Expected CTC (LPA)</label>
                <input
                  type="number"
                  step="0.5"
                  className="input"
                  value={profile.expected_ctc_lpa || 3}
                  onChange={(e) => setProfile(prev => ({ 
                    ...prev, 
                    expected_ctc_lpa: parseFloat(e.target.value) 
                  }))}
                />
              </div>
            </div>
          </div>

          {/* Work Preferences */}
          <div>
            <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Work Preferences</h3>
            <div className="space-y-3">
              <div className="flex items-center p-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-700">
                <input
                  type="checkbox"
                  id="night-shift"
                  checked={profile.night_shift_ok || false}
                  onChange={(e) => setProfile(prev => ({ 
                    ...prev, 
                    night_shift_ok: e.target.checked 
                  }))}
                  className="mr-3 w-5 h-5"
                />
                <label htmlFor="night-shift" className="text-gray-900 dark:text-white font-medium">
                  Willing to work night shifts
                </label>
              </div>
              <div className="flex items-center p-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-700">
                <input
                  type="checkbox"
                  id="weekend"
                  checked={profile.weekend_ok || false}
                  onChange={(e) => setProfile(prev => ({ 
                    ...prev, 
                    weekend_ok: e.target.checked 
                  }))}
                  className="mr-3 w-5 h-5"
                />
                <label htmlFor="weekend" className="text-gray-900 dark:text-white font-medium">
                  Willing to work weekends
                </label>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end pt-4">
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
    </div>
  );
};

export default JobPreferences;
