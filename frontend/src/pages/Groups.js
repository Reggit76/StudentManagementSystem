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
import { groupsAPI, divisionsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Groups = () => {
  const { hasPermission } = useAuth();
  const [groups, setGroups] = useState([]);
  const [divisions, setDivisions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState({ open: false, type: null, data: null });

  useEffect(() => {
    fetchGroups();
    fetchDivisions();
  }, []);

  const fetchGroups = async () => {
    setLoading(true);
    try {
      const response = await groupsAPI.getAll();
      setGroups(response.data);
    } catch (err) {
      setError('Failed to load groups');
    } finally {
      setLoading(false);
    }
  };

  const fetchDivisions = async () => {
    try {
      const response = await divisionsAPI.getAll();
      setDivisions(response.data);
    } catch (err) {
      setError('Failed to load divisions');
    }
  };

  const handleAddGroup = () => {
    setDialog({
      open: true,
      type: 'add',
      data: { Name: '', DivisionID: '', Year: new Date().getFullYear() },
    });
  };

  const handleEditGroup = (group) => {
    setDialog({
      open: true,
      type: 'edit',
      data: group,
    });
  };

  const handleDeleteGroup = async (id) => {
    if (window.confirm('Are you sure you want to delete this group?')) {
      try {
        await groupsAPI.delete(id);
        fetchGroups();
      } catch (err) {
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
        await groupsAPI.update(dialog.data.ID, dialog.data);
      }
      handleDialogClose();
      fetchGroups();
    } catch (err) {
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
              <TableCell>Division</TableCell>
              <TableCell>Year</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : groups.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  No groups found
                </TableCell>
              </TableRow>
            ) : (
              groups.map((group) => (
                <TableRow key={group.ID}>
                  <TableCell>{group.Name}</TableCell>
                  <TableCell>
                    {divisions.find(d => d.ID === group.DivisionID)?.Name || '-'}
                  </TableCell>
                  <TableCell>{group.Year}</TableCell>
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
                          onClick={() => handleDeleteGroup(group.ID)}
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
              name="Name"
              value={dialog.data?.Name || ''}
              onChange={handleInputChange}
              required
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Division</InputLabel>
              <Select
                name="DivisionID"
                value={dialog.data?.DivisionID || ''}
                onChange={handleInputChange}
                label="Division"
                required
              >
                {divisions.map((division) => (
                  <MenuItem key={division.ID} value={division.ID}>
                    {division.Name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Year"
              name="Year"
              type="number"
              value={dialog.data?.Year || new Date().getFullYear()}
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