import { useState, useEffect } from 'react';
import apiService from '../services/api';
import type { Profile } from '../types';
import { toast } from 'react-toastify';

const Profile = () => {
  const [profile, setProfile] = useState<Profile>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [resumeStatus, setResumeStatus] = useState<any>(null);

  useEffect(() => {
    loadProfile();
    loadResumeStatus();

    // Listen for Naukri disconnect event to reload profile
    const handleDisconnect = () => {
      loadProfile();
      loadResumeStatus();
    };
    window.addEventListener('naukri-disconnected', handleDisconnect);

    // Listen for resume delete event to reload status
    const handleResumeDelete = () => {
      loadResumeStatus();
    };
    window.addEventListener('resume-deleted', handleResumeDelete);

    // Listen for resume approve event to reload profile
    const handleResumeApprove = () => {
      loadProfile();
      loadResumeStatus();
    };
    window.addEventListener('resume-approved', handleResumeApprove);

    return () => {
      window.removeEventListener('naukri-disconnected', handleDisconnect);
      window.removeEventListener('resume-deleted', handleResumeDelete);
      window.removeEventListener('resume-approved', handleResumeApprove);
    };
  }, []);

  const loadResumeStatus = async () => {
    try {
      const status = await apiService.getResumeStatus();
      setResumeStatus(status);
    } catch (error) {
      console.error('Error loading resume status:', error);
    }
  };

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
      toast.success('Profile saved successfully!');
    } catch (error) {
      toast.error('Failed to save profile: ' + error);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof Profile, value: any) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Profile</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your professional profile</p>
        {resumeStatus?.has_resume && (
          <div className="mt-2 flex items-center text-sm text-green-600 dark:text-green-400">
            <span className="bg-green-100 dark:bg-green-900/30 px-3 py-1 rounded-full">
              ✓ Auto-populated from resume
            </span>
          </div>
        )}
      </div>

      <div className="card max-w-4xl">
        <div className="space-y-6">
          {/* Personal Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Personal Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Full Name</label>
                <input
                  type="text"
                  className="input"
                  value={profile.full_name || ''}
                  onChange={(e) => handleChange('full_name', e.target.value)}
                />
              </div>
              <div>
                <label className="label">Email</label>
                <input
                  type="email"
                  className="input"
                  value={profile.email || ''}
                  onChange={(e) => handleChange('email', e.target.value)}
                />
              </div>
              <div>
                <label className="label">Phone</label>
                <input
                  type="tel"
                  className="input"
                  value={profile.phone || ''}
                  onChange={(e) => handleChange('phone', e.target.value)}
                />
              </div>
              <div>
                <label className="label">Current City</label>
                <input
                  type="text"
                  className="input"
                  value={profile.current_city || ''}
                  onChange={(e) => handleChange('current_city', e.target.value)}
                />
              </div>
              <div>
                <label className="label">LinkedIn</label>
                <input
                  type="url"
                  className="input"
                  value={profile.linkedin || ''}
                  onChange={(e) => handleChange('linkedin', e.target.value)}
                />
              </div>
              <div>
                <label className="label">GitHub</label>
                <input
                  type="url"
                  className="input"
                  value={profile.github || ''}
                  onChange={(e) => handleChange('github', e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Professional Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Professional Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Total Experience (Years)</label>
                <input
                  type="number"
                  className="input"
                  value={profile.total_experience_years || 0}
                  onChange={(e) => handleChange('total_experience_years', parseInt(e.target.value))}
                />
              </div>
              <div>
                <label className="label">Notice Period (Days)</label>
                <input
                  type="number"
                  className="input"
                  value={profile.notice_period_days || 0}
                  onChange={(e) => handleChange('notice_period_days', parseInt(e.target.value))}
                />
              </div>
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
              <div>
                <label className="label">Current Company</label>
                <input
                  type="text"
                  className="input"
                  value={profile.current_company || ''}
                  onChange={(e) => handleChange('current_company', e.target.value)}
                />
              </div>
              <div>
                <label className="label">Current Role</label>
                <input
                  type="text"
                  className="input"
                  value={profile.current_role || ''}
                  onChange={(e) => handleChange('current_role', e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Skills */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Skills</h3>
            <div>
              <label className="label">Skills (comma-separated)</label>
              <textarea
                className="input"
                rows={4}
                value={profile.skills?.join(', ') || ''}
                onChange={(e) => handleChange('skills', e.target.value.split(',').map(s => s.trim()))}
              />
            </div>
          </div>

          {/* Target Roles */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Target Roles</h3>
            <div>
              <label className="label">Target Job Roles (comma-separated)</label>
              <textarea
                className="input"
                rows={3}
                value={profile.target_roles?.join(', ') || ''}
                onChange={(e) => handleChange('target_roles', e.target.value.split(',').map(s => s.trim()))}
                placeholder="e.g., Software Developer, Full Stack Engineer, Backend Developer"
              />
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                These roles will be used to find matching jobs on Naukri
              </p>
            </div>
          </div>

          {/* Additional Context */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Additional Context</h3>
            <div>
              <label className="label">Additional Information</label>
              <textarea
                className="input"
                rows={4}
                value={profile.additional_context || ''}
                onChange={(e) => handleChange('additional_context', e.target.value)}
                placeholder="Any additional information about yourself..."
              />
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={handleSave}
              disabled={saving}
              className="btn btn-primary"
            >
              {saving ? 'Saving...' : 'Save Profile'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
