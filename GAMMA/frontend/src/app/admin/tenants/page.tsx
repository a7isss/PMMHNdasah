'use client';

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Paper,
  InputAdornment,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Business,
  People,
  CheckCircle,
  Cancel,
  ArrowBack,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/lib/hooks';
import {
  useGetTenantsQuery,
  useUpdateTenantMutation,
  useDeleteTenantMutation,
} from '@/lib/api/adminApi';
// Using simple table instead of DataGrid for now

export default function TenantManagement() {
  const router = useRouter();
  const user = useAppSelector((state) => state.auth.user);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTenant, setSelectedTenant] = useState<any>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const { data: tenantsData, isLoading, error, refetch } = useGetTenantsQuery({
    search: searchTerm || undefined,
    limit: 100,
  });

  const [updateTenant, { isLoading: updating }] = useUpdateTenantMutation();
  const [deleteTenant, { isLoading: deleting }] = useDeleteTenantMutation();

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

  const handleEditTenant = (tenant: any) => {
    setSelectedTenant(tenant);
    setEditDialogOpen(true);
  };

  const handleDeleteTenant = (tenant: any) => {
    setSelectedTenant(tenant);
    setDeleteDialogOpen(true);
  };

  const handleUpdateTenant = async () => {
    if (!selectedTenant) return;

    try {
      await updateTenant({
        tenantId: selectedTenant.id,
        data: {
          name: selectedTenant.name,
          domain: selectedTenant.domain,
          subscription_plan: selectedTenant.subscription_plan,
          is_active: selectedTenant.is_active,
          contact_email: selectedTenant.contact_email,
          contact_phone: selectedTenant.contact_phone,
        },
      }).unwrap();

      setEditDialogOpen(false);
      setSelectedTenant(null);
      refetch();
    } catch (error) {
      console.error('Failed to update tenant:', error);
    }
  };

  const handleConfirmDelete = async () => {
    if (!selectedTenant) return;

    try {
      await deleteTenant(selectedTenant.id).unwrap();
      setDeleteDialogOpen(false);
      setSelectedTenant(null);
      refetch();
    } catch (error) {
      console.error('Failed to delete tenant:', error);
    }
  };



  if (isLoading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Typography>Loading tenants...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Alert severity="error">
          Failed to load tenants. Please try again.
        </Alert>
      </Container>
    );
  }

  const tenants = tenantsData?.tenants || [];

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => router.push('/admin')}
            sx={{ mr: 2 }}
          >
            Back to Dashboard
          </Button>
        </Box>
        <Typography variant="h4" component="h1" gutterBottom>
          Tenant Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage companies and organizations in the system
        </Typography>
      </Box>

      {/* Controls */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Tenants ({tenants.length})</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => router.push('/admin/tenants/create')}
          >
            Create Tenant
          </Button>
        </Box>

        <TextField
          fullWidth
          placeholder="Search tenants by name or domain..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
          sx={{ maxWidth: 400 }}
        />
      </Paper>

      {/* Data Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Tenant Name</TableCell>
              <TableCell>Domain</TableCell>
              <TableCell>Plan</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Users</TableCell>
              <TableCell>Contact Email</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tenants.map((tenant) => (
              <TableRow key={tenant.id}>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Business sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="body2" fontWeight="medium">
                      {tenant.name}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {tenant.domain || 'No domain'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={tenant.subscription_plan}
                    size="small"
                    color={
                      tenant.subscription_plan === 'enterprise' ? 'primary' :
                      tenant.subscription_plan === 'professional' ? 'secondary' :
                      tenant.subscription_plan === 'starter' ? 'warning' : 'default'
                    }
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    icon={tenant.is_active ? <CheckCircle /> : <Cancel />}
                    label={tenant.is_active ? 'Active' : 'Inactive'}
                    size="small"
                    color={tenant.is_active ? 'success' : 'error'}
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <People sx={{ mr: 0.5, fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="body2">{tenant.user_count}</Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {tenant.contact_email || 'Not set'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {new Date(tenant.created_at).toLocaleDateString()}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box>
                    <Tooltip title="Edit Tenant">
                      <IconButton
                        size="small"
                        onClick={() => handleEditTenant(tenant)}
                        color="primary"
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Tenant">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteTenant(tenant)}
                        color="error"
                        disabled={tenant.user_count > 0}
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Edit Tenant Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Tenant</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Tenant Name"
              value={selectedTenant?.name || ''}
              onChange={(e) => setSelectedTenant({ ...selectedTenant, name: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Domain"
              value={selectedTenant?.domain || ''}
              onChange={(e) => setSelectedTenant({ ...selectedTenant, domain: e.target.value })}
              fullWidth
              placeholder="custom-domain.com"
            />
            <TextField
              label="Contact Email"
              type="email"
              value={selectedTenant?.contact_email || ''}
              onChange={(e) => setSelectedTenant({ ...selectedTenant, contact_email: e.target.value })}
              fullWidth
            />
            <TextField
              label="Contact Phone"
              value={selectedTenant?.contact_phone || ''}
              onChange={(e) => setSelectedTenant({ ...selectedTenant, contact_phone: e.target.value })}
              fullWidth
            />
            <TextField
              select
              label="Subscription Plan"
              value={selectedTenant?.subscription_plan || 'starter'}
              onChange={(e) => setSelectedTenant({ ...selectedTenant, subscription_plan: e.target.value })}
              fullWidth
              SelectProps={{ native: true }}
            >
              <option value="free">Free</option>
              <option value="starter">Starter</option>
              <option value="professional">Professional</option>
              <option value="enterprise">Enterprise</option>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleUpdateTenant}
            variant="contained"
            disabled={updating}
          >
            {updating ? 'Updating...' : 'Update Tenant'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Tenant</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the tenant "{selectedTenant?.name}"?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This action cannot be undone. The tenant and all associated data will be permanently removed.
          </Typography>
          {selectedTenant?.user_count > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              This tenant has {selectedTenant.user_count} users. You must remove all users before deleting the tenant.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={deleting || selectedTenant?.user_count > 0}
          >
            {deleting ? 'Deleting...' : 'Delete Tenant'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
