import { useState } from 'react';
import apiService from '../services/api';
import type { ParsedResumeData, Profile } from '../types';
import { Upload, FileText, Check, X } from 'lucide-react';
import { toast } from 'react-toastify';

const Resume = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [parsedData, setParsedData] = useState<ParsedResumeData | null>(null);
  const [editing, setEditing] = useState(false);
  const [editedData, setEditedData] = useState<Partial<Profile>>({});

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    try {
      const response = await apiService.uploadResume(file);
      setParsedData(response.resume_data);
      setEditedData(mapParsedToProfile(response.resume_data));
      toast.success('Resume uploaded and parsed successfully!');
    } catch (error) {
      toast.error('Failed to upload resume: ' + error);
    } finally {
      setUploading(false);
    }
  };

  const mapParsedToProfile = (parsed: ParsedResumeData): Partial<Profile> => {
    return {
      full_name: parsed.full_name,
      email: parsed.email,
      phone: parsed.phone,
      current_city: parsed.location,
      linkedin: parsed.linkedin,
      github: parsed.github,
      portfolio: parsed.portfolio,
      skills: parsed.skills || [],
      total_experience_years: parsed.experience?.total_years || 0,
      target_roles: parsed.target_roles || [],
      education: parsed.education,
    };
  };

  const handleApprove = async () => {
    try {
      await apiService.approveResumeData({
        approved_data: editedData,
        resume_filename: file?.name
      });
      toast.success('Resume data approved and profile updated!');
      setParsedData(null);
      setFile(null);
      // Emit event to notify other pages
      window.dispatchEvent(new CustomEvent('resume-approved'));
    } catch (error) {
      toast.error('Failed to approve data: ' + error);
    }
  };

  const handleReject = () => {
    setParsedData(null);
    setFile(null);
  };

  return (
    <div className="p-8 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-4xl font-bold gradient-text text-shadow-lg">Resume</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2 text-lg">Upload and parse your resume</p>
      </div>

      {!parsedData ? (
        <div className="card-gradient max-w-2xl animate-slide-up">
          <div className="border-2 border-dashed border-blue-300 dark:border-blue-700 rounded-2xl p-12 text-center bg-gradient-to-br from-blue-50/50 to-indigo-50/50 dark:from-blue-900/20 dark:to-indigo-900/20 hover:border-blue-400 dark:hover:border-blue-600 transition-all duration-300">
            <div className="p-4 bg-blue-100 dark:bg-blue-900/30 rounded-xl inline-block mb-4">
              <Upload className="w-16 h-16 mx-auto text-blue-600 dark:text-blue-400" />
            </div>
            <p className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Drag & drop your resume here
            </p>
            <p className="text-gray-600 dark:text-gray-400 mb-6">or click to browse</p>
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFileSelect}
              className="hidden"
              id="resume-upload"
            />
            <label
              htmlFor="resume-upload"
              className="btn btn-primary cursor-pointer"
            >
              Browse Files
            </label>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-4">
              Supported formats: PDF, DOC, DOCX
            </p>
          </div>

          {file && (
            <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg mr-3">
                    <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <span className="font-semibold text-gray-900 dark:text-white">{file.name}</span>
                </div>
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="btn btn-primary"
                >
                  {uploading ? 'Uploading...' : 'Upload & Parse'}
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="card-gradient max-w-4xl animate-slide-up">
          <div className="mb-6">
            <h3 className="text-2xl font-bold gradient-text">Review Extracted Information</h3>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Review and edit the extracted information before saving</p>
          </div>

          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Full Name</label>
                <input
                  type="text"
                  className="input"
                  value={editedData.full_name || ''}
                  onChange={(e) => setEditedData({ ...editedData, full_name: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Email</label>
                <input
                  type="email"
                  className="input"
                  value={editedData.email || ''}
                  onChange={(e) => setEditedData({ ...editedData, email: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Phone</label>
                <input
                  type="tel"
                  className="input"
                  value={editedData.phone || ''}
                  onChange={(e) => setEditedData({ ...editedData, phone: e.target.value })}
                />
              </div>
              <div>
                <label className="label">Current City</label>
                <input
                  type="text"
                  className="input"
                  value={editedData.current_city || ''}
                  onChange={(e) => setEditedData({ ...editedData, current_city: e.target.value })}
                />
              </div>
              <div>
                <label className="label">LinkedIn</label>
                <input
                  type="url"
                  className="input"
                  value={editedData.linkedin || ''}
                  onChange={(e) => setEditedData({ ...editedData, linkedin: e.target.value })}
                />
              </div>
              <div>
                <label className="label">GitHub</label>
                <input
                  type="url"
                  className="input"
                  value={editedData.github || ''}
                  onChange={(e) => setEditedData({ ...editedData, github: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="label">Skills</label>
              <input
                type="text"
                className="input"
                value={editedData.skills?.join(', ') || ''}
                onChange={(e) => setEditedData({
                  ...editedData,
                  skills: e.target.value.split(',').map(s => s.trim())
                })}
              />
            </div>

            <div>
              <label className="label">Target Roles (Job Titles)</label>
              <input
                type="text"
                className="input"
                value={editedData.target_roles?.join(', ') || ''}
                onChange={(e) => setEditedData({
                  ...editedData,
                  target_roles: e.target.value.split(',').map(s => s.trim())
                })}
                placeholder="e.g., Software Developer, Full Stack Engineer, Backend Developer"
              />
              <p className="text-sm text-gray-500 mt-1">
                These roles will be used to find matching jobs on Naukri
              </p>
            </div>

            <div>
              <label className="label">Total Experience (Years)</label>
              <input
                type="number"
                className="input"
                value={editedData.total_experience_years || 0}
                onChange={(e) => setEditedData({
                  ...editedData,
                  total_experience_years: parseInt(e.target.value)
                })}
              />
            </div>

            <div className="flex justify-end space-x-4 mt-8">
              <button
                onClick={handleReject}
                className="btn btn-secondary"
              >
                <X className="w-4 h-4 mr-2 inline" />
                Reject
              </button>
              <button
                onClick={handleApprove}
                className="btn btn-success"
              >
                <Check className="w-4 h-4 mr-2 inline" />
                Approve & Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Resume;
