import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Grid,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import InputAdornment from '@mui/material/InputAdornment';
import { groupsAPI, subdivisionsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Groups = () => {
  const { hasPermission } = useAuth();
  const [groups, setGroups] = useState([]);
  const [subdivisions, setSubdivisions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });
  
  // Фильтры
  const [filters, setFilters] = useState({
    subdivision_id: '',
    year: '',
    search: '',
  });

  useEffect(() => {
    fetchSubdivisions();
    fetchGroups();
  }, []);

  useEffect(() => {
    // Перезагружаем группы при изменении фильтров
    const timeoutId = setTimeout(() => {
      fetchGroups();
    }, 300); // Debounce для поиска

    return () => clearTimeout(timeoutId);
  }, [filters]);

  const fetchGroups = async () => {
    setLoading(true);
    setError('');
    try {
      // Формируем параметры запроса
      const params = {};
      if (filters.subdivision_id) params.subdivision_id = filters.subdivision_id;
      if (filters.year) params.year = filters.year;
      if (filters.search) params.search = filters.search;

      const response = await groupsAPI.getAll(params);
      const groupsData = response.data;
      
      if (groupsData && groupsData.items) {
        // Если ответ пагинированный
        setGroups(groupsData.items);
      } else if (Array.isArray(groupsData)) {
        // Если ответ - простой массив
        setGroups(groupsData);
      } else {
        console.error('Unexpected groups data format:', groupsData);
        setGroups([]);
        setError('Некорректный формат данных групп');
      }
    } catch (err) {
      console.error('Failed to load groups:', err);
      setError('Не удалось загрузить группы');
      setGroups([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubdivisions = async () => {
    try {
      const response = await subdivisionsAPI.getAll();
      const subdivisionsData = response.data;
      
      if (subdivisionsData && subdivisionsData.items) {
        setSubdivisions(subdivisionsData.items);
      } else if (Array.isArray(subdivisionsData)) {
        setSubdivisions(subdivisionsData);
      } else {
        console.error('Unexpected subdivisions data format:', subdivisionsData);
        setSubdivisions([]);
      }
    } catch (err) {
      console.error('Failed to load subdivisions:', err);
      setSubdivisions([]);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      subdivision_id: '',
      year: '',
      search: '',
    });
  };

  const handleAddGroup = () => {
    setDialog({
      open: true,
      type: 'add',
      data: { 
        name: '', 
        subdivision_id: filters.subdivision_id || '', 
        year: filters.year || new Date().getFullYear() 
      },
    });
  };

  const handleEditGroup = (group) => {
    setDialog({
      open: true,
      type: 'edit',
      data: {
        ...group,
        subdivision_id: group.subdivisionid || group.subdivision_id
      },
    });
  };

  const handleDeleteGroup = async (id) => {
    if (window.confirm('Are you sure you want to delete this group?')) {
      try {
        await groupsAPI.delete(id);
        fetchGroups();
      } catch (err) {
        console.error('Failed to delete group:', err);
        setError('Failed to delete group');
      }
    }
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
  };

  const handleDialogSave = async () => {
    try {
      if (dialog.type === 'add') {
        await groupsAPI.create(dialog.data);
      } else {
        await groupsAPI.update(dialog.data.id, dialog.data);
      }
      handleDialogClose();
      fetchGroups();
    } catch (err) {
      console.error('Failed to save group:', err);
      setError('Failed to save group');
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setDialog(prev => ({
      ...prev,
      data: { ...prev.data, [name]: value },
    }));
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Groups
        </Typography>
        {hasPermission('canManageGroups') && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAddGroup}
          >
            Add Group
          </Button>
        )}
      </Box>

      {/* Фильтры */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={3}>
            <TextField
              fullWidth
              size="small"
              label="Search groups"
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Subdivision</InputLabel>
              <Select
                value={filters.subdivision_id}
                label="Subdivision"
                onChange={(e) => handleFilterChange('subdivision_id', e.target.value)}
              >
                <MenuItem value="">All Subdivisions</MenuItem>
                {subdivisions.map((subdivision) => (
                  <MenuItem key={subdivision.id} value={subdivision.id}>
                    {subdivision.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField
              fullWidth
              size="small"
              label="Year"
              type="number"
              value={filters.year}
              onChange={(e) => handleFilterChange('year', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <Button
              variant="outlined"
              startIcon={<ClearIcon />}
              onClick={clearFilters}
              fullWidth
            >
              Clear Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Subdivision</TableCell>
              <TableCell>Year</TableCell>
              <TableCell>Students</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : groups.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No groups found
                </TableCell>
              </TableRow>
            ) : (
              groups.map((group) => (
                <TableRow key={group.id}>
                  <TableCell>{group.name}</TableCell>
                  <TableCell>
                    {group.subdivision_name || 
                     subdivisions.find(s => s.id === (group.subdivisionid || group.subdivision_id))?.name || 
                     '-'}
                  </TableCell>
                  <TableCell>{group.year}</TableCell>
                  <TableCell>{group.students_count || 0}</TableCell>
                  <TableCell align="right">
                    {hasPermission('canManageGroups') && (
                      <>
                        <IconButton
                          color="primary"
                          onClick={() => handleEditGroup(group)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          color="error"
                          onClick={() => handleDeleteGroup(group.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialog.open} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialog.type === 'add' ? 'Add New Group' : 'Edit Group'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Name"
              name="name"
              value={dialog.data?.name || ''}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Subdivision</InputLabel>
              <Select
                name="subdivision_id"
                value={dialog.data?.subdivision_id || ''}
                onChange={handleInputChange}
                label="Subdivision"
                required
              >
                {subdivisions.map((subdivision) => (
                  <MenuItem key={subdivision.id} value={subdivision.id}>
                    {subdivision.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Year"
              name="year"
              type="number"
              value={dialog.data?.year || new Date().getFullYear()}
              onChange={handleInputChange}
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button onClick={handleDialogSave} color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Groups;