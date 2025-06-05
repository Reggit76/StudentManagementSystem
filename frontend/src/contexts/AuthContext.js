import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const ROLES = {
  CHAIRMAN: 'CHAIRMAN',                    // Председатель профкома
  DEPUTY_CHAIRMAN: 'DEPUTY_CHAIRMAN',     // Зам председателя
  DIVISION_HEAD: 'DIVISION_HEAD',         // Председатель подразделения
  DORMITORY_HEAD: 'DORMITORY_HEAD',       // Председатель общежития
};

// Права доступа для каждой роли
export const ROLE_PERMISSIONS = {
  [ROLES.CHAIRMAN]: {
    canViewAll: true,
    canManageUsers: true,
    canManageDivision: true,
    canManageGroups: true,
    canManageStudents: true,
    canViewDormitory: true,
    canManageRoles: true,
    canDeleteAll: true,
  },
  [ROLES.DEPUTY_CHAIRMAN]: {
    canViewAll: true,
    canManageUsers: false,
    canManageDivision: true,
    canManageGroups: true,
    canManageStudents: true,
    canViewDormitory: true,
    canManageRoles: false,
    canDeleteAll: false,
  },
  [ROLES.DIVISION_HEAD]: {
    canViewAll: false,
    canManageUsers: false,
    canManageDivision: false,
    canManageGroups: true,
    canManageStudents: true,
    canViewDormitory: false,
    canManageRoles: false,
    canDeleteAll: false,
  },
  [ROLES.DORMITORY_HEAD]: {
    canViewAll: false,
    canManageUsers: false,
    canManageDivision: false,
    canManageGroups: false,
    canManageStudents: true,
    canViewDormitory: true,
    canManageRoles: false,
    canDeleteAll: false,
  },
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('token');
    if (token) {
      checkAuth();
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuth = async () => {
    try {
      const response = await authAPI.me();
      setUser(response.data);
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password);
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      
      // Получаем данные пользователя
      const userResponse = await authAPI.me();
      setUser(userResponse.data);
      
      return userResponse.data;
    } catch (error) {
      console.error('Login failed:', error);
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const hasPermission = (permission) => {
    if (!user || !user.roles) return false;
    return user.roles.some(role => ROLE_PERMISSIONS[role.name]?.[permission]);
  };

  const canAccessRoute = (requiredPermissions) => {
    if (!user) return false;
    if (!requiredPermissions) return true;
    
    return requiredPermissions.some(permission => hasPermission(permission));
  };

  const getRoleDisplayName = (roleName) => {
    const roleNames = {
      'CHAIRMAN': 'Председатель профкома',
      'DEPUTY_CHAIRMAN': 'Заместитель председателя',
      'DIVISION_HEAD': 'Председатель подразделения',
      'DORMITORY_HEAD': 'Председатель общежития'
    };
    return roleNames[roleName] || roleName;
  };

  const value = {
    user,
    loading,
    login,
    logout,
    hasPermission,
    canAccessRoute,
    getRoleDisplayName,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};