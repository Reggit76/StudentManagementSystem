import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Typography,
  Box,
  Toolbar,
  AppBar,
} from '@mui/material';
import {
  People as PeopleIcon,
  Group as GroupIcon,
  Business as BusinessIcon,
  Apartment as ApartmentIcon,
  Payment as PaymentIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const drawerWidth = 240;

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, hasPermission, getRoleDisplayName } = useAuth();

  const menuItems = [
    {
      text: 'Students',
      icon: <PeopleIcon />,
      path: '/students',
      permission: null,
    },
    {
      text: 'Groups',
      icon: <GroupIcon />,
      path: '/groups',
      permission: 'canManageGroups',
    },
    {
      text: 'Divisions',
      icon: <BusinessIcon />,
      path: '/divisions',
      permission: 'canManageDivision',
    },
    {
      text: 'Hostels',
      icon: <ApartmentIcon />,
      path: '/hostels',
      permission: 'canViewDormitory',
    },
    {
      text: 'Contributions',
      icon: <PaymentIcon />,
      path: '/contributions',
      permission: 'canManageStudents',
    },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <>
      <AppBar
        position="fixed"
        sx={{
          width: `calc(100% - ${drawerWidth}px)`,
          ml: `${drawerWidth}px`,
        }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            Student Union Management
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
        variant="permanent"
        anchor="left"
      >
        <Toolbar>
          <Typography variant="h6" noWrap>
            Menu
          </Typography>
        </Toolbar>
        <Divider />
        <List>
          {menuItems.map((item) => {
            if (item.permission && !hasPermission(item.permission)) {
              return null;
            }
            return (
              <ListItem
                button
                key={item.text}
                onClick={() => navigate(item.path)}
                selected={location.pathname === item.path}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItem>
            );
          })}
        </List>
        <Divider />
        <Box sx={{ mt: 'auto', mb: 2 }}>
          <List>
            <ListItem>
              <ListItemText
                primary={user.login}
                secondary={user.roles.map(role => getRoleDisplayName(role.name)).join(', ')}
              />
            </ListItem>
            <ListItem button onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon />
              </ListItemIcon>
              <ListItemText primary="Logout" />
            </ListItem>
          </List>
        </Box>
      </Drawer>
      <Toolbar />
    </>
  );
};

export default Navigation;