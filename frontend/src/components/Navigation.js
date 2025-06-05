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
  AdminPanelSettings as AdminIcon,
  History as HistoryIcon,
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
      text: 'Студенты',
      icon: <PeopleIcon />,
      path: '/students',
      permission: null,
    },
    {
      text: 'Группы',
      icon: <GroupIcon />,
      path: '/groups',
      permission: 'canManageGroups',
    },
    {
      text: 'Подразделения',
      icon: <BusinessIcon />,
      path: '/divisions',
      permission: 'canManageSubdivision',
    },
    {
      text: 'Общежития',
      icon: <ApartmentIcon />,
      path: '/hostels',
      permission: 'canViewDormitory',
    },
    {
      text: 'Взносы',
      icon: <PaymentIcon />,
      path: '/contributions',
      permission: 'canManageStudents',
    },
  ];

  // Админ-пункты меню
  const adminMenuItems = [
    {
      text: 'Пользователи',
      icon: <AdminIcon />,
      path: '/users',
      permission: 'canManageUsers',
    },
    {
      text: 'Журнал действий',
      icon: <HistoryIcon />,
      path: '/logs',
      permission: 'canViewAll',
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
            Управление профсоюзом студентов
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
            Меню
          </Typography>
        </Toolbar>
        <Divider />
        
        {/* Основные пункты меню */}
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

        {/* Админ-раздел */}
        {adminMenuItems.some(item => !item.permission || hasPermission(item.permission)) && (
          <>
            <Divider />
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Администрирование
              </Typography>
            </Box>
            <List>
              {adminMenuItems.map((item) => {
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
          </>
        )}

        <Divider />
        <Box sx={{ mt: 'auto', mb: 2 }}>
          <List>
            <ListItem>
              <ListItemText
                primary={user.login}
                secondary={user.roles && user.roles.length > 0 
                  ? user.roles.map(role => getRoleDisplayName(role.name)).join(', ')
                  : 'Нет ролей'
                }
              />
            </ListItem>
            <ListItem button onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon />
              </ListItemIcon>
              <ListItemText primary="Выйти" />
            </ListItem>
          </List>
        </Box>
      </Drawer>
      <Toolbar />
    </>
  );
};

export default Navigation;