import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://skirt-unstable-hurled.ngrok-free.dev';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  role: 'doctor' | 'technical_staff';
  hospital_id: string;
  specialty?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  role: string;
  hospital_id: string;
  specialty?: string;
  created_at: string;
}

export interface PatientCreateRequest {
  full_name: string;
  date_of_birth: string;
  sex: string;
}

export interface PatientResponse {
  patient_code: string;
  id: string;
  full_name: string;
}

export interface ScanUploadResponse {
  id?: string;
  scan_id?: string;
  patient_code: string;
  ai_grade: number;
  ai_severity: string;
  ai_confidence: number;
  status: string;
}

export interface ScanResponse {
  id: string;
  patient_code: string;
  ai_grade: number;
  ai_severity: string;
  ai_confidence: number;
  status: string;
  doctor_grade?: number;
  doctor_notes?: string;
  reviewed_at?: string;
  created_at: string;
}

export interface DashboardStats {
  total_patients: number;
  reviewed_scans_count: number;
  affected_scans_count: number;
  affected_percentage: number;
  age_group_breakdown: Array<{
    group: string;
    count: number;
    percentage: number;
  }>;
  monthly_scan_counts: Array<{
    year: number;
    month: number;
    month_name: string;
    count: number;
  }>;
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add interceptor to dynamically attach token from localStorage to each request
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  setToken(token: string | null) {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  // Auth endpoints
  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/auth/login', data);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/auth/register', data);
    return response.data;
  }

  async getCurrentUser(): Promise<UserResponse> {
    const response = await this.client.get<UserResponse>('/auth/me');
    return response.data;
  }

  // Patient endpoints
  async createPatient(data: PatientCreateRequest): Promise<PatientResponse> {
    const response = await this.client.post<PatientResponse>('/patients/', data);
    return response.data;
  }

  async getPatient(patientCode: string): Promise<any> {
    const response = await this.client.get(`/patients/${patientCode}`);
    return response.data;
  }

  // Scan endpoints
  async uploadScan(patientCode: string, file: File): Promise<ScanUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<ScanUploadResponse>(
      `/scans/?patient_code=${patientCode}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async getMyScans(skip: number = 0, limit: number = 50): Promise<any> {
    const response = await this.client.get('/scans/mine', {
      params: { skip, limit },
    });
    return response.data;
  }

  async getScan(scanId: string): Promise<ScanResponse> {
    const response = await this.client.get<ScanResponse>(`/scans/${scanId}`);
    return response.data;
  }

  // Doctor endpoints
  async getScanQueue(region?: string, skip: number = 0, limit: number = 50): Promise<any> {
    const response = await this.client.get('/doctor/scans/queue', {
      params: { region, skip, limit },
    });
    return response.data;
  }

  async getScanDetail(scanId: string): Promise<any> {
    const response = await this.client.get(`/doctor/scans/${scanId}`);
    return response.data;
  }

  async submitScanReview(scanId: string, data: { doctor_grade: number; notes: string }): Promise<any> {
    const response = await this.client.post(`/doctor/scans/${scanId}/review`, data);
    return response.data;
  }

  async getPatients(skip: number = 0, limit: number = 50): Promise<any> {
    const response = await this.client.get('/patients/', {
      params: { skip, limit },
    });
    return response.data;
  }

  async getMyPatients(skip: number = 0, limit: number = 50): Promise<any> {
    const response = await this.client.get('/doctor/patients/mine', {
      params: { skip, limit },
    });
    return response.data;
  }

  async registerPatient(data: any): Promise<any> {
    const response = await this.client.post('/patients/', data);
    return response.data;
  }

  // Dashboard endpoints
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.client.get<DashboardStats>('/dashboard/stats');
    return response.data;
  }

  async getHospitalStats(): Promise<DashboardStats> {
    const response = await this.client.get<DashboardStats>('/dashboard/stats/hospital');
    return response.data;
  }

  // Public endpoints (no auth)
  async patientLookup(patientCode: string): Promise<any> {
    const response = await this.client.get(`/patient-lookup/${patientCode}`);
    return response.data;
  }
}

export default new ApiClient();
