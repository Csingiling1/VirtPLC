import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api';

interface ApiError {
    isNetworkError?: boolean;
    response?: {
        status: number;
        data?: {
            message?: string;
        };
    };
    request?: unknown;
    message?: string;
}

interface User {
    id: number;
    email: string;
    firstName: string;
    lastName: string;
    role: string;
    company: {
        id: number;
        name: string;
        domain: string;
    } | null;
    manufacturer?: {
        id: number;
        name: string;
        manufacturerId: string;
    } | null;
}

interface AuthContextType {
    user: User | null;
    login: (email: string, password: string) => Promise<void>;
    register: (userData: RegisterData) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
    isLoading: boolean;
}

interface RegisterData {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
    companyName: string;
    companyDomain: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Check for existing token on app load
        const token = localStorage.getItem('authToken');
        if (token) {
            validateToken(token);
        } else {
            setIsLoading(false);
        }
    }, []);

    const validateToken = async (token: string) => {
        try {
            const response = await api.post('/api/auth/validate', {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUser(response.data.user);
        } catch (error) {
            localStorage.removeItem('authToken');
        } finally {
            setIsLoading(false);
        }
    };

    const login = async (email: string, password: string) => {
        try {
            const response = await api.post('/api/auth/login', { email, password });
            const { token, user: userData } = response.data;

            localStorage.setItem('authToken', token);
            setUser(userData);

            // Set default axios header for future requests
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } catch (error: unknown) {
            console.error('Login error:', error);

            // Handle different types of errors
            const err = error as ApiError;

            if (err.isNetworkError) {
                throw new Error('Cannot connect to the server. Please check your internet connection and ensure the backend is running.');
            }

            if (err.response) {
                // Server responded with error status
                const status = err.response.status;
                const data = err.response.data;

                switch (status) {
                    case 400:
                        throw new Error(data?.message || 'Invalid email or password format.');
                    case 401:
                        throw new Error('Invalid email or password. Please check your credentials.');
                    case 403:
                        throw new Error('Account is disabled or access is forbidden.');
                    case 404:
                        throw new Error('Authentication service not found. Please contact support.');
                    case 429:
                        throw new Error('Too many login attempts. Please try again later.');
                    case 500:
                        throw new Error('Server error. Please try again later or contact support.');
                    default:
                        throw new Error(data?.message || `Login failed with status ${status}.`);
                }
            } else if (err.request) {
                // Network error (CORS, no response, etc.)
                throw new Error('Network error: Cannot reach the authentication server. This might be a CORS issue or the server is down.');
            } else {
                // Other error
                throw new Error('An unexpected error occurred during login.');
            }
        }
    };

    const register = async (userData: RegisterData) => {
        try {
            const response = await api.post('/api/auth/register', userData);
            const { token, user: newUser } = response.data;

            localStorage.setItem('authToken', token);
            setUser(newUser);

            // Set default axios header for future requests
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } catch (error: unknown) {
            console.error('Registration error:', error);

            // Handle different types of errors
            const err = error as ApiError;

            if (err.isNetworkError) {
                throw new Error('Cannot connect to the server. Please check your internet connection and ensure the backend is running.');
            }

            if (err.response) {
                // Server responded with error status
                const status = err.response.status;
                const data = err.response.data;

                switch (status) {
                    case 400:
                        throw new Error(data?.message || 'Invalid registration data. Please check all fields.');
                    case 409:
                        throw new Error('Email already exists. Please use a different email address.');
                    case 422:
                        throw new Error(data?.message || 'Validation failed. Please check your input.');
                    case 500:
                        throw new Error('Server error during registration. Please try again later.');
                    default:
                        throw new Error(data?.message || `Registration failed with status ${status}.`);
                }
            } else if (err.request) {
                // Network error (CORS, no response, etc.)
                throw new Error('Network error: Cannot reach the registration server. This might be a CORS issue or the server is down.');
            } else {
                // Other error
                throw new Error('An unexpected error occurred during registration.');
            }
        }
    };

    const logout = () => {
        localStorage.removeItem('authToken');
        delete api.defaults.headers.common['Authorization'];
        setUser(null);
    };

    const value: AuthContextType = {
        user,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        isLoading,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};