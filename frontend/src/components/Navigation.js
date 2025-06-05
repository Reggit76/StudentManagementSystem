import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Button,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
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
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, hasPermission, getRoleDisplayName } = useAuth();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

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

  const drawer = (
    <>
      <Toolbar />
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
    </>
  );

  return (
    <>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          zIndex: 1100,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Управление профсоюзом студентов
          </Typography>
          <Button color="inherit" onClick={handleLogout} startIcon={<LogoutIcon />}>
            Выйти
          </Button>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              zIndex: 1200,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              zIndex: 1000,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
    </>
  );
};

export default Navigation;