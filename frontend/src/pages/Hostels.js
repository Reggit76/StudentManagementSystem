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
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { studentsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Hostels = () => {
  const { hasPermission } = useAuth();
  const [hostelStudents, setHostelStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });

  useEffect(() => {
    fetchHostelStudents();
  }, []);

  const fetchHostelStudents = async () => {
    setLoading(true);
    try {
      const response = await studentsAPI.getAll({ hostel: true });
      setHostelStudents(response.data);
    } catch (err) {
      setError('Failed to load hostel students');
    } finally {
      setLoading(false);
    }
  };

  const handleAddHostelStudent = () => {
    setDialog({
      open: true,
      type: 'add',
      data: {
        RoomNumber: '',
        Block: '',
        CheckInDate: new Date().toISOString().split('T')[0],
        Notes: '',
      },
    });
  };

  const handleEditHostelStudent = (student) => {
    setDialog({
      open: true,
      type: 'edit',
      data: {
        ...student.HostelData,
        StudentID: student.ID,
      },
    });
  };

  const handleDeleteHostelStudent = async (id) => {
    if (window.confirm('Are you sure you want to remove this student from the hostel?')) {
      try {
        await studentsAPI.delete(`${id}/hostel`);
        fetchHostelStudents();
      } catch (err) {
        setError('Failed to remove student from hostel');
      }
    }
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
  };

  const handleDialogSave = async () => {
    try {
      if (dialog.type === 'add') {
        await studentsAPI.create('hostel', dialog.data);
      } else {
        await studentsAPI.update(`${dialog.data.StudentID}/hostel`, dialog.data);
      }
      handleDialogClose();
      fetchHostelStudents();
    } catch (err) {
      setError('Failed to save hostel student');
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
          Hostel Students
        </Typography>
        {hasPermission('canViewDormitory') && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAddHostelStudent}
          >
            Add Hostel Student
          </Button>
        )}
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
              <TableCell>Student Name</TableCell>
              <TableCell>Group</TableCell>
              <TableCell>Room</TableCell>
              <TableCell>Block</TableCell>
              <TableCell>Check-in Date</TableCell>
              <TableCell>Notes</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : hostelStudents.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No hostel students found
                </TableCell>
              </TableRow>
            ) : (
              hostelStudents.map((student) => (
                <TableRow key={student.ID}>
                  <TableCell>{student.FullName}</TableCell>
                  <TableCell>{student.Group?.Name}</TableCell>
                  <TableCell>{student.HostelData?.RoomNumber}</TableCell>
                  <TableCell>{student.HostelData?.Block}</TableCell>
                  <TableCell>
                    {new Date(student.HostelData?.CheckInDate).toLocaleDateString()}
                  </TableCell>
                  <TableCell>{student.HostelData?.Notes}</TableCell>
                  <TableCell align="right">
                    {hasPermission('canViewDormitory') && (
                      <>
                        <IconButton
                          color="primary"
                          onClick={() => handleEditHostelStudent(student)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          color="error"
                          onClick={() => handleDeleteHostelStudent(student.ID)}
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
          {dialog.type === 'add' ? 'Add New Hostel Student' : 'Edit Hostel Student'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 2 }}>
            {dialog.type === 'add' && (
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Student</InputLabel>
                <Select
                  name="StudentID"
                  value={dialog.data?.StudentID || ''}
                  onChange={handleInputChange}
                  label="Student"
                  required
                >
                  {/* Add student options here */}
                </Select>
              </FormControl>
            )}
            <TextField
              fullWidth
              label="Room Number"
              name="RoomNumber"
              value={dialog.data?.RoomNumber || ''}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Block"
              name="Block"
              value={dialog.data?.Block || ''}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Check-in Date"
              name="CheckInDate"
              type="date"
              value={dialog.data?.CheckInDate || ''}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              fullWidth
              label="Notes"
              name="Notes"
              value={dialog.data?.Notes || ''}
              onChange={handleInputChange}
              multiline
              rows={4}
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

export default Hostels; 