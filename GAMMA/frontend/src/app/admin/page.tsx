'use client';

import React from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  Alert,
} from '@mui/material';
import {
  Business,
  People,
  TrendingUp,
  Security,
  Add,
  ManageAccounts,
  BusinessCenter,
  Restore,
  DeleteSweep,
  BugReport,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/lib/hooks';
import { useGetAdminStatsQuery } from '@/lib/api/adminApi';

export default function AdminDashboard() {
  const router = useRouter();
  const user = useAppSelector((state) => state.auth.user);
  const { data: stats, isLoading, error } = useGetAdminStatsQuery();

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

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography>Loading admin dashboard...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">
          Failed to load admin statistics. Please try again.
        </Alert>
      </Container>
    );
  }

  const statCards = [
    {
      title: 'Total Tenants',
      value: stats?.tenants.total || 0,
      subtitle: `${stats?.tenants.active || 0} active, ${stats?.tenants.new_last_30_days || 0} new this month`,
      icon: <Business color="primary" sx={{ fontSize: 40 }} />,
      color: 'primary.main',
    },
    {
      title: 'Total Users',
      value: stats?.users.total || 0,
      subtitle: `${stats?.users.active || 0} active, ${stats?.users.new_last_30_days || 0} new this month`,
      icon: <People color="secondary" sx={{ fontSize: 40 }} />,
      color: 'secondary.main',
    },
    {
      title: 'System Health',
      value: stats?.system_health.database_status === 'healthy' ? 'Healthy' : 'Issues',
      subtitle: `Last updated: ${new Date(stats?.system_health.last_updated || '').toLocaleString()}`,
      icon: <Security color="success" sx={{ fontSize: 40 }} />,
      color: 'success.main',
    },
  ];

  const roleBreakdown = stats?.roles || {};

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Super Admin Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage tenants, users, and system-wide operations
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3, mb: 4 }}>
        {statCards.map((card, index) => (
          <Card key={index} sx={{ flex: 1, minHeight: 140 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                {card.icon}
                <Box sx={{ ml: 2 }}>
                  <Typography variant="h6" component="div">
                    {card.title}
                  </Typography>
                  <Typography variant="h4" component="div" sx={{ color: card.color }}>
                    {card.value}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2" color="text.secondary">
                {card.subtitle}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Role Distribution */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            User Role Distribution
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {Object.entries(roleBreakdown).map(([role, count]) => (
              <Chip
                key={role}
                label={`${role}: ${count}`}
                variant="outlined"
                color={role === 'super_admin' ? 'error' : role === 'admin' ? 'warning' : 'default'}
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2 }}>
            <Button
              variant="contained"
              fullWidth
              startIcon={<BusinessCenter />}
              onClick={() => router.push('/admin/tenants')}
              sx={{ height: 56, flex: 1 }}
            >
              Manage Tenants
            </Button>
            <Button
              variant="contained"
              fullWidth
              startIcon={<ManageAccounts />}
              onClick={() => router.push('/admin/users')}
              sx={{ height: 56, flex: 1 }}
            >
              Manage Users
            </Button>
            <Button
              variant="outlined"
              fullWidth
              startIcon={<Add />}
              onClick={() => router.push('/admin/tenants/create')}
              sx={{ height: 56, flex: 1 }}
            >
              Create Tenant
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Debug & Development Tools */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Debug & Development Tools
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            System diagnostics, API testing, and debugging utilities
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2 }}>
            <Button
              variant="outlined"
              fullWidth
              startIcon={<BugReport />}
              onClick={() => router.push('/admin/debug')}
              sx={{ height: 56, flex: 1 }}
              color="warning"
            >
              Debug Dashboard
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Data Recovery Section */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Data Recovery & Soft Deletes
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Manage soft-deleted records and restore accidentally deleted data
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2 }}>
            <Button
              variant="outlined"
              fullWidth
              startIcon={<DeleteSweep />}
              onClick={() => router.push('/admin/deleted/tasks')}
              sx={{ height: 56, flex: 1 }}
              color="warning"
            >
              View Deleted Tasks
            </Button>
            <Button
              variant="outlined"
              fullWidth
              startIcon={<DeleteSweep />}
              onClick={() => router.push('/admin/deleted/projects')}
              sx={{ height: 56, flex: 1 }}
              color="warning"
            >
              View Deleted Projects
            </Button>
            <Button
              variant="outlined"
              fullWidth
              startIcon={<DeleteSweep />}
              onClick={() => router.push('/admin/deleted/users')}
              sx={{ height: 56, flex: 1 }}
              color="warning"
            >
              View Deleted Users
            </Button>
            <Button
              variant="contained"
              fullWidth
              startIcon={<Restore />}
              onClick={() => router.push('/admin/restore')}
              sx={{ height: 56, flex: 1 }}
              color="success"
            >
              Bulk Restore
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Recent Activity Placeholder */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activity
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Activity logging will be implemented in the next phase.
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
}
