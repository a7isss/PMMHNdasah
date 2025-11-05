'use client';

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
} from '@mui/material';
import {
  Restore,
  DeleteForever,
  ArrowBack,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/lib/hooks';

interface DeletedTask {
  id: string;
  name: string;
  project_id: string;
  deleted_at: string;
  created_at: string;
}

export default function DeletedTasksPage() {
  const router = useRouter();
  const user = useAppSelector((state) => state.auth.user);
  const [deletedTasks, setDeletedTasks] = useState<DeletedTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTask, setSelectedTask] = useState<DeletedTask | null>(null);
  const [restoreDialogOpen, setRestoreDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  // Check if user is super admin
  if (user?.role !== 'super_admin') {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">
          Access denied. Super Admin privileges required.
        </Alert>
      </Container>
    );
  }

  // Mock data - replace with actual API call
  React.useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setDeletedTasks([
        {
          id: 'task-1',
          name: 'Design System Implementation',
          project_id: 'proj-1',
          deleted_at: '2025-11-05T10:30:00Z',
          created_at: '2025-10-15T09:00:00Z',
        },
        {
          id: 'task-2',
          name: 'Database Migration',
          project_id: 'proj-2',
          deleted_at: '2025-11-04T14:20:00Z',
          created_at: '2025-10-20T11:15:00Z',
        },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const handleRestore = async (task: DeletedTask) => {
    setSelectedTask(task);
    setRestoreDialogOpen(true);
  };

  const confirmRestore = async () => {
    if (!selectedTask) return;

    try {
      // TODO: Implement actual API call
      // await restoreTask(selectedTask.id);

      setSnackbar({
        open: true,
        message: `Task "${selectedTask.name}" has been restored successfully`,
        severity: 'success'
      });

      // Remove from local state
      setDeletedTasks(prev => prev.filter(t => t.id !== selectedTask.id));
      setRestoreDialogOpen(false);
      setSelectedTask(null);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to restore task. Please try again.',
        severity: 'error'
      });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Typography>Loading deleted tasks...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => router.push('/admin')}
          variant="outlined"
        >
          Back to Admin
        </Button>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Deleted Tasks
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage soft-deleted tasks and restore them if needed
          </Typography>
        </Box>
      </Box>

      {/* Stats Card */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Typography variant="h6">
                {deletedTasks.length} Deleted Task{deletedTasks.length !== 1 ? 's' : ''}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Tasks that have been soft-deleted and can be restored
              </Typography>
            </Box>
            <Chip
              label={`${deletedTasks.length} items`}
              color="warning"
              variant="outlined"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Tasks Table */}
      {deletedTasks.length === 0 ? (
        <Card>
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 6 }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No Deleted Tasks
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All tasks are currently active. Deleted tasks will appear here.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Task Name</strong></TableCell>
                  <TableCell><strong>Project ID</strong></TableCell>
                  <TableCell><strong>Created</strong></TableCell>
                  <TableCell><strong>Deleted</strong></TableCell>
                  <TableCell align="right"><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {deletedTasks.map((task) => (
                  <TableRow key={task.id} hover>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {task.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={task.project_id}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(task.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="error.main">
                        {formatDate(task.deleted_at)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<Restore />}
                        onClick={() => handleRestore(task)}
                        color="success"
                      >
                        Restore
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Card>
      )}

      {/* Restore Confirmation Dialog */}
      <Dialog open={restoreDialogOpen} onClose={() => setRestoreDialogOpen(false)}>
        <DialogTitle>Confirm Task Restoration</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to restore the task "{selectedTask?.name}"?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This will make the task visible again to all users who have access to its project.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRestoreDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={confirmRestore}
            variant="contained"
            color="success"
            startIcon={<Restore />}
          >
            Restore Task
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}
