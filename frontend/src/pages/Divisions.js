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
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { divisionsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Divisions = () => {
  const { hasPermission } = useAuth();
  const [divisions, setDivisions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });

  useEffect(() => {
    fetchDivisions();
  }, []);

  const fetchDivisions = async () => {
    setLoading(true);
    try {
      const response = await divisionsAPI.getAll();
      setDivisions(response.data);
    } catch (err) {
      setError('Failed to load divisions');
    } finally {
      setLoading(false);
    }
  };

  const handleAddDivision = () => {
    setDialog({
      open: true,
      type: 'add',
      data: { Name: '', Description: '' },
    });
  };

  const handleEditDivision = (division) => {
    setDialog({
      open: true,
      type: 'edit',
      data: division,
    });
  };

  const handleDeleteDivision = async (id) => {
    if (window.confirm('Are you sure you want to delete this division?')) {
      try {
        await divisionsAPI.delete(id);
        fetchDivisions();
      } catch (err) {
        setError('Failed to delete division');
      }
    }
  };

  const handleDialogClose = () => {
    setDialog({ open: false, type: null, data: null });
  };

  const handleDialogSave = async () => {
    try {
      if (dialog.type === 'add') {
        await divisionsAPI.create(dialog.data);
      } else {
        await divisionsAPI.update(dialog.data.ID, dialog.data);
      }
      handleDialogClose();
      fetchDivisions();
    } catch (err) {
      setError('Failed to save division');
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
          Divisions
        </Typography>
        {hasPermission('canManageDivision') && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAddDivision}
          >
            Add Division
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
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : divisions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={3} align="center">
                  No divisions found
                </TableCell>
              </TableRow>
            ) : (
              divisions.map((division) => (
                <TableRow key={division.ID}>
                  <TableCell>{division.Name}</TableCell>
                  <TableCell>{division.Description}</TableCell>
                  <TableCell align="right">
                    {hasPermission('canManageDivision') && (
                      <>
                        <IconButton
                          color="primary"
                          onClick={() => handleEditDivision(division)}
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          color="error"
                          onClick={() => handleDeleteDivision(division.ID)}
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
          {dialog.type === 'add' ? 'Add New Division' : 'Edit Division'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Name"
              name="Name"
              value={dialog.data?.Name || ''}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Description"
              name="Description"
              value={dialog.data?.Description || ''}
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

export default Divisions; 