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
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  TextField,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import InputAdornment from '@mui/material/InputAdornment';
import { studentsAPI, groupsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import StudentForm from '../components/StudentForm';

const Students = () => {
  const { user, hasPermission } = useAuth();
  const [students, setStudents] = useState([]);
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });

  useEffect(() => {
    fetchGroups();
    fetchStudents();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await groupsAPI.getAll();
      setGroups(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error('Failed to load groups:', err);
      setGroups([]);
    }
  };

  const fetchStudents = async (params = {}) => {
    setLoading(true);
    setError('');
    try {
      const queryParams = {
        group_id: selectedGroup || undefined,
        search: searchTerm || undefined,
        ...params,
      };
      
      // Убираем пустые параметры
      Object.keys(queryParams).forEach(key => {
        if (queryParams[key] === undefined || queryParams[key] === '') {
          delete queryParams[key];
        }
      });

      const response = await studentsAPI.getAll(queryParams);
      const studentsData = response.data;
      
      // Проверяем, что получили массив
      if (Array.isArray(studentsData)) {
        setStudents(studentsData);
      } else {
        console.error('Expected array, got:', studentsData);
        setStudents([]);
        setError('Некорректный формат данных от сервера');
      }
    } catch (err) {
      console.error('Failed to load students:', err);
      setError('Не удалось загрузить список студентов');
      setStudents([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddStudent = () => {
    setDialog({
      open: true,
      type: 'add',
      data: {
        group_id: selectedGroup || '',
        full_name: '',
        is_active: false,
        is_budget: true,
        year: new Date().getFullYear(),
      },
    });
  };

  const handleEditStudent = (student) => {
    setDialog({
      open: true,
      type: 'edit',
      data: student,
    });
  };

  const handleDeleteStudent = async (id) => {
    if (window.confirm('Are you sure you want to delete this student?')) {
      try {
        await studentsAPI.delete(id);
        fetchStudents();
      } catch (err) {
        setError('Failed to delete student');
      }
    }
  };

  const handleGroupChange = (event) => {
    setSelectedGroup(event.target.value);
    setTimeout(() => fetchStudents({ group_id: event.target.value }), 100);
  };

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
    setTimeout(() => fetchStudents({ search: event.target.value }), 300);
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
  };

  const handleDialogSave = async (formData) => {
    try {
      if (dialog.type === 'add') {
        await studentsAPI.create(formData);
      } else {
        await studentsAPI.update(dialog.data.id, formData);
      }
      handleDialogClose();
      fetchStudents();
    } catch (err) {
      setError('Failed to save student');
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Students
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            size="small"
            placeholder="Search students..."
            value={searchTerm}
            onChange={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel id="group-select-label">Group</InputLabel>
            <Select
              labelId="group-select-label"
              value={selectedGroup}
              label="Group"
              onChange={handleGroupChange}
              size="small"
            >
              <MenuItem value="">All Groups</MenuItem>
              {groups.map((group) => (
                <MenuItem key={group.id} value={group.id}>
                  {group.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          {hasPermission('canManageStudents') && (
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleAddStudent}
            >
              Add Student
            </Button>
          )}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Full Name</TableCell>
              <TableCell>Group</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Budget</TableCell>
              <TableCell>Year</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : students.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  No students found
                </TableCell>
              </TableRow>
            ) : (
              students.map((student) => (
                <TableRow key={student.id}>
                  <TableCell>{student.full_name || student.fullname}</TableCell>
                  <TableCell>{student.group_name}</TableCell>
                  <TableCell>
                    <Chip
                      label={student.is_active || student.isactive ? 'Active' : 'Inactive'}
                      color={student.is_active || student.isactive ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={student.is_budget || student.isbudget ? 'Budget' : 'Contract'}
                      color={student.is_budget || student.isbudget ? 'primary' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{student.year}</TableCell>
                  <TableCell align="right">
                    {hasPermission('canManageStudents') && (
                      <>
                        <IconButton
                          color="primary"
                          onClick={() => handleEditStudent(student)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          color="error"
                          onClick={() => handleDeleteStudent(student.id)}
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

      {/* Student Form Dialog */}
      <Dialog open={dialog.open} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialog.type === 'add' ? 'Add New Student' : 'Edit Student'}
        </DialogTitle>
        <DialogContent>
          {dialog.open && (
            <StudentForm
              data={dialog.data}
              groups={groups}
              onSubmit={handleDialogSave}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Students;