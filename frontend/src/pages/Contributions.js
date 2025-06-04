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

const Contributions = () => {
  const { hasPermission } = useAuth();
  const [contributions, setContributions] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });

  useEffect(() => {
    fetchContributions();
    fetchStudents();
  }, []);

  const fetchContributions = async () => {
    setLoading(true);
    try {
      const response = await studentsAPI.getAll({ contributions: true });
      setContributions(response.data);
    } catch (err) {
      setError('Failed to load contributions');
    } finally {
      setLoading(false);
    }
  };

  const fetchStudents = async () => {
    try {
      const response = await studentsAPI.getAll();
      setStudents(response.data);
    } catch (err) {
      setError('Failed to load students');
    }
  };

  const handleAddContribution = () => {
    setDialog({
      open: true,
      type: 'add',
      data: {
        StudentID: '',
        Amount: '',
        PaymentDate: new Date().toISOString().split('T')[0],
        Period: new Date().getFullYear(),
        Notes: '',
      },
    });
  };

  const handleEditContribution = (contribution) => {
    setDialog({
      open: true,
      type: 'edit',
      data: contribution,
    });
  };

  const handleDeleteContribution = async (id) => {
    if (window.confirm('Are you sure you want to delete this contribution?')) {
      try {
        await studentsAPI.delete(`${id}/contributions`);
        fetchContributions();
      } catch (err) {
        setError('Failed to delete contribution');
      }
    }
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
  };

  const handleDialogSave = async () => {
    try {
      if (dialog.type === 'add') {
        await studentsAPI.create('contributions', dialog.data);
      } else {
        await studentsAPI.update(`${dialog.data.StudentID}/contributions/${dialog.data.ID}`, dialog.data);
      }
      handleDialogClose();
      fetchContributions();
    } catch (err) {
      setError('Failed to save contribution');
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
          Contributions
        </Typography>
        {hasPermission('canManageStudents') && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAddContribution}
          >
            Add Contribution
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
              <TableCell>Amount</TableCell>
              <TableCell>Payment Date</TableCell>
              <TableCell>Period</TableCell>
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
            ) : contributions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No contributions found
                </TableCell>
              </TableRow>
            ) : (
              contributions.map((contribution) => (
                <TableRow key={contribution.ID}>
                  <TableCell>{contribution.Student?.FullName}</TableCell>
                  <TableCell>{contribution.Student?.Group?.Name}</TableCell>
                  <TableCell>{contribution.Amount}</TableCell>
                  <TableCell>
                    {new Date(contribution.PaymentDate).toLocaleDateString()}
                  </TableCell>
                  <TableCell>{contribution.Period}</TableCell>
                  <TableCell>{contribution.Notes}</TableCell>
                  <TableCell align="right">
                    {hasPermission('canManageStudents') && (
                      <>
                        <IconButton
                          color="primary"
                          onClick={() => handleEditContribution(contribution)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          color="error"
                          onClick={() => handleDeleteContribution(contribution.ID)}
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
          {dialog.type === 'add' ? 'Add New Contribution' : 'Edit Contribution'}
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
                  {students.map((student) => (
                    <MenuItem key={student.ID} value={student.ID}>
                      {student.FullName} ({student.Group?.Name})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
            <TextField
              fullWidth
              label="Amount"
              name="Amount"
              type="number"
              value={dialog.data?.Amount || ''}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Payment Date"
              name="PaymentDate"
              type="date"
              value={dialog.data?.PaymentDate || ''}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              fullWidth
              label="Period"
              name="Period"
              type="number"
              value={dialog.data?.Period || new Date().getFullYear()}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
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

export default Contributions; 