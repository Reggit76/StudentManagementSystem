import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

import { AuthProvider, useAuth } from './contexts/AuthContext';
import theme from './theme';
import Navigation from './components/Navigation';
import Login from './pages/Login';
import Students from './pages/Students';
import Groups from './pages/Groups';
import Divisions from './pages/Divisions';
import Hostels from './pages/Hostels';
import Contributions from './pages/Contributions';
import Users from './pages/Users';
import AuditLogs from './pages/AuditLogs';

const PrivateRoute = ({ children, requiredPermissions = [] }) => {
  const { user, loading, canAccessRoute } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (requiredPermissions.length > 0 && !canAccessRoute(requiredPermissions)) {
    return <Navigate to="/" />;
  }

  return children;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Navigate to="/students" />
          </PrivateRoute>
        }
      />

      <Route
        path="/students"
        element={
          <PrivateRoute>
            <Students />
          </PrivateRoute>
        }
      />

      <Route
        path="/groups"
        element={
          <PrivateRoute requiredPermissions={['canManageGroups']}>
            <Groups />
          </PrivateRoute>
        }
      />

      <Route
        path="/divisions"
        element={
          <PrivateRoute requiredPermissions={['canManageSubdivision']}>
            <Divisions />
          </PrivateRoute>
        }
      />

      <Route
        path="/hostels"
        element={
          <PrivateRoute requiredPermissions={['canViewDormitory']}>
            <Hostels />
          </PrivateRoute>
        }
      />

      <Route
        path="/contributions"
        element={
          <PrivateRoute requiredPermissions={['canManageStudents']}>
            <Contributions />
          </PrivateRoute>
        }
      />

      <Route
        path="/users"
        element={
          <PrivateRoute requiredPermissions={['canManageUsers']}>
            <Users />
          </PrivateRoute>
        }
      />

      <Route
        path="/logs"
        element={
          <PrivateRoute requiredPermissions={['canViewAll']}>
            <AuditLogs />
          </PrivateRoute>
        }
      />
    </Routes>
  );
};

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Box sx={{ display: 'flex' }}>
            <Navigation />
            <Box
              component="main"
              sx={{
                flexGrow: 1,
                height: '100vh',
                overflow: 'auto',
                backgroundColor: (theme) =>
                  theme.palette.mode === 'light'
                    ? theme.palette.grey[100]
                    : theme.palette.grey[900],
              }}
            >
              <AppRoutes />
            </Box>
          </Box>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;