import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface User {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    role: string;
    companyId: string;
    companyName: string;
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
            const response = await axios.post('/api/auth/validate', {}, {
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
            const response = await axios.post('/api/auth/login', { email, password });
            const { token, user: userData } = response.data;

            localStorage.setItem('authToken', token);
            setUser(userData);

            // Set default axios header for future requests
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } catch (error) {
            throw new Error('Login failed. Please check your credentials.');
        }
    };

    const register = async (userData: RegisterData) => {
        try {
            const response = await axios.post('/api/auth/register', userData);
            const { token, user: newUser } = response.data;

            localStorage.setItem('authToken', token);
            setUser(newUser);

            // Set default axios header for future requests
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } catch (error) {
            throw new Error('Registration failed. Please try again.');
        }
    };

    const logout = () => {
        localStorage.removeItem('authToken');
        delete axios.defaults.headers.common['Authorization'];
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