export interface Profile {
  full_name?: string;
  email?: string;
  phone?: string;
  current_city?: string;
  preferred_locations?: string[];
  linkedin?: string;
  github?: string;
  portfolio?: string;
  education?: {
    degree?: string;
    field?: string;
    institution?: string;
    year?: string;
  };
  target_roles?: string[];
  skills?: string[];
  total_experience_years?: number;
  notice_period_days?: number;
  current_ctc_lpa?: number;
  expected_ctc_lpa?: number;
  currently_employed?: boolean;
  current_company?: string;
  current_role?: string;
  relocate_cities?: boolean;
  night_shift_ok?: boolean;
  weekend_ok?: boolean;
  immediately_available?: boolean;
  additional_context?: string;
}

export interface SessionStatus {
  success: boolean;
  connected: boolean;
  session_id?: string;
  created_at?: string;
  expires_at?: string;
  time_remaining_seconds?: number;
  time_remaining_hours?: number;
  message?: string;
}

export interface ParsedResumeData {
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  portfolio?: string;
  education?: {
    degree?: string;
    university?: string;
    year?: string;
    field?: string;
  };
  skills?: string[];
  experience?: {
    total_years: number;
    companies: string[];
    job_titles: string[];
  };
  certifications?: string[];
  target_roles?: string[];
}

export interface Application {
  timestamp: string;
  source: string;
  title: string;
  company: string;
  status: string;
  reason?: string;
  error_category?: string;
}

export interface Statistics {
  total_seen: number;
  total_qualified: number;
  total_filtered: number;
  total_applied: number;
  total_skipped: number;
  total_errors: number;
  total_uncertain: number;
  total_duplicates_skipped: number;
  total_security_stops: number;
  by_role: Record<string, any>;
  by_company: Record<string, number>;
  by_error_category: Record<string, number>;
  by_skip_reason: Record<string, number>;
  success_rate: number;
  duration_seconds: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
