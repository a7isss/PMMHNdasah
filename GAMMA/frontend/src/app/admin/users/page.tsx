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
  MenuItem,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Person,
  Business,
  CheckCircle,
  Cancel,
  ArrowBack,
  Block,
  Check,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/lib/hooks';
import {
  useGetUsersQuery,
  useCreateUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useDeactivateUserMutation,
  useActivateUserMutation,
  useGetTenantsQuery,
} from '@/lib/api/adminApi';

export default function UserManagement() {
  const router = useRouter();
  const user = useAppSelector((state) => state.auth.user);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTenant, setSelectedTenant] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [newUser, setNewUser] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone: '',
    job_title: '',
    role: 'member',
    whatsapp_number: '',
  });

  const { data: usersData, isLoading, error, refetch } = useGetUsersQuery({
    search: searchTerm || undefined,
    tenant_id: selectedTenant || undefined,
    role: selectedRole || undefined,
    is_active: selectedStatus ? selectedStatus === 'active' : undefined,
    limit: 100,
  });

  const { data: tenantsData } = useGetTenantsQuery({ limit: 100 });

  const [createUser, { isLoading: creating }] = useCreateUserMutation();
  const [updateUser, { isLoading: updating }] = useUpdateUserMutation();
  const [deleteUser, { isLoading: deleting }] = useDeleteUserMutation();
  const [deactivateUser] = useDeactivateUserMutation();
  const [activateUser] = useActivateUserMutation();

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

  const handleCreateUser = async () => {
    if (!selectedTenant) {
      alert('Please select a tenant');
      return;
    }

    try {
      await createUser({
        userData: newUser,
        tenantId: selectedTenant,
      }).unwrap();

      setCreateDialogOpen(false);
      setNewUser({
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        phone: '',
        job_title: '',
        role: 'member',
        whatsapp_number: '',
      });
      setSelectedTenant('');
      refetch();
    } catch (error) {
      console.error('Failed to create user:', error);
    }
  };

  const handleEditUser = (user: any) => {
    setSelectedUser(user);
    setEditDialogOpen(true);
  };

  const handleUpdateUser = async () => {
    if (!selectedUser) return;

    try {
      await updateUser({
        userId: selectedUser.id,
        data: {
          first_name: selectedUser.first_name,
          last_name: selectedUser.last_name,
          phone: selectedUser.phone,
          job_title: selectedUser.job_title,
          role: selectedUser.role,
          whatsapp_number: selectedUser.whatsapp_number,
          is_active: selectedUser.is_active,
        },
      }).unwrap();

      setEditDialogOpen(false);
      setSelectedUser(null);
      refetch();
    } catch (error) {
      console.error('Failed to update user:', error);
    }
  };

  const handleDeleteUser = (user: any) => {
    setSelectedUser(user);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!selectedUser) return;

    try {
      await deleteUser(selectedUser.id).unwrap();
      setDeleteDialogOpen(false);
      setSelectedUser(null);
      refetch();
    } catch (error) {
      console.error('Failed to delete user:', error);
    }
  };

  const handleToggleUserStatus = async (user: any) => {
    try {
      if (user.is_active) {
        await deactivateUser(user.id).unwrap();
      } else {
        await activateUser(user.id).unwrap();
      }
      refetch();
    } catch (error) {
      console.error('Failed to toggle user status:', error);
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Typography>Loading users...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Alert severity="error">
          Failed to load users. Please try again.
        </Alert>
      </Container>
    );
  }

  const users = usersData?.users || [];
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
          User Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage users across all tenants in the system
        </Typography>
      </Box>

      {/* Filters and Controls */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Users ({users.length})</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create User
          </Button>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
          <TextField
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 250 }}
          />

          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Tenant</InputLabel>
            <Select
              value={selectedTenant}
              onChange={(e) => setSelectedTenant(e.target.value)}
              label="Tenant"
            >
              <MenuItem value="">All Tenants</MenuItem>
              {tenants.map((tenant) => (
                <MenuItem key={tenant.id} value={tenant.id}>
                  {tenant.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Role</InputLabel>
            <Select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              label="Role"
            >
              <MenuItem value="">All Roles</MenuItem>
              <MenuItem value="super_admin">Super Admin</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
              <MenuItem value="manager">Manager</MenuItem>
              <MenuItem value="member">Member</MenuItem>
              <MenuItem value="viewer">Viewer</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              label="Status"
            >
              <MenuItem value="">All Status</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Paper>

      {/* Users Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>User</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Tenant</TableCell>
              <TableCell>Last Login</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Person sx={{ mr: 1, color: 'primary.main' }} />
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {user.first_name} {user.last_name}
                      </Typography>
                      {user.job_title && (
                        <Typography variant="caption" color="text.secondary">
                          {user.job_title}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{user.email}</Typography>
                  {user.whatsapp_verified && (
                    <Typography variant="caption" color="success.main">
                      WhatsApp verified
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={user.role}
                    size="small"
                    color={
                      user.role === 'super_admin' ? 'error' :
                      user.role === 'admin' ? 'warning' :
                      user.role === 'manager' ? 'info' :
                      user.role === 'member' ? 'primary' : 'default'
                    }
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    icon={user.is_active ? <CheckCircle /> : <Cancel />}
                    label={user.is_active ? 'Active' : 'Inactive'}
                    size="small"
                    color={user.is_active ? 'success' : 'error'}
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Business sx={{ mr: 0.5, fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="body2">{user.tenant.name}</Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {user.last_login_at
                      ? new Date(user.last_login_at).toLocaleDateString()
                      : 'Never'
                    }
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Tooltip title="Edit User">
                      <IconButton
                        size="small"
                        onClick={() => handleEditUser(user)}
                        color="primary"
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={user.is_active ? 'Deactivate User' : 'Activate User'}>
                      <IconButton
                        size="small"
                        onClick={() => handleToggleUserStatus(user)}
                        color={user.is_active ? 'warning' : 'success'}
                      >
                        {user.is_active ? <Block fontSize="small" /> : <Check fontSize="small" />}
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete User">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteUser(user)}
                        color="error"
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

      {/* Create User Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New User</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Tenant *</InputLabel>
              <Select
                value={selectedTenant}
                onChange={(e) => setSelectedTenant(e.target.value)}
                label="Tenant *"
              >
                {tenants.map((tenant) => (
                  <MenuItem key={tenant.id} value={tenant.id}>
                    {tenant.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="First Name"
                value={newUser.first_name}
                onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })}
                fullWidth
              />
              <TextField
                label="Last Name"
                value={newUser.last_name}
                onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })}
                fullWidth
              />
            </Box>

            <TextField
              label="Email"
              type="email"
              value={newUser.email}
              onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
              fullWidth
              required
            />

            <TextField
              label="Password"
              type="password"
              value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              fullWidth
              required
            />

            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Phone"
                value={newUser.phone}
                onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
                fullWidth
              />
              <TextField
                label="Job Title"
                value={newUser.job_title}
                onChange={(e) => setNewUser({ ...newUser, job_title: e.target.value })}
                fullWidth
              />
            </Box>

            <TextField
              select
              label="Role"
              value={newUser.role}
              onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
              fullWidth
              SelectProps={{ native: true }}
            >
              <option value="viewer">Viewer</option>
              <option value="member">Member</option>
              <option value="manager">Manager</option>
              <option value="admin">Admin</option>
              <option value="super_admin">Super Admin</option>
            </TextField>

            <TextField
              label="WhatsApp Number"
              value={newUser.whatsapp_number}
              onChange={(e) => setNewUser({ ...newUser, whatsapp_number: e.target.value })}
              fullWidth
              placeholder="+1234567890"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateUser}
            variant="contained"
            disabled={creating || !selectedTenant}
          >
            {creating ? 'Creating...' : 'Create User'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="First Name"
                value={selectedUser?.first_name || ''}
                onChange={(e) => setSelectedUser({ ...selectedUser, first_name: e.target.value })}
                fullWidth
              />
              <TextField
                label="Last Name"
                value={selectedUser?.last_name || ''}
                onChange={(e) => setSelectedUser({ ...selectedUser, last_name: e.target.value })}
                fullWidth
              />
            </Box>

            <TextField
              label="Phone"
              value={selectedUser?.phone || ''}
              onChange={(e) => setSelectedUser({ ...selectedUser, phone: e.target.value })}
              fullWidth
            />

            <TextField
              label="Job Title"
              value={selectedUser?.job_title || ''}
              onChange={(e) => setSelectedUser({ ...selectedUser, job_title: e.target.value })}
              fullWidth
            />

            <TextField
              select
              label="Role"
              value={selectedUser?.role || 'member'}
              onChange={(e) => setSelectedUser({ ...selectedUser, role: e.target.value })}
              fullWidth
              SelectProps={{ native: true }}
            >
              <option value="viewer">Viewer</option>
              <option value="member">Member</option>
              <option value="manager">Manager</option>
              <option value="admin">Admin</option>
              <option value="super_admin">Super Admin</option>
            </TextField>

            <TextField
              label="WhatsApp Number"
              value={selectedUser?.whatsapp_number || ''}
              onChange={(e) => setSelectedUser({ ...selectedUser, whatsapp_number: e.target.value })}
              fullWidth
              placeholder="+1234567890"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleUpdateUser}
            variant="contained"
            disabled={updating}
          >
            {updating ? 'Updating...' : 'Update User'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete User</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the user "{selectedUser?.first_name} {selectedUser?.last_name}"?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This action cannot be undone. The user account and all associated data will be permanently removed.
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            This will permanently delete the user. Consider deactivating instead if you might need to restore access later.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={deleting}
          >
            {deleting ? 'Deleting...' : 'Delete User'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
