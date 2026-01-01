/**
 * Manus Client - TypeScript Client for Manus Architecture Visualization Service
 * 
 * This module provides a TypeScript client to communicate with the Manus Python service
 * for architecture visualization, real-time collaboration, and multi-channel rendering.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { EventEmitter } from 'events';

// ===== TYPE DEFINITIONS =====

export enum RenderChannel {
  WEB = 'web',
  XR = 'xr',
  PDF = 'pdf',
  PRESENTATION = 'presentation',
  DEV_REVIEW = 'dev_review'
}

export enum UserRole {
  ADMIN = 'admin',
  EDITOR = 'editor',
  VIEWER = 'viewer',
  COLLABORATOR = 'collaborator'
}

export enum ArchitectureLayerType {
  PRESENTATION = 'presentation',
  APPLICATION = 'application',
  DOMAIN = 'domain',
  INFRASTRUCTURE = 'infrastructure',
  DATA = 'data',
  EXTERNAL = 'external'
}

export interface ArchitectureNode {
  id?: string;
  label: string;
  layer: ArchitectureLayerType;
  description: string;
  details?: Record<string, unknown>;
  metrics?: Record<string, unknown>;
  tags?: string[];
  icon?: string;
  color?: string;
}

export interface ArchitectureEdge {
  id?: string;
  source: string;
  target: string;
  relationship: string;
  weight?: number;
  label?: string;
  description?: string;
  dataFlow?: string;
  protocol?: string;
}

export interface ArchitectureModel {
  id?: string;
  name: string;
  description: string;
  nodes?: ArchitectureNode[];
  edges?: ArchitectureEdge[];
  keyDomains?: string[];
  techStack?: Record<string, string[]>;
  version?: string;
  createdBy?: string;
  tags?: string[];
}

export interface RenderRequest {
  modelId: string;
  channel: RenderChannel;
  options?: Record<string, unknown>;
  includeMetadata?: boolean;
  includeMetrics?: boolean;
}

export interface RenderResponse {
  requestId: string;
  status: string;
  channel: RenderChannel;
  outputFormat: string;
  data: Record<string, unknown>;
  generatedAt: string;
  generationTimeMs: number;
}

export interface UserCredentials {
  username: string;
  password: string;
  email?: string;
}

export interface AuthResponse {
  user: {
    id: string;
    username: string;
    email?: string;
    role: UserRole;
  };
  token: string;
}

// ===== MANUS CLIENT CLASS =====

export class ManusClient extends EventEmitter {
  private client: AxiosInstance;
  private baseURL: string;
  private authToken: string | null = null;
  private userId: string | null = null;
  private websocketUrl: string;

  constructor(baseURL: string = 'http://localhost:8000') {
    super();
    this.baseURL = baseURL;
    this.websocketUrl = baseURL.replace('http', 'ws');
    
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add request interceptor to attach auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  // ===== AUTHENTICATION =====

  async register(credentials: UserCredentials): Promise<AuthResponse> {
    try {
      const response = await this.client.post<AuthResponse>(
        '/api/v1/auth/register',
        credentials
      );
      this.setAuth(response.data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async login(username: string, password: string): Promise<AuthResponse> {
    try {
      const response = await this.client.post<AuthResponse>(
        '/api/v1/auth/login',
        { username, password }
      );
      this.setAuth(response.data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private setAuth(response: AuthResponse): void {
    this.authToken = response.token;
    this.userId = response.user.id;
    this.emit('authenticated', response.user);
  }

  getAuthToken(): string | null {
    return this.authToken;
  }

  // ===== ARCHITECTURE MODELS =====

  async createModel(model: ArchitectureModel): Promise<ArchitectureModel> {
    try {
      const response = await this.client.post<ArchitectureModel>(
        '/api/v1/models',
        model
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getModel(modelId: string): Promise<ArchitectureModel> {
    try {
      const response = await this.client.get<ArchitectureModel>(
        `/api/v1/models/${modelId}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async listModels(tags?: string[]): Promise<ArchitectureModel[]> {
    try {
      const params = tags ? { tags: tags.join(',') } : {};
      const response = await this.client.get<ArchitectureModel[]>(
        '/api/v1/models',
        { params }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateModel(
    modelId: string,
    model: ArchitectureModel
  ): Promise<ArchitectureModel> {
    try {
      const response = await this.client.put<ArchitectureModel>(
        `/api/v1/models/${modelId}`,
        model
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteModel(modelId: string): Promise<{ id: string; status: string }> {
    try {
      const response = await this.client.delete<{ id: string; status: string }>(
        `/api/v1/models/${modelId}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getModelHistory(
    modelId: string
  ): Promise<Array<{ version: number; model: ArchitectureModel }>> {
    try {
      const response = await this.client.get<
        Array<{ version: number; model: ArchitectureModel }>
      >(`/api/v1/models/${modelId}/versions`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // ===== RENDERING =====

  async render(request: RenderRequest): Promise<RenderResponse> {
    try {
      const response = await this.client.post<RenderResponse>(
        '/api/v1/render',
        request
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getRenderFormats(): Promise<{
    channels: string[];
    formats: Record<string, string>;
  }> {
    try {
      const response = await this.client.get<{
        channels: string[];
        formats: Record<string, string>;
      }>('/api/v1/render-formats');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // ===== UTILITY =====

  async healthCheck(): Promise<{
    status: string;
    service: string;
    timestamp: string;
  }> {
    try {
      const response = await this.client.get<{
        status: string;
        service: string;
        timestamp: string;
      }>('/health');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getStats(): Promise<{
    totalModels: number;
    totalUsers: number;
    activeConnections: number;
    timestamp: string;
  }> {
    try {
      const response = await this.client.get<{
        totalModels: number;
        totalUsers: number;
        activeConnections: number;
        timestamp: string;
      }>('/api/v1/stats');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // ===== WEBSOCKET COLLABORATION =====

  connectCollaboration(
    modelId: string,
    onMessage: (message: unknown) => void,
    onError?: (error: Error) => void
  ): WebSocket {
    const ws = new WebSocket(`${this.websocketUrl}/ws/models/${modelId}`);

    ws.onopen = () => {
      this.emit('collaboration:connected', modelId);
      console.log(`Connected to collaboration channel: ${modelId}`);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        onMessage(message);
        this.emit('collaboration:message', message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (event) => {
      const error = new Error(`WebSocket error: ${event}`);
      this.emit('collaboration:error', error);
      if (onError) onError(error);
    };

    ws.onclose = () => {
      this.emit('collaboration:disconnected', modelId);
      console.log(`Disconnected from collaboration channel: ${modelId}`);
    };

    return ws;
  }

  // ===== ERROR HANDLING =====

  private handleError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      const message = axiosError.response?.data as Record<string, unknown>
        ? (axiosError.response.data as Record<string, unknown>).message
        : axiosError.message;
      return new Error(`Manus API Error: ${message || error.message}`);
    }
    return new Error(`Unexpected error: ${error}`);
  }
}

// ===== EXPORTS =====

export default ManusClient;
