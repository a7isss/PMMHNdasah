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
  ArrowBack,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/lib/hooks';

interface DeletedProject {
  id: string;
  name: string;
  tenant_id: string;
  deleted_at: string;
  created_at: string;
}

export default function DeletedProjectsPage() {
  const router = useRouter();
  const user = useAppSelector((state) => state.auth.user);
  const [deletedProjects, setDeletedProjects] = useState<DeletedProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProject, setSelectedProject] = useState<DeletedProject | null>(null);
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
      setDeletedProjects([
        {
          id: 'proj-1',
          name: 'Website Redesign Project',
          tenant_id: 'tenant-1',
          deleted_at: '2025-11-05T08:15:00Z',
          created_at: '2025-09-01T10:00:00Z',
        },
        {
          id: 'proj-2',
          name: 'Mobile App Development',
          tenant_id: 'tenant-2',
          deleted_at: '2025-11-03T16:45:00Z',
          created_at: '2025-08-15T14:30:00Z',
        },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const handleRestore = async (project: DeletedProject) => {
    setSelectedProject(project);
    setRestoreDialogOpen(true);
  };

  const confirmRestore = async () => {
    if (!selectedProject) return;

    try {
      // TODO: Implement actual API call
      // await restoreProject(selectedProject.id);

      setSnackbar({
        open: true,
        message: `Project "${selectedProject.name}" has been restored successfully`,
        severity: 'success'
      });

      // Remove from local state
      setDeletedProjects(prev => prev.filter(p => p.id !== selectedProject.id));
      setRestoreDialogOpen(false);
      setSelectedProject(null);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to restore project. Please try again.',
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
        <Typography>Loading deleted projects...</Typography>
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
            Deleted Projects
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage soft-deleted projects and restore them if needed
          </Typography>
        </Box>
      </Box>

      {/* Stats Card */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Typography variant="h6">
                {deletedProjects.length} Deleted Project{deletedProjects.length !== 1 ? 's' : ''}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Projects that have been soft-deleted and can be restored
              </Typography>
            </Box>
            <Chip
              label={`${deletedProjects.length} items`}
              color="warning"
              variant="outlined"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Projects Table */}
      {deletedProjects.length === 0 ? (
        <Card>
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 6 }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No Deleted Projects
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All projects are currently active. Deleted projects will appear here.
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
                  <TableCell><strong>Project Name</strong></TableCell>
                  <TableCell><strong>Tenant ID</strong></TableCell>
                  <TableCell><strong>Created</strong></TableCell>
                  <TableCell><strong>Deleted</strong></TableCell>
                  <TableCell align="right"><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {deletedProjects.map((project) => (
                  <TableRow key={project.id} hover>
                    <TableCell>
                      <Typography variant="body1" fontWeight="medium">
                        {project.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={project.tenant_id}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(project.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="error.main">
                        {formatDate(project.deleted_at)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<Restore />}
                        onClick={() => handleRestore(project)}
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
        <DialogTitle>Confirm Project Restoration</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to restore the project "{selectedProject?.name}"?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This will make the project and all its tasks visible again to all team members.
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
            Restore Project
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
