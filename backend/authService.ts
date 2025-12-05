import { User } from './user';
import { generateToken, TokenPayload } from './auth';

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface LoginPayload {
  email?: string;
  username?: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  token?: string;
  user?: Omit<any, 'password_hash'>;
  error?: string;
}

export class AuthService {
  private users: Map<string, User> = new Map();

  async register(payload: RegisterPayload): Promise<AuthResponse> {
    try {
      if (!payload.email || !payload.username || !payload.password) {
        return {
          success: false,
          message: 'Missing required fields',
          error: 'email, username, and password are required'
        };
      }

      if (payload.password.length < 8) {
        return {
          success: false,
          message: 'Password too weak',
          error: 'Password must be at least 8 characters long'
        };
      }

      const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$/;
      if (!emailRegex.test(payload.email)) {
        return {
          success: false,
          message: 'Invalid email format',
          error: 'Please provide a valid email address'
        };
      }

      const passwordHash = await User.hashPassword(payload.password);
      const user = new User({
        id: this.generateId(),
        email: payload.email,
        username: payload.username,
        password_hash: passwordHash,
        first_name: payload.first_name,
        last_name: payload.last_name,
        role: 'user',
        status: 'active'
      });

      this.users.set(user.id, user);

      const tokenPayload: TokenPayload = {
        userId: user.id,
        email: user.email,
        role: user.role
      };

      const token = generateToken(tokenPayload);

      return {
        success: true,
        message: 'User registered successfully',
        token,
        user: user.getPublicData()
      };
    } catch (error: any) {
      return {
        success: false,
        message: 'Registration failed',
        error: error.message
      };
    }
  }

  async login(payload: LoginPayload): Promise<AuthResponse> {
    try {
      if (!payload.password) {
        return {
          success: false,
          message: 'Password is required',
          error: 'password is required'
        };
      }

      if (!payload.email && !payload.username) {
        return {
          success: false,
          message: 'Email or username is required',
          error: 'email or username is required'
        };
      }

      let user: User | undefined;
      if (payload.email) {
        user = Array.from(this.users.values()).find(u => u.email === payload.email);
      } else if (payload.username) {
        user = Array.from(this.users.values()).find(u => u.username === payload.username);
      }

      if (!user) {
        return {
          success: false,
          message: 'Invalid credentials',
          error: 'User not found'
        };
      }

      const isPasswordValid = await user.verifyPassword(payload.password);
      if (!isPasswordValid) {
        return {
          success: false,
          message: 'Invalid credentials',
          error: 'Password is incorrect'
        };
      }

      user.last_login = new Date();

      const tokenPayload: TokenPayload = {
        userId: user.id,
        email: user.email,
        role: user.role
      };

      const token = generateToken(tokenPayload);

      return {
        success: true,
        message: 'Login successful',
        token,
        user: user.getPublicData()
      };
    } catch (error: any) {
      return {
        success: false,
        message: 'Login failed',
        error: error.message
      };
    }
  }

  private generateId(): string {
    return 'user_' + Math.random().toString(36).substr(2, 9);
  }
}

export default new AuthService();
