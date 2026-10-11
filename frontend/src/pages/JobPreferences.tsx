import { useState, useEffect } from 'react';
import apiService from '../services/api';
import type { Profile } from '../types';
import { toast } from 'react-toastify';
import { Plus } from 'lucide-react';

const TARGET_ROLES = [
  'Full Stack Developer',
  'MERN Stack Developer',
  'React Developer',
  'Node.js Developer',
  'Frontend Developer',
  'Software Developer',
  'Software Engineer',
  'Web Developer',
  'Junior Software Developer',
  'Junior Software Engineer',
  'Junior Full Stack Developer',
  'Associate Software Engineer',
  'Associate Developer',
  'Graduate Software Engineer',
  'Trainee Software Engineer',
  'Frontend Engineer',
  'React.js Developer',
  'JavaScript Developer',
  'Backend Developer',
];

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

  const handleToggleRole = (role: string) => {
    const currentRoles = profile.target_roles || [];
    if (currentRoles.includes(role)) {
      setProfile(prev => ({
        ...prev,
        target_roles: currentRoles.filter(r => r !== role)
      }));
    } else {
      setProfile(prev => ({
        ...prev,
        target_roles: [...currentRoles, role]
      }));
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
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Job Preferences</h1>
        <p className="text-gray-600 mt-1">Configure your job search preferences</p>
      </div>

      <div className="card max-w-4xl">
        <div className="space-y-6">
          {/* Target Roles */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Target Roles</h3>
            <p className="text-sm text-gray-600 mb-4">Select from predefined roles or add custom ones</p>

            {/* Predefined Roles */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
              {TARGET_ROLES.map((role) => {
                const isSelected = (profile.target_roles || []).includes(role);
                return (
                  <button
                    key={role}
                    onClick={() => handleToggleRole(role)}
                    className={`p-3 rounded-lg border-2 transition-colors ${
                      isSelected
                        ? 'border-primary-600 bg-primary-50 text-primary-700'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    {role}
                  </button>
                );
              })}
            </div>

            {/* Add Custom Role */}
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                className="input flex-1"
                placeholder="Add custom role (e.g., Angular Developer)"
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

            {/* Selected Roles Display */}
            {(profile.target_roles || []).length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Selected Roles:</h4>
                <div className="flex flex-wrap gap-2">
                  {(profile.target_roles || []).map((role) => (
                    <div
                      key={role}
                      className="inline-flex items-center gap-2 px-3 py-1 bg-primary-100 text-primary-700 rounded-full"
                    >
                      {role}
                      <button
                        onClick={() => handleRemoveCustomRole(role)}
                        className="text-primary-500 hover:text-primary-700"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Experience Range */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Experience Range</h3>
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
            <h3 className="text-lg font-semibold mb-4">Location Preferences</h3>
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
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="relocate"
                  checked={profile.relocate_cities || false}
                  onChange={(e) => setProfile(prev => ({ 
                    ...prev, 
                    relocate_cities: e.target.checked 
                  }))}
                  className="mr-2"
                />
                <label htmlFor="relocate" className="text-gray-700">
                  Willing to relocate
                </label>
              </div>
            </div>
          </div>

          {/* Salary Preferences */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Salary Preferences</h3>
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
            <h3 className="text-lg font-semibold mb-4">Work Preferences</h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="night-shift"
                  checked={profile.night_shift_ok || false}
                  onChange={(e) => setProfile(prev => ({ 
                    ...prev, 
                    night_shift_ok: e.target.checked 
                  }))}
                  className="mr-2"
                />
                <label htmlFor="night-shift" className="text-gray-700">
                  Willing to work night shifts
                </label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="weekend"
                  checked={profile.weekend_ok || false}
                  onChange={(e) => setProfile(prev => ({ 
                    ...prev, 
                    weekend_ok: e.target.checked 
                  }))}
                  className="mr-2"
                />
                <label htmlFor="weekend" className="text-gray-700">
                  Willing to work weekends
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
    </div>
  );
};

export default JobPreferences;
